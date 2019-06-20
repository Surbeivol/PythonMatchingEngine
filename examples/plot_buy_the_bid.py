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



# =============================================================================
# RESTART MARKET
# =============================================================================

gtw = Gateway(ticker='ana',
             year=2019,
             month=5,
             day=23,
             start_h=9,
             end_h=10,
             latency=20000)
    


btb = BuyTheBid(1000000, 1)



hist_bidask = list()
hist_leaves = list()
t = time.time()

while (not btb.done) and (gtw.mkt_time < gtw.stop_time):        
    hist_bidask.append([gtw.mkt.bbidpx, gtw.mkt.baskpx, gtw.mkt_time])
    if not gtw.flying_ord():    
        try:
            order = gtw.ord_status(btb.leave_uid)        
            if order['leavesqty']>0:
                hist_leaves.append([order['price'], gtw.mkt_time])
        except:
            pass
        
    btb.eval_and_act(gtw)        
    gtw.tick()    
print(time.time()-t)





# =============================================================================
# PLOTTING THE ALGO RESULT 
# =============================================================================


## MARKET BIDASK
bidask = pd.DataFrame(hist_bidask, columns=['bid', 'ask', 'timestamp'])
bidask.set_index(bidask.timestamp, inplace=True)
# MARKET TRADES 
trades = pd.DataFrame(gtw.mkt.trades).loc[:gtw.mkt.ntrds-1]
trades.set_index(trades.timestamp, inplace=True)
# MY TRADES 
my_trades = pd.DataFrame(gtw.mkt.my_trades).loc[:gtw.mkt.my_ntrds-1]
my_trades.set_index(my_trades.timestamp, inplace=True)

leaves = pd.DataFrame(hist_leaves, columns=['price', 'timestamp'])
leaves.set_index(leaves.timestamp, inplace=True)

# filter:

plt.figure(num=1, figsize=(20, 10))
start_t = bidask.index[0]
win_size = 120
win_move = 20

for i in range(200):
    end_t = start_t + timedelta(0,win_size)    
    subbidask = bidask.loc[start_t:end_t]
    subtrades = trades.loc[start_t:end_t]
    mysubtrades = my_trades.loc[start_t:end_t]
    subleaves = leaves.loc[start_t:end_t]
    
    greenc = '#009900'
    redc = '#cc0000'

    plt.plot(subbidask.bid, color=greenc, label='bid1')
    plt.plot(subbidask.ask, color=redc, label='ask1')
    
    idx_buy_init = np.where(subtrades.buy_init * (subtrades.agg_ord > 0))
    idx_sell_init = np.where(np.logical_not(subtrades.buy_init) * \
                             (subtrades.agg_ord > 0))
    buy_init_trd = subtrades.iloc[idx_buy_init]['price']
    sell_init_trd = subtrades.iloc[idx_sell_init]['price']
    
    idx_my_buy_init = np.where(mysubtrades.buy_init)
    idx_my_sell_init = np.where(np.logical_not(mysubtrades.buy_init))
    my_buy_init_trd = mysubtrades.iloc[idx_my_buy_init]['price']
    my_sell_init_trd = mysubtrades.iloc[idx_my_sell_init]['price']
    
    plt.plot(buy_init_trd, color=greenc, linestyle=' ', marker='^', 
             markersize=12, label='aggbuy')
    plt.plot(sell_init_trd, color=redc, linestyle=' ', marker='v', 
             markersize=12, label='aggsell')
    
    plt.plot(my_buy_init_trd, color='blue', linestyle=' ', marker='^', 
             markersize=7, label='aggbuy')
    plt.plot(my_sell_init_trd, color='blue', linestyle=' ', marker='v', 
             markersize=7, label='aggsell')
    
    plt.plot(subleaves.price, color='blue', linestyle=' ', marker='.', 
             markersize=5, label='aggbuy')
    
    plt.legend()
    plt.show(block=False)
    
    input("Click to advance")
    
    start_t += timedelta(0, win_move) 
    plt.clf()