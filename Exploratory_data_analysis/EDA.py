import pandas as pd

from email import utils
import matplotlib.pyplot as plt
import seaborn as sns

dataPath = input('Enter data path: ')  # please enter the full data path where you have stored Enron.pkl
df = pd.read_pickle(dataPath)
#print(dataPath)

#print(len(df))
#print(df.head(5))
print(df.custodian.value_counts())
#==========================================================================
#to see how many mails in each mailbox
plt.figure(figsize=(25,8))
p = sns.countplot(data = df, x= 'custodian')
p.set_xticklabels(p.get_xticklabels(),rotation = 90);
p.show()

#==========================================================================
#to see over all email frequency of Lay.k and Skilling.J
temp = df[df['custodian'].isin(['lay-k','skilling-j'])].copy()
t = temp[ temp['date']< pd.to_datetime('2006-01-01')]
t = t[t['date'] > pd.to_datetime('2000-01-01')]
#print(len(t))
t = t.groupby('date').custodian.count()

plt.figure(figsize=(20,12))
plt.xlabel('sent date')
plt.ylabel('# of emails')
plt.title('Overall email frequency')
t.plot()

#==========================================================================
#what are the important dates?

print('Enron filed bankruptcy on 2/12/2001. So let us slice data around that')
print(min(df.date)) # prints earliest date
print(max(df.date)) # prints last date in this dataset

#What do their mailboxes look like?
plt.figure (figsize=(25,8))
p =sns.countplot(data = df, x='custodian', order=df['custodian'].value_counts().index);
#plt.legend(loc='upper right');
p.set_xticklabels(p.get_xticklabels(),rotation = 90);
p.plot()

#==========================================================================
print('Who are the primary communicators - what is the outbox look like ')
print('unique receivers of emails from Lay and Skilling')

t = df.copy()
t = df[ df['date']< pd.to_datetime('2003-01-01')]
t = t[t['date'] > pd.to_datetime('1999-01-01')]
t1 = t[t['custodian'].isin(['lay-k','skilling-j'])]

t1 = t1.groupby('date').to.nunique()
plt.figure(figsize=(20,12))
plt.xlabel('sent date')
plt.ylabel('# unique receivers from lay ')
plt.title('From lay and skilling')
#plt.legend(labels =['Overall','lay-skilling'], loc='upper right')

t1.plot()

#==========================================================================

print('unique receivers from Lay and Skilling')
lay_skilling = df[df['custodian'].isin(['lay-k','skilling-j'])]
t = lay_skilling.copy()
t['to_names'] = t['to'].apply(lambda x: x.split(','))
result = pd.DataFrame([(tup.public_id,d, tup.from_) for tup in t.itertuples() for d in tup.to_names], columns = ('public_id', 'to', 'from_') )
result_to = result[result['to'].map((result.to.value_counts()<1000) &(result.to.value_counts()>100))] # only more than 100. top 3 are self mails
result_from = result[result['from_'].map((result.from_.value_counts()>100))] # only more than 10
plt.figure(figsize=(20,12))
plt.xlabel('sent date')
plt.ylabel('# unique receivers from lay ')
plt.title('From lay and skilling')
p =sns.countplot(data = result_to, x='to', order=result_to['to'].value_counts().index);
#plt.legend(loc='upper right');
p.set_xticklabels(p.get_xticklabels(),rotation = 90);
p.plot()

#==========================================================================
