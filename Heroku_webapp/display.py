
import pandas as pd 
import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

def save_frequency_plot(df):

    query = df.loc[0]['Query']
    #plt.figure(figsize=(10,6))
    t1 = df.groupby('date').to.count()
    
    plt.title('Query Frequency')
    plt.ylabel(' Frequency of ' +query+' in mails')
    #t1.plot()
    plt.plot(t1)

    freq_plt = '/home/santhilata/Desktop/freq_plot.png'
    plt.savefig(freq_plt)
    print('saving the file from freq')

    return 

def save_time_plot(df, df_name,query, from_date, to_date):
    #query = df.loc[0]['Query']
     
    plt.figure(figsize=(10,6))
    plt.scatter(x=df.date, y=df.public_id)
    title = 'query='+query+'; data='+df_name
    plt.title(title)
    #plt.legend(labels = [query], loc='upper right')
    plt.yticks([], []);

    #time_plt = 'static/lib/time_plot_'+query+df_name+'.pdf'

    time_plt1 = 'static/lib/time_plot_'+query+df_name+'from_'+from_date+'_to_'+to_date+'.png'
    #time_plt1 = 'images/time_plot_'+query+df_name+'from_'+from_date+'_to_'+to_date+'.png'
    
    
    #plt.savefig(time_plt)
    plt.savefig(time_plt1)
    print('saving the file from time')
    return 


def create_wordcloud(col,  df_name,query,  from_date, to_date):
    text = ' '.join(x for x in list(col))

    stopwords = set(STOPWORDS)
    stopwords.update(['Enron','Subject:','From:','To:','new', 'image','will','shall','please','blank','said'])

    wordcloud = WordCloud(stopwords=stopwords, max_font_size = 50, max_words=100, background_color='white').generate(text)
    plt.figure(figsize=(10,6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    wc_plt = 'static/lib/wc_'+query+df_name+'from_'+from_date+'_to_'+to_date+'.png'
    #wc_plt = 'images/wc_'+query+df_name+'from_'+from_date+'_to_'+to_date+'.png'
    plt.savefig(wc_plt)

    return
