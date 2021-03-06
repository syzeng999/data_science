# -*- coding: utf-8 -*-

# Jonathan Halverson
# Sunday, February 12, 2017

import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 200)

# flag to get updated data or not
scrape_cards = False

# create a list of the card numbers
cards = range(1, 209)
cards.reverse()
cards.remove(151)
cards.remove(176)

# scrape new card data if needed
base_path = 'ppv_wikipedia_cards/wikipedia_cards_'
if scrape_cards:
  import requests
  for card in cards:
    url = 'https://en.wikipedia.org/wiki/UFC_' + str(card)
    r = requests.get(url)
    with open(base_path + str(card) + '.html', 'w') as f:
      f.write(r.content)

# list index of fight card
table_idx = dict([(card, 2) for card in cards])
table_idx[31] = 3
table_idx[40] = 3
table_idx[57] = 3
table_idx[149] = 21

# list index of event info
info_idx = dict([(card, 0) for card in cards])
info_idx[31] = 1
info_idx[57] = 1
info_idx[149] = 19

fights = pd.DataFrame()
for card in cards:
  # read tables from html into a list of dataframes
  with open(base_path + str(card) + '.html', 'r') as f:
    html = f.read()
  # extract table
  dfs = pd.read_html(html)
  df = dfs[table_idx[card]].copy()
  # drop rows and concatenate
  df = df[df[2].isin(['def.', 'vs.', 'def', 'vs'])]
  # load table of fight card meta data
  venue = dfs[info_idx[card]]
  venue.set_index(0, inplace=True)
  # add new columns
  df['Card'] = 'UFC ' + str(card)
  df['Location'] = venue.loc['City', 1]
  df['Date'] = venue.loc['Date', 1]
  fights = pd.concat([fights, df], ignore_index=True)

fights.reset_index(drop=True, inplace=True)
fights.drop(labels=[7], axis=1, inplace=True)
fights.columns = ['Weight', 'Winner', 'DefVs', 'Loser', 'Method', 'Round', 'Time', 'Card', 'Location', 'Date'] 

# clean names
fights['Winner'] = fights['Winner'].str.replace('\\(c\\)|\\(ic\\)|\\(UFC Champion\\)', repl='').str.strip()
fights['Loser'] = fights['Loser'].str.replace('\\(c\\)|\\(ic\\)|\\(Pride Champion\\)', repl='').str.strip()

# clean dates
fights.Date = fights.Date.str.encode('ascii', errors='ignore')
fights.Date = fights.Date.apply(lambda x: x if '(' not in x else x[x.index('(') + 1:-1])
fights.Date = fights.Date.str.replace('\\[.\\]', '')
fights.Date = pd.to_datetime(fights.Date)

# write dataframe to CSV file
fights.to_csv('ppv_wikipedia_cards/ppv_wikipedia_fights.csv', encoding='utf-8', index=False)

#############################
fighter = u'José Aldo'
fighter = 'Nick Diaz'
fighter = 'Carlos Condit'
fighter = u'Patrick Côté'
fighter = 'Georges St-Pierre'
fighter = 'Rafael dos Anjos'
fighter = 'Conor McGregor'
fighter = 'Anderson Silva'

#print fights[(fights.Winner.str.contains('Georges')) | (fights.Loser.str.contains('Georges'))]
#print fights[(fights.Winner == fighter) | (fights.Loser == fighter)]
#print fights[(~fights.DefVs.isin(['def\.'])) & (fights.DefVs.isin(['def']))]
#print fights[(~fights.Method.str.contains('TKO')) & (fights.Method.str.contains('KO'))]
#print fights[fights.Method.str.contains('no contest', case=False)]
#print fights.Winner.apply(lambda x: x if len(x.split()) < 2 else 'NaN').unique()
#print fights.Date.apply(lambda x: x.year).value_counts().sort_index()

# possible ways for a fight to end
s = fights.Method.apply(lambda x: x.encode('ascii', 'ignore')).str.replace(r'\(.*\)','')
s = s.str.replace('\\[..\\]', '').str.replace('[0-9\\,\\(]', '').apply(lambda x: x.lower().strip()).sort_values().unique()
print s

# Which days of the week were PPV's held?
#fights['DayOfWeek'] = fights.Date.dt.weekday_name
#print fights[['Card', 'Location', 'Date', 'DayOfWeek']].drop_duplicates().DayOfWeek.value_counts()

# Submissions vs KOs in championship rounds
#print fights[(fights.Round.isin(['4', '5'])) & (fights.Method.str.contains('Submission', case=False))]
#print fights[(fights.Round.isin(['4', '5'])) & (fights.Method.str.contains('KO', case=False))]
