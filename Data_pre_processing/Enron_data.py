#1. The following code reads data from interesting custodians
#2. The output dataframe is saved as Enron_full.pkl
#3. Lay-k and skilling-j at Enron.pkl
from collections import Counter
from datetime import datetime
from email import utils
from email.parser import Parser
import os
import sys

import pandas as pd


#the following functions reads all emails from people list and creates a dataframe
def _create_dataframe_from_Enron_folders(dataPath):
    print(dataPath)
    
    message_id = []
    public_id=[]
    to_ = [] 
    cc_ =[]
    bcc_ =[]
    from_ = []
    sent_date_time = []
    subject = []
    email_body = []
    attachments_ = []
    
    i=0 # used for keeping track of the file volume
    j=0 # used for testing
    if os.path.exists(dataPath):
        for subdir, dirs, files in os.walk(dataPath):
            #print(subdir)
            for file in files: 

                j += 1
                file = os.path.join(subdir,file)   
                try:
                    #print(file)
                    with open(file, 'r', encoding= 'UTF-8', errors='ignore') as f:   # to avoid unprintable characters                         
                        lines = f.read()                              
                        email = Parser().parsestr(lines)  
                        
                        #donot add any new features of email object here

                        email_to = email['to']
                        email_to = email_to.replace("\n", "")
                        email_to = email_to.replace("\t", "")
                        email_to = email_to.replace(" ", "")
                        #email_to = email_to.split(",")  

                        if len(email_to)>0:  # avoid spurious folders # add new features of email object from here
                            to_.append(email_to)
                            message_id.append( email['Message-ID'])
                            i += 1
                        else:
                            to_.append('')
                            
                        if email['from']:
                            from_.append(email['from'])
                        else:
                            from_.append('')  

                        if email['Date']:
                            sent_date_time.append(email['Date'])

                        if email['Subject']:
                            subject.append(email['Subject'])
                        else:
                            subject.append('')

                        public_id.append(file.replace(dataPath,''))

                        # attachments
                        attachment = ''                                                                   
                        if email.is_multipart(): # check whether there are attachments                               
                            for part in email.walk():                                    
                                attachment= attachment + '\n' +part
                        attachment = 'No Attachment' if attachment =='' else attachment     
                        attachments_.append(attachment) 

                        #content
                        content = email.get_payload()
                        if len(content)> 0:
                            email_body.append(content)
                        else:
                            email_body.append('')

                        # cc   
                        cc_list = email['cc']   
                        if cc_list:
                            cc_list = cc_list.replace("\n","")                                
                            cc_list = cc_list.replace("\t","")
                            cc_list = cc_list.replace(" ", "")
                            #cc_list = cc_list.split(",")
                            cc_.append(cc_list)  
                        else:
                            cc_.append('No_Name')


                        # bcc
                        bcc_list = email['bcc']
                        if bcc_list:
                            bcc_list = bcc_list.replace("\n","")                                
                            bcc_list = bcc_list.replace("\t","")
                            bcc_list = bcc_list.replace(" ", "")
                            #bcc_list = bcc_list.split(",")
                            if cc_list != bcc_list:
                                bcc_.append(bcc_list)
                            else:
                                bcc_.append('No_Name')
                        else:
                            bcc_.append('No_Name')


                except:                        
                    continue
                    
                   
    dataFrame = pd.DataFrame(list(zip(public_id, message_id, to_,from_,cc_, bcc_,sent_date_time,subject,email_body, attachments_)),
                             columns = ('public_id','message_id','to','from_','cc','bcc','sent_date','subject','body_content', 'attach_content'))
    print(i, len(dataFrame)) 
    print(len(public_id), len(message_id), len(to_), len(from_), len(cc_), len(bcc_), len(sent_date_time), len(subject), len(attachments_))
    return  dataFrame
            
# get only date from date format
def _get_date(x)   :
    default_date = 'Tue, 1 Jan 2222 00:00:00 -0000'
    try:
        result = pd.to_datetime(x).date()
        
    except :
        result = pd.to_datetime(default_date).date()
        
    return result


dataPath = (sys.argv and sys.argv[1]) or input('Enter data path: ')
print(f"dataPath {dataPath}")

df = _create_dataframe_from_Enron_folders(dataPath)

#test
print('checking')
print('No.of records: ',len(df)) 


#checking with the operating system
operating_system = (sys.argv and sys.argv[2]) or input('Enter your operating system: 1 for Windows, 2 for Linux: ')
print(f"operating_system: {operating_system}")

if operating_system == '1':
    # on windows
    df['custodian'] = df['public_id'].apply(lambda x: x.split('\\')[0])
elif operating_system == '2':
    #This is on linux
    df['custodian'] = df['public_id'].apply(lambda x: x.split('/')[0])

print('checking')
print('No.of custodians: ',df.custodian.nunique())


df = df.fillna({'custodian':'No_Name', 'public_id': 'No_publicID',  'from':'No_Name',
                'to':'No_Name',
                'cc':'No_Name', 'bcc':'No_Name', 'sent_date':pd.to_datetime('2222-01-01'),  'subject':'No Subject',
                'body_content':'No content', 'attach_content':'No Attachment'})

print('converting date formats')
df['date'] = df['sent_date'].apply(lambda x: _get_date(x))

#len(df[df['date'] == pd.to_datetime('2222/01/01')]) # are there any default dates? should return '0' when run
#Drop over all duplicates if any. I forgot to check how many duplicates were there. 
df = df.drop_duplicates(keep = 'first')
df = df.reset_index(drop=True)

if len(df) == 495554: 
    print('no duplicates')
else:
    print('has duplicates')

outputPath = (sys.argv and sys.argv[3]) or input('Enter output path location: (include / at the end)')
print(f"outputPath: {outputPath}")
df.to_pickle(outputPath+'Enron_full.pkl')
print('The processed output is saved at '+outputPath+'Enron_full.pkl')
print('Please reuse this output to avoid running this whole process again')

print('Creating folders for CEOs - Lay.K and Skilling.J')

lay = df[df['custodian']=='lay-k']
lay= lay.reset_index(drop=True)
lay.to_pickle(outputPath+'lay_k.pkl')

skilling = df[df['custodian']=='skilling-j']
skilling= skilling.reset_index(drop=True)
skilling.to_pickle(outputPath+'skilling_j.pkl')

print('the processed output for lay.K and skilling.J are created at '+outputPath+'lay_k.pkl'+ ' and '+ outputPath+'skilling_j.pkl' )

