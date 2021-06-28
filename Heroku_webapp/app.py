from flask import Flask, request, render_template, session
import pandas as pd
from datetime import datetime
from rq import Queue
from rq.job import Job
from worker import conn
from rq import get_current_job
import dict_
import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from display import save_frequency_plot, save_time_plot, create_wordcloud

from itertools import cycle
import time
from time import sleep
import os
from flask_sqlalchemy import SQLAlchemy
from waitress import serve


q = Queue('low', is_async=True, connection=conn)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///result.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Result(db.Model):
    #__tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    query_ = db.Column(db.String, nullable=False)
    df_name = db.Column(db.String, nullable=False)
    from_ = db.Column(db.String(200), nullable=False)
    to = db.Column(db.String(200), nullable=False)
    cc = db.Column(db.String(200), nullable=False)
    bcc = db.Column(db.String(200), nullable=False)    
    sent_date = db.Column(db.DateTime, default=datetime.utcnow)
    subject = db.Column(db.String(500), nullable=False)
    body_content = db.Column(db.String(4000), nullable=False)

    def __repr__(self):
        return '<Query %r>' % self.id

#******************************** Support functions ********************************************#
import numpy as np
import pandas as pd
from collections import defaultdict

import spacy
from spacy.matcher import PhraseMatcher
import en_core_web_sm


meta_content_df = pd.read_pickle('models/lay_skilling.pkl')

spacy.load('en_core_web_sm')
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
nlp = spacy.blank('en')
matcher = PhraseMatcher(nlp.vocab, attr='LOWER')

#****************************************************************************#
def _return_df(df_list):
    #meta_content_df = pd.read_pickle('models/lay_skilling.pkl')
    news_df = pd.read_pickle('models/NewsLetters.pkl')
    df = pd.DataFrame()
    
    if 'all' in df_list:

        df = meta_content_df.copy()
        
        #return df
    else:
        
        for name in df_list:
            # handle the error of custodian name not in the list    
            print(name)    
            if name == 'News-Letters':
                df = df.append(news_df)
            elif name == 'lay-k':
                temp = meta_content_df[~meta_content_df['public_id'].isin (news_df['public_id'])]        
                df = df.append(temp)

        df = df.drop_duplicates(subset =['public_id','subject','body_content'],ignore_index=True)
        df = df.reset_index(drop=True)
        print(len(df))
    
    return df
#****************************************************************************#
def _add_combined_text(row):
    subject = row.subject if row.subject != 'No Subject' else ''
    attach_content = row.attach_content if row.attach_content != 'No Attachment' else ''

    text =  subject+' '+row.body_content
    text = text[:8000] if len(text)>8000 else text
    attachment = attach_content[:8000] if len(attach_content)>8000 else attach_content
    text = text+' '+attachment
    text = text.lower()
    #text = nlp(text)
    return text


#****************************************************************************#
# The following filter limits the user query upto three phrases and matches them in the text.
#The following function is especially useful when there are more phrases in the query
# Users are recommended to query with less number of phrases and use those important phrase at the start of the query

def tokenize_filter(text, search_method):
    text = 'xxx' if text=='' else str(text)
    if len(text.split()) >2:        
        text = [token for token in text.rstrip().lower().split() if token not in spacy_stopwords ]    
    
    elif search_method=='full':
        text = [text.lower()]
    else:
        text = text.split()
    return text

#****************************************************************************#
# The following function is to convert date from string format to datetime frmat

def _get_date(x)   :
    default_date = 'Tue, 1 Jan 2222 00:00:00 -0000'
    try:
        result = pd.to_datetime(x).date()
        
    except :
        result = pd.to_datetime(default_date).date()
        
    return result




#****************************************************************************#
# Following function is to phrase match 
# returns dictionary of queries and corresponding emails
def get_emails_set(df, query, search_method):
    
    phrases_to_search = tokenize_filter(query,  search_method)
    
    # Create a list of tokens for each item in each query
    query_tokens_list = [nlp(item.lower()) for item in phrases_to_search]    
    
    matcher.add("Queries", None, *query_tokens_list )        
    
    emails_dict = defaultdict(set)

    half_rows = len(df)//2
    
    job = get_current_job()
    df_list = [df[:half_rows], df[(half_rows+1):]]
    for d in df_list:

        for _, row in d.iterrows():
            
            doc = nlp(row.combined_text)        
            matches = matcher(doc)

            # Create a set of the items found in the text
            found_items = set([doc[match[1]:match[2]] for match in matches])

            # Transform the item strings to lowercase to make it case insensitive
            for item in found_items:
                emails_dict[str(item)].add(row.public_id)  

        job.meta['progress'] = 'halfway_through'
        job.save_meta()
    return emails_dict

   
#****************************************************************************#

