#Make sure that tensorflow is 1.15.0 

import numpy as np
import pandas as pd
import os
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf # Necessary to run BERT models (go through the readme file)


#Read data
dataPath = input('Enter data folder path: ') # enter folder path where you have stored Enron_full.pkl
meta_content_df = pd.read_pickle(dataPath+'Enron_full.pkl')
skilling_df = meta_content_df[meta_content_df['custodian'] =='skilling-j'].copy()
lay_df = meta_content_df[meta_content_df['custodian'] =='lay-k'].copy()
lay_skilling = meta_content_df[meta_content_df['custodian'].isin(['lay-k','skilling-j'])]
#===========================================================================
# get phrases to search
phrases = input('Input phrases to search separated by commas. Please enter atleast one phrase- ')
phrases_to_search = phrases.split(',')

#===========================================================================
#get dataset to search
print('Select a dataset')
dataset = input('Select 1 for the mailbox of Lay.K,\n 2 for the mailbox of Skilling.J \n 3 for Lay+skilling and \n 4 for all mailboxes \n')
embedding_name = ''
while (True):

    if (dataset == '1'):
        df = lay_df   
        embedding_name = 'lay'
        print('searching in Lay.K\'s mail box. # of mails:', len(df))             
        break
    elif (dataset == '2'):
        df = skilling_df
        embedding_name ='skilling'
        print('searching in Skilling.J\'s mail box. # of mails:', len(df))        
        break
    elif (dataset == '3'):
        df = lay_skilling
        embedding_name = 'lay_skilling'
        print('searching in Lay.K and Skilling.J\'s mail boxes. # of mails:', len(df))        
        break
    else:
        dataset =input('CAUTION: You chose to search all mailboxes. It takes a very long time to process. Do you want to proceed? if yes, type 4 again. Else type 1/2/3 - ')
        if dataset == '4':
            df = meta_content_df
            embedding_name = 'all_emps'
            print('searching in entire Enron\'s dataset. # of mails:', len(df))            
            break


#===========================================================================
#create the output folder
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

#ensure_dir(dataPath+'Results') # output path is created
ensure_dir(dataPath+'Results/Model2')

outPath = dataPath+'Results/Model2/'
#===========================================================================
#tokenization can be done using bert tokenisation in the later versions of BERT
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
def tokenize_filter(text):
    text = 'xxx' if text=='' else str(text)
    text = ' '.join(token for token in text.rstrip().lower().split() if token not in spacy_stopwords)
    return text
#Unit test
#print(tokenize_filter('All updates from all employees'))
#===========================================================================

#BERT Training and Document Extraction
# You need start the BERT server separately (go through the readme file)

from bert_serving.client import BertClient
bc = BertClient(check_length=False)

#The following procedure encodes the entire text and converts each to a 768 long vectors
# This takes a while to compute. So compute it once on the data and save it as a .pkl and reuse
def create_bert_embeddings(bert_df, embedding_name):
    bc = BertClient(check_length=False)
    bert_df =bert_df.reset_index(drop=True)
    bert_df['vector'] =""
    for index, row in bert_df.iterrows():
        
        subject = row['subject'] if row['subject'] != '' else ' '
        content = row['body_content'] if   row['body_content'] != '' else ' '  
        attach = row['attach_content'] if row['attach_content'] != '' else ' '

        text = str(subject)+' '+str(content) +' '+str(attach)
        text = text[:8000]
        text = tokenize_filter(text)
        
        search_phrase_vector =  bc.encode([text])[0]
        #print(search_phrase_vector)
        bert_df.at[index,'vector'] =search_phrase_vector
    bert_df['vector'] = bert_df['vector'].apply(lambda x: x.tolist() )
    bert_df.to_pickle(dataPath+'bert_embeddings_'+embedding_name+'.pkl') 


#  Check whether BERT embeddings are available for the given dataset. If not, create
if (os.path.exists(dataPath+'bert_embeddings_'+embedding_name+'.pkl')):
    bert_df = pd.read_pickle(dataPath+'bert_embeddings_'+embedding_name+'.pkl')
else:
    create_bert_embeddings(df)
    bert_df = pd.read_pickle(dataPath+'bert_embeddings_'+embedding_name+'.pkl')

all_vec = bert_df.vector.tolist() # make it iterable

for query in phrases_to_search:
    
    query_encode = bc.encode([query])[0] # encode query also    
    query_encode = np.array(query_encode) # convert to np.array
    all_vec = np.array(all_vec)
    
    query_encode = query_encode.reshape(-1,768)
    
    value = cosine_similarity(all_vec, query_encode) # check the cosine similarity
    
    doc_list=[]
    
    for i in range( len(bert_df)):               
        doc_list.append([bert_df.public_id[i], value[i][0]])
    
    p = pd.DataFrame(doc_list)
    p.columns = ['public_id','score'] #['email_number','score']
    p['query'] = query
    
    zz = p.merge(bert_df.loc[:, bert_df.columns != 'vector'], on='public_id') # temporary dataframe
    
    
    #print(zz.score[0])
    zz = zz.drop_duplicates(keep='first',inplace = False)  
    dy = zz.sort_values(by=['score'], ascending=False)
    dy = dy.head(25) # take only top 25 queries      
    
    dy.to_csv(outPath+'_'+query+'.csv', index=False)
    print('The results are stored in '+outPath+'_'+query+'.csv')