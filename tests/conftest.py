from collections import namedtuple
import pytest
from core.orderbook import Orderbook

@pytest.fixture
def bid1():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o1 = order(is_buy=True, qty=100, price=0.2, uid=1)
    return o1

@pytest.fixture
def bid2():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o2 = order(is_buy=True, qty=200, price=0.2, uid=2)
    return o2

@pytest.fixture
def bid3():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o3 = order(is_buy=True, qty=300, price=0.19, uid=3)
    return o3

@pytest.fixture
def bid4():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o4 = order(is_buy=True, qty=400, price=0.19, uid=4)
    return o4

@pytest.fixture
def bid5():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o5 = order(is_buy=True, qty=500, price=0.18, uid=5)
    return o5

@pytest.fixture
def ask1():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o6 = order(is_buy=False, qty=600, price=0.3, uid=6)
    return o6

@pytest.fixture
def ask2():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o7 = order(is_buy=False, qty=700, price=0.3, uid=7)
    return o7

@pytest.fixture
def ask3():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o8 = order(is_buy=False, qty=800, price=0.31, uid=8)
    return o8

@pytest.fixture
def ask4():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o9 = order(is_buy=False, qty=900, price=0.31, uid=9)
    return o9

@pytest.fixture
def ask5():
    order = namedtuple('Order', 'is_buy, qty, price, uid')
    o10 = order(is_buy=False, qty=1000, price=0.32, uid=10)
    return o10

@pytest.fixture
def bid_lmt_orders(bid1, bid2, bid3, bid4, bid5):
    return [bid1, bid2, bid3, bid4, bid5]

@pytest.fixture
def ask_lmt_orders(ask1, ask2, ask3, ask4, ask5):
    return [ask1, ask2, ask3, ask4, ask5]

@pytest.fixture()
def bid_orderbook(bid_lmt_orders):
    orderbook = Orderbook('san')
    for order in bid_lmt_orders:
        orderbook.send(*order)
    return orderbook

@pytest.fixture()
def ask_orderbook(ask_lmt_orders):
    orderbook = Orderbook('san')
    for order in ask_lmt_orders:
        orderbook.send(*order)
    return orderbook

@pytest.fixture()
def full_orderbook(bid_orderbook, ask_lmt_orders):
    orderbook = bid_orderbook
    for order in ask_lmt_orders:
        orderbook.send(*order)
    return orderbook
