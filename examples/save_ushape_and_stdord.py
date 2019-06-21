#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from maching_engine_utils.es_market_calendar import get_open_days
from configuration_yaml import Configuration
from maching_engine_utils.df_from_supertrack import Supertrack
import pickle
from tqdm import tqdm
sys.path.append(os.getcwd())
sys.path.append('../')

supertrack = Supertrack()
window = 70
from_date = datetime(2018, 1, 1)
today = datetime.now().date()
tickers = Configuration('../config/liq_bands.yml').config
tickers = list(tickers.keys())
dates = get_open_days(from_date, today)

file_name = './../../PythonMatchingEngineFork/data/ushape'
try:
    with open(file_name, 'rb') as f:
        ushape = pickle.load(f)
except FileNotFoundError:
    print('ushape not found')
    ushape = {'tickers': {ticker: dict() for ticker in tickers}}

file_name = './../../PythonMatchingEngineFork/data/std_ord'
try:
    with open(file_name, 'rb') as f:
        std_ord = pickle.load(f)
except FileNotFoundError:
    print('std_ord not found')
    std_ord = {'tickers': {ticker: dict() for ticker in tickers}}

for ticker in tqdm(tickers):

    for end_day in dates:
        
        download = True
        
        if ticker in ushape['tickers'].keys():
            if end_day.date() in ushape['tickers'][ticker].keys():
                download = False
        
        if download:

            start_day = end_day.date() - timedelta(window)
    
            qry = (
                f"select date, time, totvol, tottrd "
                f"from sibe_{end_day.year}.ushape_{end_day.year} "
                f"where symbol = '{ticker}' "
                f"and time <> 'clo' and time <> 'ope' "
                f"and date < '{end_day}' and date >= '{start_day}'"
            )
            
            df_year = supertrack.get_df_from_qry(qry=qry)
            
            if start_day.year != end_day.year:
            
                qry = (f"select date, time, totvol, tottrd "
                       f"from sibe_{start_day.year}.ushape_{start_day.year} "
                       f"where symbol = '{ticker}' "
                       f"and time <> 'clo' and time <> 'ope' "
                       f"and date >= '{start_day}'")
                
                df_prev_year = supertrack.get_df_from_qry(qry=qry)
                df_year = pd.concat([df_prev_year, df_year])
            
            group_df = df_year[['time',
                                'totvol',
                                'tottrd']].groupby('time').sum()
            group_df = group_df / len(df_year.date.unique())
            totvol = group_df.totvol.values
            sum_totvol = np.sum(totvol)
            pct_vol = totvol / sum_totvol
            avg_trd_vol = totvol / group_df.tottrd.values
            avg_trd_vol = np.round(avg_trd_vol, 0)
            
            std_ord['tickers'][ticker][end_day.date()] = avg_trd_vol
            ushape['tickers'][ticker][end_day.date()] = pct_vol
        
ushape['dates'] = dates
std_ord['dates'] = dates
legend = [datetime.strptime(value, '%H:%M').time() for value in group_df.index]
ushape['legend'] = np.array(legend)
std_ord['legend'] = np.array(legend)

file_name = './../../PythonMatchingEngineFork/data/std_ord'
with open(file_name, 'wb') as f:
    pickle.dump(std_ord, f)

file_name = './../../PythonMatchingEngineFork/data/ushape'
with open(file_name, 'wb') as f:
    pickle.dump(ushape, f)
