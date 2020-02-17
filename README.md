# PythonMatchingEngine
## Description

Trading Matching Engine / Orderbook / Market Simulator using Level 3 Market Data 
for realistic simulation of High Frequency Trading Strategies.

It has the following features:

* It implements a simple and fast cash-equity orderbook with price-time priority
* Aggressive orders are matched against resting liquidity producing trades and removing liquidity
* MiFID II tick-size regime compliant through helper functions
* Real historical orders injection for real historical sessions replay
* Simulation of market data and market access latency effect on your orders


## Performance

In the test folder there is performance.py script that inserts one by one the more
than 275,121 orders. This were the real orders introduced in the market for Santander 
during the 2019-05-23 trading session.

It takes around 1.7 seconds to process them, that is around 150k orders 
per second. This makes this orderbook suitable for long tick by tick
 algorithmic trading simulations.

## How to use it
From the root folder:

``` sh
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r dockerfiles/requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)
jupyter notebook
```

In examples/ you will find several notebooks explaining some basic usage. 

# Orderbook 

Orderbook class implements an cash-equity Orderbook 
with price-time priority, FIFO queues in price levels
implemented with doubly linked lists.

This implementation includes both passive and aggressive orders processing. 
That is, not only orders can be added to the Orderbook but executions 
occur if there is a price match for an incoming order.

If an aggressive order is sent (e.g. a buy order at a limit price higher
than the current best outstanding sell offer in the book) 
orders in the other side of the book (e.g. sell offers for a buy order sent)
will be swept according to their price-time priority and executions
will be stored in orderbook.trades

To better ilustrate the building blocks and behaviour of the Orderbook class 
with passive and aggressive orders, we will provide an example and some diagrams.

The following code:

``` python
from marketsimulator.orderbook import Orderbook
# initialize an empty orderbook book for Santander shares (san)
ob = Orderbook(ticker='san')
# fill with different passive orders
ob.send(uid=-1, is_buy=True, qty=100, price=10.)
ob.send(uid=-2, is_buy=True, qty=80, price=10.)
ob.send(uid=-3, is_buy=True, qty=90, price=10.)
ob.send(uid=-4, is_buy=True, qty=70, price=ob.get_new_price(10., -1))
ob.send(uid=-5, is_buy=False, qty=60, price=ob.get_new_price(10., 2))
ob.send(uid=-6, is_buy=False, qty=30, price=ob.get_new_price(10., 1))
ob.send(uid=-7, is_buy=False, qty=50, price=ob.get_new_price(10., 1))
```

Will produce this Orderbook structure:

