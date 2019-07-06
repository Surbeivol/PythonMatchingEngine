# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 17:26:49 2019

@author: fmerlos
"""
from core.orderbook import Orderbook

# initialize an empty orderbook book for Santander shares (san)
ob = Orderbook(ticker='san')

# Not all prices are allowed. Check MiFID II tick-size regime
# Move n ticks from one price
ob.get_new_price(price=10, n_moves=1)
ob.get_new_price(price=10, n_moves=-1)

# fill with different passive orders
ob.send(uid=-1, is_buy=True, qty=100, price=10.)
ob.send(uid=-2, is_buy=True, qty=80, price=10.)
ob.send(uid=-3, is_buy=True, qty=90, price=10.)
ob.send(uid=-4, is_buy=True, qty=70, price=ob.get_new_price(10., -1))
ob.send(uid=-5, is_buy=False, qty=60, price=ob.get_new_price(10., 2))
ob.send(uid=-6, is_buy=False, qty=30, price=ob.get_new_price(10., 1))
ob.send(uid=-7, is_buy=False, qty=50, price=ob.get_new_price(10., 1))

# Show current orderbook
print(ob)

# Show book dictionary of LevelPrices 
ob._bids.book
ob._asks.book

# Get best bid
ob.bbid
# Get best ask
ob.bask

# This order will sweep all ask positions and lie resting in the bid
# setting a new best bid and leaving the Asks empty
agg_price = ob.get_new_price(10., 4)
ob.send(uid=-8, is_buy=True, qty=200, price = agg_price)

print(ob)
print(ob.bbid)
print(ob.bask)

# Check that the trades happened in the oder corresponding 
# to their price-time priority
ob.trades.keys()
ob.trades['price'][:5]
ob.trades['vol'][:5]
ob.trades['pas_ord'][:5]


# =============================================================================
# USEFULL FUNCTIONS
# =============================================================================
