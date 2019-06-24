# PythonMatchingEngine

########## DESCRIPTION #############

Trading Matching Engine / orderbook Simulator using Level 3 orderbook Data 
for realistic simulation of High Frequency Trading Strategies

Orderbook class implements an cash-equity Orderbook 
with price-time priority, FIFO queues in price levels
implemented with doubly linked lists 

In contrast with other python Orderbook implementations found in 
Github like HFT-Orderbook found in:

https://github.com/Crypto-toolbox/HFT-Orderbook

this implementation includes both passive and aggressive orders processing. 
That is, not only orders can be added to the Orderbook but executions 
occur if there is a price match for an incoming order.

If an aggressive order is sent (e.g. a buy order at a limit price higher
than the current best outstanding sell offer in the book) 
orders in the other side of the book (e.g. sell offers for a buy order sent)
will be swept according to their price-time priority and executions
will be stored in orderbook.trades

Class Gateway allows historical orders to be introduced into the Orderbook
in chronological order. It also allows you to send your own orders through it
to the Orderbook simulating the Latency that you would experience in real life.

In order to make the most realistic simulation, your orders will have
market impact and will result in historical prices being introduced at
prices slightly different than they were if you consume most of the
available liquidity. For example, if you buy aggressively the liquidity
in the ask positions, next historical orders will not be introduced
at the same price as they did historically, but at higher prices
reflecting the market impact of your orders.



########## PERFORMANCE #############

Tested with 1 million orders distribuited randomly between buys
and sells and with normal price distributions the time to process them 
all is less than 4 seconds. You can find the test in performance.py

That makes it more than 250.000 processed orders per second.

It could for example simulate the whole trading session 

of the spanish stock exchange in less than 1 minute. 


########## STAND ALONE ORDERBOOK USAGE #############

 Create orderbook

from orderbook import orderbook

orderbook = orderbook()

 Send new order
order_uid = orderbook.send(is_buy=True, qty=100, price=10.002)

 Modify order
orderbook.modif(order_uid, new_is_buy=True, new_qty = 100, new_price=9.9)

 Cancel order
orderbook.cancel(order_uid)

 Check order status
order_data = orderbook.get(order_uid)

 Check orderbook executions
orderbook.trades

 Get best bid
orderbook.bbid

 Get best ask
orderbook.bask

######## USAGE OF THE ORDERBOOK WITH HISTORICAL ORDERS AND LATENCY
######## THROUGH THE GATEWAY CLASS




You can find more examples of usage in the examples folder.

from core.gateway import Gateway

gtw = Gateway(ticker='ana',
            date='2019-05-23',
            latency=20000)


 Market orderbook right after the opening auction
print(gtw.ob)
print(f'orderbook opened at {gtw.ob_time}')

 Move the orderbook 5 minute forward in time
gtw.move_n_seconds(60)

 Check orderbook time
print(f'New orderbook time is {gtw.ob_time}')

 Check new orderbook
print(gtw.ob)

 Get first 3 best bids and asks
gtw.ob.top_bids(3)
gtw.ob.top_asks(3)

 If you don't need the volume, it is faster to ask just for the prices
gtw.ob.top_bidpx(3)
gtw.ob.top_askpx(3)

 The fastest access by far is the best_bid and best_ask
gtw.ob.bbid
gtw.ob.bask

 Check if there were any trades so far
gtw.ob.trades_vol
gtw.ob.trades_px
gtw.ob.trades_time

 Check orderbook cummulative traded volume
gtw.ob.cumvol
 My total traded volume
gtw.ob.my_cumvol

 Check best ask price 
target_price = gtw.ob.bask[0]
print(f'We just saw ask price:{target_price}  \
    that happened at time {gtw.ob}')
 Send an aggressive buy order against this ask price for inmediate execution
 We are actually queuing it with gtw.latency added 
my_uid = gtw.queue_my_new(is_buy=True,
                          qty=10,
                          price=target_price)


 Check order status.
 NOTE: time has not moved yet. Therefore,
 my order is still on the fly, it did not arrive to the orderbook
 If we check its status in the orderbook we will get a KeyError
try:
    gtw.ord_status(my_uid)
except KeyError:
    print(f'The order with uid:{my_uid} did not arrive to the orderbook')

 Advance time 1 second to give the order time to arrive
gtw.move_n_seconds(1)

 Check status again. 
 I was lucky, the price I targeted did not disappear while my order was
 and flying and we got it filled (leavesqty==0) => HIT RATE 100%
 Since it is filled, it is not active anymore (active==False)
try:
    print(gtw.ord_status(my_uid))
except KeyError:
    print(f'The order with uid:{my_uid} did not arrive to the orderbook')

 Check my trades
gtw.ob.my_trades_vol
gtw.ob.my_trades_px    
 As we can see, our execution happened exactly 20 miliseconds after the
 ask price we targeted appeared in the first place. Just as expected. 
gtw.ob.my_trades_time    



 Current orderbook orderbook. The spread is wide, lets close it.
print(gtw.ob)
 Now we are goint to send an order that improves the best bid
 by one tick, closing the orderbook bid-ask spread in one tick
bbid_px = gtw.ob.bbid[0]
imp_bbid = gtw.ob.get_new_price(price=bbid_px, n_moves=1)
my_uid = gtw.queue_my_new(is_buy=True,
                          qty=7,
                          price=imp_bbid)

 Lets move gtw.latency microseconds in time to let our order arrive
gtw.move_n_seconds(gtw.latency/1e6)

 Lets check our order status
gtw.ord_status(my_uid)

 Great, its already active and setting the new best bid
gtw.ob.bbid
 Lets see the new orderbook
print(gtw.ob)

 Allright, I was just bluffing, I do not want to buy => lets cancel it
gtw.queue_my_cancel(my_uid)

 Move forward
gtw.move_n_seconds(gtw.latency/1e6)

 Lets check our order status
gtw.ord_status(my_uid)

 Lets check the book now
print(gtw.ob)



