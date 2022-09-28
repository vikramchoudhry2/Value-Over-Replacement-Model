#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from bs4 import BeautifulSoup as BS
import requests

get_ipython().system('pip install beautifulsoup4 --upgrade')
get_ipython().system('pip install certifi --upgrade')
get_ipython().system('pip install idna --upgrade')
get_ipython().system('pip install numpy --upgrade')
get_ipython().system('pip install pandas --upgrade')
get_ipython().system('pip install python-dateutil --upgrade')
get_ipython().system('pip install pytz --upgrade')
get_ipython().system('pip install requests --upgrade')
get_ipython().system('pip install six --upgrade')
get_ipython().system('pip install soupsieve --upgrade')
get_ipython().system('pip install urllib3 --upgrade')


# In[2]:


#loading the data
df = pd.read_csv('/Users/vikramchoudhry/Desktop/2021-VOR-Model/data/all_compiled.csv', index_col=0)

# removing extra characters in player names to prepare data for merging
df['Player'] = df['Player'].apply(lambda x: ' '.join(x.split()[:2]))

#removing commas from should-be float columns that are currently strings
comma_columns = ['REC_YD', 'PASS_YD', 'RUSH_YD']
for column in comma_columns:
  df[column] = df[column].apply(lambda x: x.replace(',', ''))

#converting all columns that should be floats to floats
df.iloc[:, 3:] = df.iloc[:, 3:].astype(float)

df.head()


# In[3]:


df['STANDARD'] = (df['RUSH_YD'] + df['REC_YD'])*0.1 + (df['RUSH_TD'] + df['REC_TD'])*6 + + df['PASS_YD']*0.04 + df['PASS_TD']*4 + (df['INTS'] + df['FL'])*-2

#standard + 0.5 * receptions
df['HALF_PPR'] = df['STANDARD'] + df['REC']*0.5

#standard + 1 * each reception
df['PPR'] = df['STANDARD'] + df['REC']

df.head()


# In[4]:


ADP_URL = 'https://www.fantasypros.com/nfl/adp/ppr-overall.php'

res = requests.get(ADP_URL)

soup = BS(res.content, 'html.parser')

table = soup.find('table', {'id': 'data'})

adp_df = pd.read_html(str(table))[0]

#cleaning the data.
#player name, team, and bye week were all located in the same column, and so we are splitting the column up and creating seperate columns
#for player name and team and removing bye week altogether
adp_df['Team'] = adp_df['Player Team (Bye)'].apply(lambda x: x.split()[-2])
adp_df['Player'] = adp_df['Player Team (Bye)'].apply(lambda x: ' '.join(x.split()[:-2]))
# removing extra characters in player names to prepare data for merging
adp_df['Player'] = adp_df['Player'].apply(lambda x: ' '.join(x.split()[:2]))

adp_df['POS'] = adp_df['POS'].apply(lambda x: x[:2])
adp_df = adp_df.loc[:, ['Player', 'Team', 'POS', 'AVG']]

#creating a column to rank players on their ADP
adp_df['ADP_RANK'] = adp_df['AVG'].rank(method='first')

adp_df[:100].tail(15)


# In[5]:


replacement_players = {}
for _, row in adp_df[:100].iterrows():
    replacement_players[row['POS']] = row['Player']

print(replacement_players)

replacement_values = pd.DataFrame({
    'Player': replacement_players.values(),
    'POS': replacement_players.keys()}).merge(
    df, on=['Player', 'POS']).loc[:, ['POS', 'PPR']].rename({
    'PPR': 'REPLACEMENT_VALUE'}, axis=1)

replacement_values.head()


# In[13]:


vor_df = df.loc[:, ['Player', 'POS', 'Team', 'PPR']].merge(replacement_values, on='POS')

vor_df['VOR'] = vor_df['PPR'] - vor_df['REPLACEMENT_VALUE']

vor_df.sort_values(by='VOR', ascending=False).loc[:, ['Player', 'POS', 'Team', 'PPR', 'VOR']].reset_index(drop=True).head(55)


# In[ ]:




