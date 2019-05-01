# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 12:03:03 2017

"""

import tweepy
import csv
import pandas as pd
import matplotlib.pylab as plt
from textblob import TextBlob
import numpy as np
import matplotlib.dates as mdates
import string
import re

#input your credentials here
# keys and tokens from the Twitter Dev Console
consumer_key = "*****"
consumer_secret = "****"
access_token = "****"
access_token_secret = "****"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

# Truncate any already existing file
csvFile = open('Checking.csv', "w+")
csvFile.close()
# Open/Create a file to append data
csvFile = open('Checking.csv', 'a')
#Use csv Writer
csvWriter = csv.writer(csvFile)
query = raw_input("Enter your search item:")
csvWriter.writerow(['Created','Text','Retweet Count'])

def remove_punct(text):
    text=str(text)
    text  = "".join([char for char in text if char not in string.punctuation])
    text = re.sub('([0-9]+)|(https?://\S+)|(#\S+)', '', text)
    return text


for tweet in tweepy.Cursor(api.search,
                           q=query,
                           count=5,
                           result_type="recent",
                           include_entities=True,
                           lang="en").items(5000):
    
    csvWriter.writerow([tweet.created_at, remove_punct(tweet.text.encode('utf-8')),tweet.retweet_count])
    
csvFile.close()    

dataframe = pd.read_csv("Checking.csv")
dataframe['Sentiment']= 0
dataframe['Score']=0.0    


for i,row in dataframe.iterrows():
    sent = TextBlob(row['Text'])
    dataframe.loc[i, 'Score'] = sent.sentiment.polarity
    if sent.sentiment.polarity > 0:
        dataframe.loc[i, 'Sentiment'] = 1  
    elif sent.sentiment.polarity < 0:
        dataframe.loc[i, 'Sentiment'] = -1 
         

stats=dataframe['Sentiment'].value_counts()        

stats_n=dataframe['Sentiment'].value_counts(normalize=True)           

obj= ('Neutral','Possitive','Negative')
y_pos = np.arange(len(obj))


plt.bar(y_pos, stats, align='center', alpha=0.75)
plt.xticks(y_pos, obj)
plt.xlabel('Sentiment',fontsize=12)
plt.ylabel('Frequency',fontsize=12)
plt.title('Sentiment Analysis',fontsize=14)
plt.show() 
    
print "Showing percentage of the nature of the tweets:"
print "Neutral Tweets:","%.2f"%(100*stats_n[0]),"%"  
print "Possitive Tweets:","%.2f"%(100*stats_n[1]),"%"
print "Negative Tweets:","%.2f"%(100*stats_n[-1]),"%"


dataframe.index = pd.to_datetime(dataframe['Created'])
ax= dataframe['Score'].plot()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y ,%H:%M'))
ax.set_title("Sentiment Score v/s Time",fontsize=14)
ax.set_xlabel("Created",fontsize=12)
ax.set_ylabel("Sentiment Score",fontsize=12) 
plt.show() 


dataframe.index = dataframe['Unnamed: 0']
for i,row in dataframe.iterrows():
    if row['Score']>0:
        pt=plt.scatter(i,row['Score'],c='green')
    elif row['Score']==0:
        nu=plt.scatter(i,row['Score'],c='yellow')     
    else:
        nt=plt.scatter(i,row['Score'],c='red') 
plt.legend((pt,nu,nt),('Positive','Neutral','Negative')) 
plt.title("Cluster",fontsize=14)
plt.xlabel("Tweets",fontsize=12)
plt.ylabel("Score",fontsize=12)       
plt.show()




dataframe.index = pd.to_datetime(dataframe['Created'])
d = dataframe.groupby(pd.TimeGrouper(freq='D'))['Score'].count()
d = pd.DataFrame(d)
date = d['Score'].argmax()
date= date.strftime("%d-%m-%Y")
day=int(date[0:2])
d= dataframe[dataframe.index.day==day]       
new= d.groupby(pd.TimeGrouper(freq='H'))['Score'].count()
new= pd.DataFrame(new)
ax=new.plot(kind='line',legend=False)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_title("Hourly Tweets for "+ date,fontsize=14)
ax.set_xlabel("Time",fontsize=12)
ax.set_ylabel("Tweet Count",fontsize=12) 
plt.show() 


print "Most famous tweets are:"
maximum = max(dataframe['Retweet Count'])
for i,row in dataframe.iterrows():
    if row['Retweet Count'] == maximum:
        print row['Text']