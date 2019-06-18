# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:46:49 2019

@author: fmerlos
"""

import os
os.chdir('C:/DEV/PythonMatchingEngine')
import sys
sys.path.append('C:/DEV/PythonMatchingEngine')
import time
import pdb
import numpy as np
from market.gateway import Gateway
from examples.algorithms import BuyTheBid, SimplePOV
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd



gtw = Gateway(ticker='san',
             year=2019,
             month=5,
             day=23,
             latency=20000)
    

pov_algo = SimplePOV(is_buy=True, target_pov=0.2, lmtpx=np.Inf,
                       qty=int(1e7), sweep_max=5)

hist_bidask = list()
t = time.time()
mkt_nord = gtw.mkt_nord-1
while (not pov_algo.done) and (gtw.mkt_idx < mkt_nord):        
    pov_algo.eval_and_act(gtw)
    gtw.tick()    
    hist_bidask.append([gtw.mkt.bbidpx,
                        gtw.mkt.baskpx, gtw.mkt_time])    
print(time.time()-t)


## MARKET BIDASK
bidask = pd.DataFrame(hist_bidask, columns=['bid', 'ask', 'timestamp'])
bidask.set_index(bidask.timestamp, inplace=True)
# MARKET TRADES 
trades = pd.DataFrame(gtw.mkt.trades).loc[:gtw.mkt.ntrds-1]
trades.set_index(trades.timestamp, inplace=True)
# MY TRADES 
my_trades = pd.DataFrame(gtw.mkt.my_trades).loc[:gtw.mkt.my_ntrds-1]
my_trades.set_index(my_trades.timestamp, inplace=True)

# filter:

plt.figure(num=1, figsize=(20, 10))
start_t = bidask.index[0]


for i in range(50):
    end_t = start_t + timedelta(0,60)    
    subbidask = bidask.loc[start_t:end_t]
    subtrades = trades.loc[start_t:end_t]
    mysubtrades = my_trades.loc[start_t:end_t]
    
    greenc = '#009900'
    redc = '#cc0000'

    plt.plot(subbidask.bid, color=greenc, label='bid1')
    plt.plot(subbidask.ask, color=redc, label='ask1')
    
    idx_buy_init = np.where(subtrades.buy_init)
    idx_sell_init = np.where(np.logical_not(subtrades.buy_init))
    buy_init_trd = subtrades.iloc[idx_buy_init]['price']
    sell_init_trd = subtrades.iloc[idx_sell_init]['price']
    
    idx_my_buy_init = np.where(mysubtrades.buy_init)
    idx_my_sell_init = np.where(np.logical_not(mysubtrades.buy_init))
    my_buy_init_trd = mysubtrades.iloc[idx_my_buy_init]['price']
    my_sell_init_trd = mysubtrades.iloc[idx_my_sell_init]['price']
    
    plt.plot(buy_init_trd, color=greenc, linestyle=' ', marker='^', 
             markersize=10, label='aggbuy')
    plt.plot(sell_init_trd, color=redc, linestyle=' ', marker='v', 
             markersize=10, label='aggsell')
    
    plt.plot(my_buy_init_trd, color='blue', linestyle=' ', marker='^', 
             markersize=10, label='aggbuy')
    plt.plot(my_sell_init_trd, color=redc, linestyle=' ', marker='v', 
             markersize=10, label='aggsell')
    
    plt.legend()
    plt.show(block=False)
    
    input("Click to advance")
    
    start_t += timedelta(0,5) 
    plt.clf()