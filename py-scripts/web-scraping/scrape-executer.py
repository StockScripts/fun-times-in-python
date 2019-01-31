#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 23:02:27 2019

@author: nautilus
"""

#Import py functions
import sys
import psycopg2
import datetime
import pandas as pd
import multiprocessing as mp
from sqlalchemy import create_engine

#Import custom function
sys.path.append('/home/nautilus/development/fun-times-in-python/py-scripts/web-scraping')
from scrape_yahoo import ExtractYahooStockPerformance

print('Start time: ' + str(datetime.datetime.now()))

#Grab tickers
conn_string = "host='localhost' dbname='postgres' user='rbetzler' password='pwd'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

sql_file = '/home/nautilus/development/fun-times-in-python/sql-scripts/queries/scrape-stocks.sql'
query = open(sql_file).read()

cursor.execute(query)
tickers = []
for row in cursor:
    tickers.append(row)

if len(tickers) > 0:
    outputs = pd.DataFrame({'open' : [], 
                           'high' : [],
                           'low' : [],
                           'close' : [],
                           'adj_close' : [],
                           'volume' : [],
                           'unix_timestamp' : [],
                           'date_time' : [],
                           'dividend' : [],
                           'split_numerator' : [],
                           'split_denominator' : [],
                           'ticker' : []
                           })
    
    outputs = mp.Pool(4).map(ExtractYahooStockPerformance, tickers)
    output = pd.concat(outputs)
    
    #Load df to db
    engine = create_engine('postgresql://rbetzler:pwd@localhost:5432/postgres')
    output.to_sql('fact_yahoo_stocks', engine, if_exists = 'append')
    