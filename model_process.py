import ijson
import re
from datetime import datetime
from bs4 import BeautifulSoup
import json
import requests
import pandas as pd
import ijson
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random
def str_lenth(sentence):
    return int(len(sentence.split(' ')))

df_match_clean = pd.read_json('match_df.json', lines=True)
df_news = pd.read_json('news_df.json', lines=True)

count = 0
df_main = df_match_clean.copy(deep=True)
df_main = df_main.head(1000)
df_news_copy = df_news.copy(deep=True)
for index, row in df_main.iterrows():
    count_str = 0
    timeend = int(df_match_clean.iloc[index]['time'])
    timestart = int(df_match_clean.iloc[index]['time'])-3*2592000000
    urllst = df_match_clean.iloc[index]['url']
    winteam = df_match_clean.iloc[index]['team'][0]
    loseteam = df_match_clean.iloc[index]['team'][1]

    timeend1 = int(df_news_copy.iloc[index]['time'])
    timestart1 = int(df_news_copy.iloc[index]['time'])-3*2592000000
    urllst1 = df_news_copy.iloc[index]['url']

    df1 = df_match_clean[df_match_clean['time']>=timestart]
    df2 = df1[df1['time']<(timeend-100)]
    df_win = df2[df2['team'].apply(lambda x: winteam in x)]
    df_lose = df2[df2['team'].apply(lambda x: loseteam in x)]

    df5 = df_news_copy[df_news_copy['time']>=timestart]
    df6 = df5[df5['time']<(timeend-100)]
    df_win1 = df6[df6['url'].apply(lambda x: winteam in x)]
    df_lose1 = df6[df6['url'].apply(lambda x: loseteam in x)]

    try:
        winlst = df_win['content'].tolist()  # 尝试访问可能不存在的列
    except KeyError:
        winlst = []
    try:
        loselst = df_lose['content'].tolist()  # 尝试访问可能不存在的列
    except KeyError:
        loselst = []
    try:
        winlst1 = df_win1['content'].tolist()  # 尝试访问可能不存在的列
    except KeyError:
        winlst1 = []
    try:
        loselst1 = df_lose1['content'].tolist()  # 尝试访问可能不存在的列
    except KeyError:
        loselst1 = []

    reswin = ""
    reslose = ""
    rannum = random.randint(0,1)
    for i in winlst:
        if count_str <= 2000:
            reswin += str(i)
            count_str+=str_lenth(i)
    for i in loselst:
        if count_str <= 4000:
            reslose += str(i)
            count_str+=str_lenth(i)
    for i in winlst1:
        if count_str <= 6000:
            reswin += str(i)
            count_str+=str_lenth(i)
    for i in loselst1:
        if count_str <= 8000:
            reslose += str(i)
            count_str+=str_lenth(i)
    if rannum ==1:
        resstr = reswin+reslose
        df_main.at[index, 'content'] = resstr
        df_main.at[index, 'url'] = 1
    if rannum ==0:
        resstr = reslose+reswin
        df_main.at[index, 'content'] = resstr
        df_main.at[index, 'url'] = 0

    print(count)
    count+=1


df_main.to_json('output.json', orient='records', lines=True)
strlst = [str_lenth(i) for i in df_main[df_main['content'] != ''].content.tolist()]
print(len(strlst))
print(max(strlst))
print(min(strlst))
print(sum(strlst) / len(strlst))
print(np.percentile(strlst, 15))
print(np.percentile(strlst, 30))
print(np.percentile(strlst, 45))
print(np.percentile(strlst, 60))
print(np.percentile(strlst, 75))
print(np.percentile(strlst, 90))