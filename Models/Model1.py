import numpy as np
import pandas as pd
from collections import defaultdict
import os, errno
import time
import email.utils
from email.parser import Parser

import re
import string
import spacy
from spacy.matcher import PhraseMatcher
spacy.load('en_core_web_sm')
import en_core_web_sm
print('spacy is installed')

dataPath = input('Enter data folder path: ') # enter folder path where you have stored Enron_full.pkl
meta_content_df = pd.read_pickle(dataPath+'Enron_full.pkl')
skilling_df = meta_content_df[meta_content_df['custodian'] =='skilling-j'].copy()
lay_df = meta_content_df[meta_content_df['custodian'] =='lay-k'].copy()
lay_skilling = meta_content_df[meta_content_df['custodian'].isin(['lay-k','skilling-j'])]

#print('All: ', len(meta_content_df))
#print('skilling: ',len(skilling_df))
#print('lay: ',len(lay_df))
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
nlp = spacy.blank('en')
matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
#===============================================================
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

#ensure_dir(dataPath+'Results') # output path is created
ensure_dir(dataPath+'Results/Model1')
outPath = dataPath+'Results/Model1/'
#===============================================================


# get phrases to search
phrases = input('Input phrases to search separated by commas. Please enter atleast one phrase- ')
phrases_to_search = phrases.split(',')

#get dataset to search
print('Select a dataset')
dataset = input('Select 1 for the mailbox of Lay.K,\n 2 for the mailbox of Skilling.J \n 3 for Lay+skilling and \n 4 for all mailboxes \n')

while (True):

    if (dataset == '1'):
        df = lay_df   
        print('searching in Lay.K\'s mail box. # of mails:', len(df))             
        break
    elif (dataset == '2'):
        df = skilling_df
        print('searching in Skilling.J\'s mail box. # of mails:', len(df))        
        break
    elif (dataset == '3'):
        df = lay_skilling
        print('searching in Lay.K and Skilling.J\'s mail boxes. # of mails:', len(df))        
        break
    else:
        dataset =input('CAUTION: You chose to search all mailboxes. It takes a very long time to process. Do you want to proceed? if yes, type 4 again. Else type 1/2/3 - ')
        if dataset == '4':
            df = meta_content_df
            print('searching in entire Enron\'s dataset. # of mails:', len(df))            
            break


regex = re.compile(r'(FW:|RE:|Re:|re:|fw:|Fw:)') # for subject lines
df['subject'] = df['subject'].apply(lambda x: regex.sub('', x).strip())

'''
#unit test
test1 = 'FW: re: I will come there'
test1 = regex.sub('', test1).strip()
print(test1)
'''

#Following function is to combine subject, body_content and attachments.
# There are no attachments in the ENron dataset
# the length of the text is restricted to 8000

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

# add a new column to df
df['combined_text'] = df.apply(lambda row: _add_combined_text(row), axis=1) 

#There are inserted dates in the dataset. So let us convert them to default date
def _get_date(x)   :
    default_date = 'Tue, 1 Jan 2222 00:00:00 -0000'
    try:    
        
        result = email.utils.parsedate_to_datetime(x).ctime()
        
    except :
        
        result = email.utils.parsedate_to_datetime(default_date).ctime()
        
    return result
#test case
#x = _get_date('Thu, 21 Feb 2002 13:48:35 -0800')
#print(x, type(x))

#standardize all sent_date 
meta_content_df['sent_date'] = meta_content_df['sent_date'].apply(lambda x: _get_date(x))
df['sent_date'] = df['sent_date'].apply(lambda x: _get_date(x))

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


# Following function is to phrase match 
# returns dictionary of queries and corresponding emails
def get_emails_set(df, query, search_method):
    
    phrases_to_search = tokenize_filter(query,  search_method)
    
    # Create a list of tokens for each item in each query
    query_tokens_list = [nlp(item.lower()) for item in phrases_to_search]    
    matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    matcher.add("Queries", None, *query_tokens_list )        
    
    emails_dict = defaultdict(set)
    
    for _, row in df.iterrows():
        
        doc = nlp(row.combined_text)        
        matches = matcher(doc)

        # Create a set of the items found in the text
        found_items = set([doc[match[1]:match[2]] for match in matches])

        # Transform the item strings to lowercase to make it case insensitive
        for item in found_items:
            emails_dict[str(item)].add(row.public_id)  

    return emails_dict


def _get_model1_resultset(df, query, numResults):
    #phrases ==>  search query list
    #search_list ==> list of custodians
    #numResults ==> cap on the results list
     
    #df = _return_df(search_list)        
    
    if(len(df) == 0): # suppose there are no records
        return df,df
        #return df
        
    emails_dict = get_emails_set(df,query,'full')
    if len(emails_dict.keys()) == 0 and len(query.split())>1: # if search doesnt return any result
        emails_dict = get_emails_set(df,query,'split')

    new_df = pd.DataFrame([(key,pubid) for key,val in emails_dict.items() for pubid in list(val) ], columns = ('Query','public_id'))
    
    new_df = new_df.merge(df, on='public_id') # now it contains complete list of relevant mails 
    new_df = new_df.drop_duplicates(subset=['sent_date','subject','body_content','attach_content'],ignore_index=True)    
    df = new_df # full list of results
    # the following gets list of mails that have most number of emails in the thread
    num_queries = len(emails_dict.keys())
    
    try:
        temp_df = new_df.groupby('subject').count().reset_index(drop= False).sort_values('public_id', ascending=False).head(int(numResults)//num_queries)#
        subject_list = list(temp_df.subject)
        #print(len(subject_list))
    
    
        pub_id_list = new_df[new_df['subject'].isin(subject_list)].public_id

        final_df = meta_content_df[meta_content_df['public_id'].isin(pub_id_list)].copy()
        final_df = final_df.merge(new_df[['public_id','Query']], on='public_id')
        cols = final_df.columns.tolist()
        cols = cols = cols[-1:] + cols[:-1] # rearrange query to be the first column
        final_df = final_df[cols]
        final_df = final_df.sort_values(['subject'], ascending=True).sort_values(['sent_date'], ascending=True).reset_index(drop=True)
        final_df.iloc[:,:-1].to_csv(outPath+query+'.csv')
    
        #print('len of final_df after', len(new_df), len(final_df), len(subject_list), len(pub_id_list), final_df.columns, new_df.columns, query)
        '''
        ##############
        df = final_df
        num_queries = len(emails_dict.keys())
        if num_queries!=0:
            final_df = final_df.groupby('Query').head(int(numResults)//num_queries).reset_index(drop=True) # top numResults
            #final_df = final_df.groupby('subject').head(int(numResults)//num_queries).reset_index(drop=True)

        ###################
        '''
        #return new_df  
        return final_df.iloc[:,:-1], df.iloc[:,:-1] 
    except:
        return df, df
'''
#unit test
query = 'organization restructure'
final_df,temp_df = _get_model1_resultset(df, query, 25)
final_df.to_csv(outPath+query+'.csv') 
'''

for query in phrases_to_search :
           
    final_df,temp_df = _get_model1_resultset(df, query, 25)  
    print('Query results are stored in the file - '+outPath+query+'.csv')