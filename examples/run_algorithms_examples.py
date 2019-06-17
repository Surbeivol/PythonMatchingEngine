#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 12:59:42 2019

@author: paco
"""

import time
import pdb
import numpy as np
from market.gateway import Gateway
from examples.algorithms import BuyTheBid, SimplePOV
      


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
while (not btb.done) and (gtw.mkt_idx < gtw.mkt_nord-1):        
    btb.eval_and_act(gtw)
    gtw.tick()
    
print(time.time()-t)



# =============================================================================
# TEST SIMPLE POV ALGO
# =============================================================================

gtw = Gateway(ticker='san',
             year=2019,
             month=5,
             day=23,
             latency=20000)
    

pov_algo = SimplePOV(is_buy=True, target_pov=0.2, lmtpx=np.Inf,
                       qty=int(1e7), sweep_max=5)

t = time.time()
while (not pov_algo.done) and (gtw.mkt_idx < gtw.mkt_nord-1):        
    pov_algo.eval_and_act(gtw)
    gtw.tick()    
print(time.time()-t)

