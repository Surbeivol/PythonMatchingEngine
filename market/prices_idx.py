#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
For all European Stocks Exchanges MiFID II regulation stablishes the 
minimum tick size for each product depending on the price and the
Average Daily Trades of this product. 

You can find more info and the corresponding tick size tables in:
    
    https://www.emissions-euets.com/tick-size-regime

Or googling by:
    
    "MiFID II tick size regime"

These functions build a price dictionary that will help us obtaining
the corresponding tick size for a product and also obtain a new price based
on a previous price and a number of tick movements. 

"""

import numpy as np

ticks = [0.0001, 0.0001, 0.0001, 0.0001, 0.0002, 0.0005, 0.001, 0.002,
         0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50,
         100, 200, 500,]

units = [4, 4, 4, 4, 4, 4, 3, 3, 3, 2, 2, 2,
         1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,]

band_start = {'1': 5, '2': 4, '3': 3, '4': 2, '5': 1, '6': 0}


def build_prices_dict(band):
    start = band_start[str(band)]
    band_ticks = ticks[start:(19+start)]
    band_units = units[start:(19+start)]
    prices = []
    price_ticks = []
    price = round(0,0)
    
    while price <= 50000:
        
        if (0 <= price) and (price < 0.1):
            pos = 0
        elif (0.1 <= price) and (price < 0.2):
            pos = 1
        elif (0.2 <= price) and (price < 0.5):
            pos = 2
        elif (0.5 <= price) and (price < 1):
            pos = 3
        elif (1 <= price) and (price < 2):
            pos = 4
        elif (2 <= price) and (price < 5):
            pos = 5
        elif (5 <= price) and (price < 10):
            pos = 6
        elif (10 <= price) and (price < 20):
            pos = 7
        elif (20 <= price) and (price < 50):
            pos = 8
        elif (50 <= price) and (price < 100):
            pos = 9
        elif (100 <= price) and (price < 200):
            pos = 10
        elif (200 <= price) and (price < 500):
            pos = 11
        elif (500 <= price) and (price < 1000):
            pos = 12
        elif (1000 <= price) and (price < 2000):
            pos = 13
        elif (2000 <= price) and (price < 5000):
            pos = 14
        elif (5000 <= price) and (price < 10000):
            pos = 15
        elif (10000 <= price) and (price < 20000):
            pos = 16
        elif (20000 <= price) and (price < 50000):
            pos = 17
        elif (50000 <= price):
            pos = 18
        
        tick = round(band_ticks[pos],band_units[pos])
        price_ticks.append([tick, band_units[pos]])
        prices.append(price)
        price = round((price + tick),band_units[pos])
        
    return dict(zip(prices,np.arange(len(prices)))), prices, band_ticks[18]

def get_band_dicts(bands_list):
    
    prices_idx = dict()
    prices = dict()
    max_tick = dict()
    
    for band in bands_list:
        key = f'band{band}'
        band_info = build_prices_dict(band)
        prices_idx[key], prices[key], max_tick[key] = band_info
    return prices_idx, prices, max_tick
