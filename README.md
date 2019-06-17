# PythonMatchingEngine

########## DESCRIPTION #############

Trading Matching Engine / Market Simulator using Level 3 Market Data 
for realistic simulation of High Frequency Trading Strategies

Minimalistic functionality for very high performance

Orderbook with price-time priority, FIFO queues in price levels
implemented with doubly linked lists 

In contrast with other python Orderbook implementations found in 
Github like HFT-Orderbook found in:

https://github.com/Crypto-toolbox/HFT-Orderbook

this implementation includes both passive and aggressive orders processing. 
That is, not only orders can be added to the Book but executions 
occur if there is a price match for an incoming order.

If an aggressive order is sent (e.g. a buy order at a limit price higher
than the current best outstanding sell offer in the book) 
orders in the other side of the book (e.g. sell offers for a buy order sent)
will be swept according to their price-time priority and executions
will be stored in Market.trades

We did not implement a Binary Seach Tree for PriceLevels and instead used
a dictiorany of pointers since for cash-equity applications you 
usually just see the fist 20 prices of the book and you don't end up
having thousands of different prices in the book, but usually hundreds 
at most. 


########## PERFORMANCE #############

Tested with 1 million orders distribuited randomly between buys
and sells and with normal price distributions the time to process them 
all is less than 4 seconds. You can find the test in performance.py

That makes it more than 250.000 processed orders per second.

It could for example simulate the whole trading session of the mostLeave a comment

liquid stocks of the spanish stock exchange in less than 1 minute. 


########## USAGE #############

# Create market

from market import Market

market = Market()

# Send new order
order_uid = market.send(is_buy=True, qty=100, price=10.002)

# Modify order
market.modif(order_uid, new_is_buy=True, new_qty = 100, new_price=9.9)

# Cancel order
market.cancel(order_uid)

# Check order status
order_data = market.get(order_uid)

# Check market executions
market.trades

# Get best bid
market.bbid

# Get best ask
market.bask






