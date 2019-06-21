#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 21:34:40 2019

@author: paco
"""
import timeit
import time
import pdb
import numpy as np
from market.gateway import Gateway

"""
 Create a new Gateway instance with Acciona historical orders.
 This creates a new market and fills it with the first orders to 
 reconstruct the orderbook present when the market opened that day.
 The expected total latency is configured to be 2e4microsecs==20ms 
 
"""
gtw = Gateway(ticker='ana',
             year=2019,
             month=5,
             day=21,
             latency=20000)


# Market orderbook right after the opening auction
print(gtw.mkt)
print(f'Market opened at {gtw.mkt_time}')

# Move the market 5 minute forward in time
gtw.move_n_seconds(60)

# Check market time
print(f'New market time is {gtw.mkt_time}')

# Check new orderbook
print(gtw.mkt)

# Get first 3 best bids and asks
gtw.mkt.top_bids(3)
gtw.mkt.top_asks(3)

# If you don't need the volume, it is faster to ask just for the prices
gtw.mkt.top_bidpx(3)
gtw.mkt.top_askpx(3)

# The fastest access by far is the best_bid and best_ask
gtw.mkt.bbid
gtw.mkt.bask

# Check if there were any trades so far
gtw.mkt.trades_vol
gtw.mkt.trades_px
gtw.mkt.trades_time

# Check market cummulative traded volume
gtw.mkt.cumvol
# My total traded volume
gtw.mkt.my_cumvol

# =============================================================================
# EXPERIENCING LATENCY
# =============================================================================

# Check best ask price 
target_price = gtw.mkt.bask[0]
print(f'We just saw ask price:{target_price}  \
    that happened at time {gtw.mkt_time}')
# Send an aggressive buy order against this ask price for inmediate execution
# We are actually queuing it with gtw.latency added 
my_uid = gtw.queue_my_new(is_buy=True,
                          qty=10,
                          price=target_price)


# Check order status.
# NOTE: time has not moved yet. Therefore,
# my order is still on the fly, it did not arrive to the market
# If we check its status in the market we will get a KeyError
try:
    gtw.ord_status(my_uid)
except KeyError:
    print(f'The order with uid:{my_uid} did not arrive to the market')

# Advance time 1 second to give the order time to arrive
gtw.move_n_seconds(1)

# Check status again. 
# I was lucky, the price I targeted did not disappear while my order was
# and flying and we got it filled (leavesqty==0) => HIT RATE 100%
# Since it is filled, it is not active anymore (active==False)
try:
    print(gtw.ord_status(my_uid))
except KeyError:
    print(f'The order with uid:{my_uid} did not arrive to the market')

# Check my trades
gtw.mkt.my_trades_vol
gtw.mkt.my_trades_px    
# As we can see, our execution happened exactly 20 miliseconds after the
# ask price we targeted appeared in the first place. Just as expected. 
gtw.mkt.my_trades_time    

# =============================================================================
# USING RELATIVE PRICING - PEGGING
# =============================================================================

# Current market orderbook. The spread is wide, lets close it.
print(gtw.mkt)
# Now we are goint to send an order that improves the best bid
# by one tick, closing the market bid-ask spread in one tick
bbid_px = gtw.mkt.bbid[0]
imp_bbid = gtw.mkt.get_new_price(price=bbid_px, n_moves=1)
my_uid = gtw.queue_my_new(is_buy=True,
                          qty=7,
                          price=imp_bbid)

# Lets move gtw.latency microseconds in time to let our order arrive
gtw.move_n_seconds(gtw.latency/1e6)

# Lets check our order status
gtw.ord_status(my_uid)

# Great, its already active and setting the new best bid
gtw.mkt.bbid
# Lets see the new orderbook
print(gtw.mkt)

# Allright, I was just bluffing, I do not want to buy => lets cancel it
gtw.queue_my_cancel(my_uid)

# Move forward
gtw.move_n_seconds(gtw.latency/1e6)

# Lets check our order status
gtw.ord_status(my_uid)

# Lets check the book now
print(gtw.mkt)




    

    