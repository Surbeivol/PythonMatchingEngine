#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 08:21:48 2019

@author: paco
"""
from market import Market
import numpy as np 
import matplotlib.pyplot as plt
import time
import pandas as pd
import pdb

# Create 500k buys and sells with normal distribs
# with real live tick sizes 
ticksize = 0.001
num_ords = 500000
askprices = np.round(np.random.normal(15.1, 0.1, num_ords)/ticksize)*ticksize
bidprices = np.round(np.random.normal(14.9, 0.1, num_ords)/ticksize)*ticksize
prices = np.concatenate((bidprices, askprices))

plt.title('Price distribution of buy and sell orders')
plt.hist(bidprices, 100, alpha= 0.5, label='bids')
plt.hist(askprices, 100, alpha= 0.5, label='asks')
plt.legend()

# first are buys last are sells
bid_is_buy = np.ones(num_ords, dtype=bool)
ask_is_buy = np.zeros(num_ords, dtype=bool)
is_buy = np.concatenate((bid_is_buy, ask_is_buy))

# random quantities
qtys = np.random.randint(1, 1000, 2*num_ords)

# shuffle orders
shuffled_idx = np.arange(2*num_ords)
np.random.shuffle(shuffled_idx)
orders = [[is_buy[i], qtys[i], prices[i]] for i in shuffled_idx]

# PERFORMANCE
market = Market()

t = time.time()
for i in range(2*num_ords):
    market.send(*orders[i])
print(time.time()-t)

# Number of executions 
len(market.trades)

trd_price = [trd[0] for trd in market.trades]
plt.plot(trd_price[0:1000])

t =time.time()
for i in range(10000):
    market.top_bids(5)
print(time.time()-t)