![full_book](https://user-images.githubusercontent.com/1562651/60772264-0fdb3780-a0f4-11e9-881e-0115012ce00a.png)


If we send an aggressive order to this Orderbook:

``` python 
# This order will sweep all ask positions and lie resting in the bid
# setting a new best bid and leaving the Asks empty
>>> agg_price = ob.get_new_price(10., 4)
>>> ob.send(uid=-8, is_buy=True, qty=200, price = agg_price)
# Resulting trades from aggressive order
>>> ob.trades_vol
array([30., 50., 60.])
>>> ob.trades_px
array([10.002, 10.002, 10.004])
# New best bid
>>> ob.bbid
(10.008, 60)
# New best ask
>>> ob.bask is None
True
```

The new Orderbook situation would look like this:

![empty_ask_orderbook](https://user-images.githubusercontent.com/1562651/60772267-1bc6f980-a0f4-11e9-9631-0f7f3b46ae55.png)


That is, all positions in the Ask half orderbook have been swept
and the leaves volume will set the new best bid in the market. 

You can check examples of usage in ./examples 

NOTES: 

Use positive integers for the uids when sending historical orders
to the Oderbook and negative integers when sending your own orders.
This way Orderbook class will be able to keep track of your vwap 
or cumvol against market vwap or cumvol.

You will probably not want to interact directly with the
Orderbook but instead use the Gateway class as proxy to it,
thus benefiting from the latency simulation and the posibility
to inject historical orders and move the time forward.

# Gateway


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

The following diagram describes the meaning of the latency parameter
of class Gateway:

![latency_diagram](https://user-images.githubusercontent.com/1562651/60772188-2765f080-a0f3-11e9-9b4a-3e974eab72b6.png)

## Using Orderbook through the Gateway class

Create a new Gateway instance with Santander historical orders.
This creates a new orderbook and fills it with the first orders to 
reconstruct the orderbook present when the orderbook opened that day.

It is like market replay of what happened that day and you can mix your own
orders in between.

The class Gateway instanciates an Orderbook object  
and provides methods to move the historical 
replay forward tick by tick or a number of seconds 

The expected total latency is configured to be 20,000 microseconds == 20ms


```
import datetime
import numpy as np
from marketsimulator.gateway import Gateway

gtw = Gateway(ticker='san',
             date=datetime.date(2019,5,23),
             start_h=9,
             end_h=10,
             latency=20_000)

# Market orderbook right after the opening auction
print(f'orderbook opened at {gtw.ob_time} \n')

orderbook opened at 2019-05-23 09:00:31.127000 

# Market Orderbook is initialized so that it shows the orderbook 
# that was present right after the opening auction took place
print(gtw.ob)

     vbid    pbid    pask   vask
0   12682  4.0255  4.0265   6907
1    6896  4.0250  4.0275   4000
2    2500  4.0240  4.0285   6907
3    1355  4.0230  4.0310  12992
4   17850  4.0210  4.0340  72965
5    7000  4.0205  4.0365  16625
6  104505  4.0200  4.0390    999
7     248  4.0190  4.0400  32265
8    5000  4.0170  4.0410  13442
9      60  4.0160  4.0450  15550

```

We can move the market tick by tick or n seconds forward in time:

```
# Move the orderbook 1 minute forward in time
gtw.move_n_seconds(60)
# Check orderbook time
print(f'New orderbook time is {gtw.ob_time} \n')

New orderbook time is 2019-05-23 09:01:31.127000 

# Check new orderbook
print(gtw.ob)

    vbid    pbid    pask   vask
0   1187  4.0165  4.0200   4491
1   2500  4.0160  4.0210   5219
2  25000  4.0150  4.0220   2719
3   5219  4.0135  4.0230   5219
4    500  4.0130  4.0240   4691
5   2719  4.0125  4.0250   5219
6   8300  4.0120  4.0260   2666
7   5219  4.0115  4.0265    253
8  21189  4.0110  4.0270  12666
9   8214  4.0105  4.0275   5491
```

We can also send our orders to the Orderbook using the Gateway
as a proxy. This will have the effect of simulating the latency 
of your orders before reaching the market (20 ms in this example)

```
# Check best ask price to set as our target price
target_price = gtw.ob.bask[0]
mkt_time_when_target_px_showed = gtw.ob_time
print(f'We just saw ask price:{target_price}'  \
        f' that happened at time {mkt_time_when_target_px_showed}')

 We just saw ask price:4.02 that happened at time 2019-05-23 09:01:31.127000

# Send an aggressive buy order against this ask price for inmediate execution
# We are actually queuing it with gtw.latency added 
my_uid = gtw.queue_my_new(is_buy=True,
                          qty=10000,
                          price=target_price)


# Check order status.
# NOTE: time has not moved yet. Therefore,
# my order is still on the fly, it did not arrive to the orderbook
# If we check its status in the orderbook we will get a KeyError
try:
    gtw.ord_status(my_uid)
except KeyError:
    print(f'The order with uid:{my_uid} did not arrive to the orderbook')

 The order with uid:-1 did not arrive to the orderbook

 # Advance time 1 second to give the order time to arrive
gtw.move_n_seconds(1)

# Check status again. 
# I was lucky, the price I targeted did not disappear while my order was
# and flying and we got it filled (leavesqty==0) => HIT RATE 100%
# Since it is filled, it is not active anymore (active==False)
try:
    print(gtw.ord_status(my_uid))
except KeyError:
    print(f'The order with uid:{my_uid} did not arrive to the orderbook')

{'uid': -1, 'is_buy': True, 'qty': 10, 'cumqty': 10, 'leavesqty': 0, 'price': 4.02, 'timestamp': Timestamp('2019-05-23 09:01:31.147000'), 'active': False}

# Check my trades
print(gtw.ob.my_trades_vol)
print(gtw.ob.my_trades_px)

# As we can see, our execution happened exactly 20 miliseconds after the
# ask price we targeted appeared in the first place. Just as expected. 
print(gtw.ob.my_trades_time)
print('')
print('Our execution was done 20 ms after the price first showed')
print(gtw.ob.my_trades_time[0]-mkt_time_when_target_px_showed)

[10.]
[4.02]
[Timestamp('2019-05-23 09:01:31.147000')]

Our execution was done 20 ms after the price first showed
0 days 00:00:00.020000
```

Please check jupyter notebooks in ./examples for more examples of how to use it
