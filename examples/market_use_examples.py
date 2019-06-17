# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 17:26:49 2019

@author: fmerlos
"""

from market.market import Market

# initialize an empty market book for Santander shares (san)
mkt = Market(ticker='san')

# Not all prices are allowed. Check MiFID II tick-size regime
# Move n ticks from one price
mkt.get_new_price(price=10, n_moves=1)
mkt.get_new_price(price=10, n_moves=-1)

# fill with different passive orders
mkt.send(uid=-1, is_buy=True, qty=100, price=10.)
mkt.send(uid=-2, is_buy=True, qty=80, price=10.)
mkt.send(uid=-3, is_buy=True, qty=90, price=10.)
mkt.send(uid=-4, is_buy=True, qty=70, price=mkt.get_new_price(10., -1))
mkt.send(uid=-5, is_buy=False, qty=60, price=mkt.get_new_price(10., 2))
mkt.send(uid=-6, is_buy=False, qty=30, price=mkt.get_new_price(10., 1))
mkt.send(uid=-7, is_buy=False, qty=50, price=mkt.get_new_price(10., 1))

# Show current market orderbook
print(mkt)

# Show book dictionary of LevelPrices 
mkt._bids.book
mkt._asks.book

# Get best bid
mkt.bbid
# Get best ask
mkt.bask

# This order will sweep all ask positions and lie resting in the bid
# setting a new best bid and leaving the Asks empty
agg_price = mkt.get_new_price(10., 4)
mkt.send(uid=-8, is_buy=True, qty=200, price = agg_price)

print(mkt)
print(mkt.bbid)
print(mkt.bask)

# Check that the trades happened in the oder corresponding 
# to their price-time priority
mkt.trades.keys()
mkt.trades['price'][:5]
mkt.trades['vol'][:5]
mkt.trades['pas_ord'][:5]


# =============================================================================
# USEFULL FUNCTIONS
# =============================================================================
