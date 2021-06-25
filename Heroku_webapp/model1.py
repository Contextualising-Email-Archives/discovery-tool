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
    meta_content_df = pd.read_pickle('models/lay_skilling.pkl')
    df = pd.DataFrame()
    if 'all' in df_list:

        df = meta_content_df.copy()
        #return df
    else:
        for name in df_list:
            # handle the error of custodian name not in the list    
            print(name)    
            temp = meta_content_df[meta_content_df['custodian']==name]        
            df = df.append(temp)

        df = df.reset_index(drop=True)

    
    return df

df = _return_df(['lay-k'])
print(df.columns)
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
#The following keeps 


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
# Following function is to phrase match 
# returns dictionary of queries and corresponding emails
def get_emails_set(df, query, search_method):
    
    phrases_to_search = tokenize_filter(query,  search_method)
    
    # Create a list of tokens for each item in each query
    query_tokens_list = [nlp(item.lower()) for item in phrases_to_search]    
    
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

   
#****************************************************************************#

def _get_model1_resultset(query, search_list, numResults):
    #phrases ==>  search query list
    #search_list ==> list of custodians
    #numResults ==> cap on the results list
     
    df = _return_df(search_list)        

    if(len(df) == 0): # suppose there are no records
        #return df,df
        return df
        
    df['combined_text'] = df.apply(lambda row: _add_combined_text(row), axis=1)    
    emails_dict = get_emails_set(df,query,'full')
    if len(emails_dict.keys()) == 0 and len(query.split())>1: #search doesnt return any result
        emails_dict = get_emails_set(df,query,'split')

    new_df = pd.DataFrame([(key,pubid) for key,val in emails_dict.items() for pubid in list(val) ], columns = ('Query','public_id'))
    new_df =  new_df.reset_index(drop=True)
    new_df = new_df.merge(meta_content_df, on='public_id')
        
    
    #print('len of new_df before', len(new_df))
    new_df = new_df.drop_duplicates(ignore_index=True)
    #print('len of new_df after', len(new_df))
    df = new_df
    num_queries = len(emails_dict.keys())
    if num_queries!=0:
        new_df = new_df.groupby('Query').head(int(numResults)//num_queries).reset_index(drop=True) # top numResults
    
   

    
    #return new_df,df
    return new_df

    