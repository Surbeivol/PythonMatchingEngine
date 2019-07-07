# PythonMatchingEngine
## Description

Trading Matching Engine / Orderbook / Market Simulator using Level 3 Market Data 
for realistic simulation of High Frequency Trading Strategies.

It has the following features:

* It implements a simple and fast cash-equity orderbook with price-time priority
* Aggressive orders are matched against resting liquidity producing trades and removing liquidity
* MiFID II tick size regime compliant through helper functions
* Real historical orders injection for real historical sessions replay
* Simulation of market data and market access latency effect on your orders


## Performance

In the test folder there is performance.py script that inserts one by one the more
than 275121 orders. This were the real orders introduced in the market for Santander 
during the 2019-05-23 trading session.

It takes around 1.7 seconds to process them all producing around 12k trades. 

## How to use it

Since it is not yet a package you can download with pip, you will need to add 
the root directory of the project to your PYTHONPATH for python to 
recognize the project modules. 

For example, if you are going to use Jupyter, you could do:

``` sh
cd PythonMatchingEngine
export PYTHONPATH=$PYTHONPATH:$(pwd)
jupyter notebook
```

In examples/ you will find several notebooks explaining some basic usage. 

## Implementation

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


### Example

To better ilustrate the building blocks and behaviour of the Orderbook class 
with passive and aggressive orders, we will provide an example and some diagrams.

The following code:

``` python
from core.orderbook import Orderbook
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

![orderbook](https://user-images.githubusercontent.com/1562651/60772186-12895d00-a0f3-11e9-96a5-9c3a26c242ee.png)


If we send an aggressive order to this Orderbook:

``` python 
# This order will sweep all ask positions and lie resting in the bid
# setting a new best bid and leaving the Asks empty
agg_price = ob.get_new_price(10., 4)
ob.send(uid=-8, is_buy=True, qty=200, price = agg_price)
```

The new Orderbook situation would look like this:

![empty_ask_orderbook](https://user-images.githubusercontent.com/1562651/60772190-364ca300-a0f3-11e9-8719-d7dac555d467.png)


That is, all positions in the Ask half orderbook have been swept
and the leaves volume will set the new best bid in the market. 

NOTE: you will probably not want to interact directly with the
Orderbook but instead use the Gateway class as proxy to it,
thus benefiting from the latency simulation and the posibility
to inject historical orders and move the time forward.
