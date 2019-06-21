#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 12:59:42 2019

@author: paco
"""
import sys
import os
import time
import numpy as np
from market.gateway import Gateway
from examples.algorithms import BuyTheBid, SimplePOV
from datetime import datetime
sys.path.append(os.getcwd())
sys.path.append('../')

# =============================================================================
# TEST BUY THE BID ALGO
# =============================================================================

gtw_kwargs = {
    'date': datetime(2019, 5, 21).date(),
    'ticker': 'ana',
    'start_h': 9,
    'end_h': 17.5,
    'latency': 20000,
}

gtw = Gateway(**gtw_kwargs)
    
btb = BuyTheBid(1000000, 1)

t = time.time()
while (not btb.done) and (gtw.mkt_time < gtw.end_time):        
    
    btb.eval_and_act(gtw)
    gtw.tick()
    
print(time.time()-t)

# =============================================================================
# TEST SIMPLE POV ALGO
# =============================================================================

gtw_kwargs = {
    'date': datetime(2019, 5, 23).date(),
    'ticker': 'san',
    'start_h': 9,
    'end_h': 17.5,
    'latency': 20000,
}

algo_kwargs = {
    'is_buy': True,
    'target_pov': 0.2,
    'lmtpx': np.Inf,
    'qty': int(1e7),
    'sweep_max': 1,
    'min_vol': 200,
    'n_seconds': 1,
}

gtw = Gateway(**gtw_kwargs)

pov_algo = SimplePOV(**dict(gtw_kwargs, **algo_kwargs))

t = time.time()

while (not pov_algo.done) and (gtw.mkt_time < gtw.end_time):        
    pov_algo.eval_and_act(gtw)

print(time.time()-t)