def _get_model1_resultset(query, search_list, from_date, to_date, numResults):
    #phrases ==>  search query list
    #search_list ==> list of custodians
    #from_date ==> from date to search
    # to_date ==> to date to search
    #numResults ==> cap on the results list

    df_name = ''
    for name in search_list:
        df_name = df_name+'_'+name

     
    df = _return_df(search_list)        

    job = get_current_job()

    if(len(df) == 0): # suppose there are no records
        #return df,df
        #return df
        return 'job_done'
        
    df['combined_text'] = df.apply(lambda row: _add_combined_text(row), axis=1)    
    

    job.meta['progress'] = 'before_search'
    job.save_meta()
    
    from_date = _get_date(from_date)
    to_date = _get_date(to_date)

    emails_dict = get_emails_set(df,query,'full') # sending for searching across
    if len(emails_dict.keys()) == 0 and len(query.split())>1: #search doesnt return any result
        emails_dict = get_emails_set(df,query,'split')

    job.meta['progress'] = 'after_search'
    job.save_meta()
    
    

    new_df = pd.DataFrame([(key,pubid) for key,val in emails_dict.items() for pubid in list(val) ], columns = ('Query','public_id'))
    new_df =  new_df.reset_index(drop=True)
    new_df = new_df.merge(meta_content_df, on='public_id')       
    
    new_df = new_df.drop_duplicates(subset=['to','from_','subject','body_content','date'],ignore_index=True)
    new_df = new_df[(new_df['date']>= from_date ) & (new_df['date']<=to_date)]
    
    df = new_df
    num_queries = len(emails_dict.keys())
    if num_queries!=0:
        new_df = new_df.groupby('Query').head(int(numResults)//num_queries).reset_index(drop=True) # top numResults    
   
    new_df = new_df.sort_values(  by=['date'], ignore_index=True  )
    new_df['combined_text'] = new_df.apply(lambda row: _add_combined_text(row), axis=1)
    #return new_df,df
    
    job.meta['progress'] = 'Finished'
    job.save_meta()
    
    
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        db.session.execute(table.delete())
    db.session.commit()
    

    query_join = '_'.join(query.lower().split())
    #print('from _get_model', query_join, df_name)
    for idx, row in new_df.iterrows():
        new_row = Result(id =idx, query_=query_join, df_name=df_name, from_ = row['from_'], to=row['to'], cc = row['cc'], bcc = row['bcc'],
        sent_date=row['date'], subject = row['subject'],body_content = row['body_content'])

        try:
            print('adding data', query_join, df_name)
            db.session.add(new_row)
            db.session.commit()

        except Exception as e:
            print('There was an issue adding your data', e )

    job.meta['progress'] = 'Finished'
    job.save_meta()    
    
    #***************plot frequency and wordcloud **********
    save_time_plot(new_df, df_name,query_join,str(from_date),str(to_date) ) 
    create_wordcloud(new_df['combined_text'], df_name,query_join,str(from_date),str(to_date))

    #return new_df
    return 'Finished'
#****************************************************************************#
def _get_model2_resultset(query, search_list, from_date, to_date):
    
    df_name = ''
    for name in search_list:
        df_name = df_name+'_'+name
    
    query_dict = {
        'risk reputation of all employees':'risk_reputation',
        'risk departmental':'risk_departmental',
        'political risks': 'risk_political',
        'Bankruptcy mails':'Bankruptcy',
        'Election BUSH':'Election_BUSH',
        'Strategic decisions':'Strategic_decisions',
        'Joint Energy Development Investment Limited': 'JEDI' ,
        'reorganization plans': 'reorganization_plans',
        'Chewco Investments L. P.': 'CHEWCO',
        'Profits scenarios':'profits'
    
    }
    if query not in query_dict.keys():
        query = 'Election BUSH'

    file_name = query_dict[query]
    df = pd.read_pickle('models/model2_'+file_name+'.pkl')
    from_date = _get_date(from_date)
    to_date = _get_date(to_date)
    

    df = df[(df['date']>= from_date ) & (df['date']<=to_date)]
    df = df.sort_values(  by=['date'], ignore_index=True  )
    df['combined_text'] = df.apply(lambda row: _add_combined_text(row), axis=1)

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        db.session.execute(table.delete())
    db.session.commit()

    query_join = '_'.join(query.lower().split())
    #print('from _get_model', query_join, df_name)
    for idx, row in df.iterrows():
        new_row = Result(id =idx, query_=query_join, df_name=df_name, from_ = row['from_'], to=row['to'], cc = row['cc'], bcc = row['bcc'],
        sent_date=row['date'], subject = row['subject'],body_content = row['body_content'])

        try:
            print('adding data', query_join, df_name)
            db.session.add(new_row)
            db.session.commit()

        except Exception as e:
            print('There was an issue adding your data', e )
    

    #***************plot frequency and wordcloud **********
    save_time_plot(df, df_name,query_join,str(from_date),str(to_date) ) 
    create_wordcloud(df['combined_text'], df_name,query_join,str(from_date),str(to_date))

    return 'finished'




#****************************************************************************#
@app.route('/', methods=['POST','GET'])
def index():
    
    from app import _get_model1_resultset    
    from app import _get_model2_resultset
    
    query1 =''
    from_date = datetime.now().date()
    to_date = datetime.now().date()
    job_meta= 'about to start'


    if request.method == 'POST':
        choice11 = request.form.getlist('choice11') 
        if len(choice11) ==0:
            choice11 = ['all']   

        df_name = ''
        for name in choice11:
            df_name = df_name+'_'+name
        
        
        dict_.session['df'] = df_name
        query1 = request.form['query']    
        query_join = '_'.join(query1.lower().split())
     
        dict_.session['query1'] = query1

        from_date = request.form['from_date']
        dict_.session['from_date'] = from_date
        to_date = request.form['to_date']
        dict_.session['to_date'] = to_date
        search = request.form['search']
        dict_.session['search'] = search

        print(from_date,to_date)

        if search == 'Simple Search':
            
            job_meta = 'started'
            
            if (len(choice11)>0) and (query1 != ''):            
            
                res = q.enqueue_call(_get_model1_resultset, args = (query1,choice11,from_date, to_date, 25),  timeout=50000, result_ttl=5000)            
                
                res_key = res.key.decode("utf-8")
                res_key = res_key.replace("rq:job:","")
                dict_.session['res_key'] = res_key
                job = Job.fetch(res_key, connection=conn)    
                job.meta['progress']  = 'job started'

            


        else:
            print ('ADVANCED SEARCH')
            _get_model2_resultset(query1,choice11,from_date,to_date)
            job_meta = 'started'

    return render_template('index.html', job_meta= job_meta, query1=query1, from_date=from_date, to_date = to_date)


@app.route('/Results',  methods=['POST','GET'])           
def Results():

    query1 = dict_.session['query1']   
    query_join = '_'.join(query1.lower().split())

    df_name = dict_.session['df']
    from_date = dict_.session['from_date']
    to_date = dict_.session['to_date']
    search = dict_.session['search']

    if request.method == 'POST':  

        if search == 'Simple Search':
            results = Result.query.all() 
            print('from app /results', query_join, df_name)
            #results = Result.query.filter(Result.query_ == query_join and Result.df_name == df_name).all()
            print(len(results), query_join, df_name)

            if len(results) == 0:
                res_key = dict_.session['res_key']    
                print(res_key)
                job = Job.fetch(res_key, connection=conn)
                job_meta = 'progressing'
                return render_template('index.html', job_meta = job_meta , query1=query1, from_date=from_date, to_date = to_date)
            else:
                
                return render_template('index.html', job_meta = 'finished', query1=query1, results = results, from_date=from_date, to_date = to_date)

        elif search == 'Advanced Search':

            results =  Result.query.all() 
            job_meta = 'finished'
            return render_template('index.html', job_meta = job_meta, query1=query1, results = results, from_date=from_date, to_date = to_date)

    return render_template('index.html', job_meta = 'not finished', query1=query1, from_date=from_date, to_date = to_date)


@app.route('/default_page' )
def default():    
    return render_template('assisted_search_terms_default.html')

@app.route('/Enron')
def Enron():
    return render_template('assisted_search_terms_enron.html')


@app.route('/TimePlot', methods=['POST','GET'])
def frequency_plot():

    print('plot the time plot')
    query1 = dict_.session['query1']
    query_join = '_'.join(query1.lower().split())

    search = dict_.session['search']
    df_name = dict_.session['df']
    from_date = dict_.session['from_date']
    to_date = dict_.session['to_date']

    if request.method in ['POST','GET']:
        
        #plot = 'lib/time_plot_'+query_join+df_name+'.pdf' # not using pdf
        plot1 = 'lib/time_plot_'+query_join+df_name+'from_'+from_date+'_to_'+to_date+'.png'
        plot2 = 'lib/wc_'+query_join+df_name+'from_'+from_date+'_to_'+to_date+'.png'
    

    else:
        #plot = 'lib/default.pdf'
        plot1 = 'css/rose.png'
        plot2 = 'css/rose.png'
    
    return render_template('index.html', plot1 = plot1, plot2=plot2)




if __name__ == '__main__':
    
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table from main  %s' % table)
        db.session.execute(table.delete())
    db.session.commit()
    
    db.create_all()
    
    port = 5000

    #app.run(debug=True)

    # serve your flask app with waitress, instead of running it directly.
    serve(app, host='0.0.0.0', port=port) # <---- ADD THIS

