#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Created on Thu May 30 08:21:48 2019

@author: paco
"""
from marketsimulator.orderbook import Orderbook
from marketsimulator.gateway import Gateway
import numpy as np 
import matplotlib.pyplot as plt
import time
from datetime import datetime
import pandas as pd
import pdb


# Test with file data/orders-san-2019-5-23.csv
# containing 275_121 orders, modifications or cancelations in a single day

session = datetime.strptime('2019-05-23', '%Y-%m-%d').date()

gtw = Gateway(ticker='san',
             date=session,
             latency=20_000)

num_ords = len(gtw.hist_orders)

t = time.time()
while(gtw.ob_time < gtw.end_time):
    gtw.tick()
print(f'Time to process the whole real trading session \n \
        with {num_ords} real orders: {time.time()-t}')

plt.figure(figsize=(20,10))
plt.title(f'Last px of the {len(gtw.ob.trades_px)} trades ' \
            f'resulting of the matching of the {num_ords} orders')
plt.plot(gtw.ob.trades_time, gtw.ob.trades_px)
plt.show()
