from marketsimulator.pricelevel import PriceLevel
from marketsimulator.order import Order

def test_append():
    
    first_order = Order(uid=1, is_buy=True, qty=1, price=5)
    pricelevel = PriceLevel(first_order)

    second_order = Order(uid=2, is_buy=True, qty=1, price=5)
    pricelevel.append(second_order)

    assert pricelevel.head_order is first_order
    assert pricelevel.head_order.next is second_order
    assert pricelevel.tail_order is second_order

def test_vol():
    first_order = Order(uid=1, is_buy=True, qty=1, price=5)
    pricelevel = PriceLevel(first_order)

    second_order = Order(uid=2, is_buy=True, qty=1, price=5)
    pricelevel.append(second_order)

    assert pricelevel.vol == first_order.qty + first_order.qty

def test_remove():
    first_order = Order(uid=1, is_buy=True, qty=1, price=5)
    pricelevel = PriceLevel(first_order)

    second_order = Order(uid=2, is_buy=True, qty=1, price=5)
    pricelevel.append(second_order)

    pricelevel.remove(first_order)
    assert pricelevel.head_order is second_order
