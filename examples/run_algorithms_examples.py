#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 12:59:42 2019

@author: paco
"""

import time
import pdb
import numpy as np
import pandas as pd
from market.gateway import Gateway
from examples.algorithms import BuyTheBid, SimplePOV
from datetime import timedelta
import matplotlib.pyplot as plt
      


# =============================================================================
# TEST BUY THE BID ALGO
# =============================================================================

gtw = Gateway(ticker='ana',
             year=2019,
             month=5,
             day=21,
             latency=20000)
    

btb = BuyTheBid(1000000, 1)

t = time.time()
while (not btb.done) and (gtw.mkt_time < gtw.end_time):        
    
    btb.eval_and_act(gtw)
    gtw.tick()
    
print(time.time()-t)



# =============================================================================
# TEST SIMPLE POV ALGO
# =============================================================================

gtw = Gateway(ticker='ana',
             year=2019,
             month=5,
             day=21,
             start_h=14,
             end_h=16,
             latency=20000)

pov_algo = SimplePOV(is_buy=True, target_pov=0.2, lmtpx=np.Inf,
                       qty=int(1e7), sweep_max=5)

hist_bidask = list()
t = time.time()
mkt_nord = gtw.mkt_nord-1

while (not pov_algo.done) and (gtw.mkt_time < gtw.end_time):        
    ord_in_queue = pov_algo.eval_and_act(gtw)
    if ord_in_queue:  
        #gtw.tick()
        gtw.move_n_seconds(n_seconds=1)
    else:
        gtw.tick()
        
print(time.time()-t)


## PLOT 
bidask = pd.DataFrame(hist_bidask, columns=['bid', 'ask', 'timestamp'])
bidask.set_index(bidask.timestamp, inplace=True)
trades = pd.DataFrame(gtw.mkt.trades).loc[:gtw.mkt.ntrds-1]
trades.set_index(trades.timestamp, inplace=True)

# filter:

plt.figure(num=1, figsize=(20, 10))
start_t = bidask.index[0]


for i in range(20):
    end_t = start_t + timedelta(0,60)    
    subbidask = bidask.loc[start_t:end_t]
    subtrades = trades.loc[start_t:end_t]
    
    greenc = '#009900'
    redc = '#cc0000'

    plt.plot(subbidask.bid, color=greenc, label='bid1')
    plt.plot(subbidask.ask, color=redc, label='ask1')
    
    idx_buy_init = np.where(subtrades.buy_init)
    idx_sell_init = np.where(np.logical_not(subtrades.buy_init))
    buy_init_trd = subtrades.iloc[idx_buy_init]['price']
    sell_init_trd = subtrades.iloc[idx_sell_init]['price']
    
    plt.plot(buy_init_trd, color=greenc, linestyle=' ', marker='^', 
             markersize=10, label='aggbuy')
    plt.plot(sell_init_trd, color=redc, linestyle=' ', marker='v', 
             markersize=10, label='aggsell')
    plt.legend()
    plt.show()
    
    input("Click to advance")
    start_t = end_t
    plt.clf()
        
