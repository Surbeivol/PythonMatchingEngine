from marketsimulator.asks import Asks
from marketsimulator.order import Order


def test_add_order():
    asks = Asks()
    first_order = Order(uid=1, is_buy=False, qty=1, price=5)
    asks.add(first_order)

    assert asks.head_pricelevel.head_order is first_order

    lower_priority_order = Order(uid=2, is_buy=False, qty=1, price=7)
    asks.add(lower_priority_order)

    assert asks.head_pricelevel.head_order is first_order
    assert asks.tail_pricelevel.head_order is lower_priority_order

    highest_priority_order = Order(uid=3, is_buy=False, qty=1, price=1)
    asks.add(highest_priority_order)

    assert asks.head_pricelevel.head_order is highest_priority_order
    assert asks.tail_pricelevel.head_order is lower_priority_order

    order_between_highest_and_first = Order(uid=4, is_buy=False, qty=1, price=3)
    asks.add(order_between_highest_and_first)

    assert asks.head_pricelevel.head_order is highest_priority_order
    assert asks.head_pricelevel.next.head_order is order_between_highest_and_first
    assert asks.head_pricelevel.next.next.head_order is first_order
    assert asks.tail_pricelevel.tail_order is lower_priority_order

    order_between_first_and_lower = Order(uid=5, is_buy=False, qty=1, price=6)
    asks.add(order_between_first_and_lower)

    assert asks.head_pricelevel.head_order is highest_priority_order
    assert asks.head_pricelevel.next.head_order is order_between_highest_and_first
    assert asks.head_pricelevel.next.next.head_order is first_order       
    assert asks.tail_pricelevel.tail_order is lower_priority_order
    assert asks.tail_pricelevel.prev.tail_order is order_between_first_and_lower

def test_add_order_start_with_highest_priority():

    asks = Asks()
    first_order = Order(uid=1, is_buy=False, qty=1, price=5)
    asks.add(first_order)

    highest_priority_order = Order(uid=3, is_buy=False, qty=1, price=1)
    asks.add(highest_priority_order)

    assert asks.head_pricelevel.head_order is highest_priority_order
    assert asks.tail_pricelevel.head_order is first_order

def test_remove():

    asks = Asks()
    
    highest_priority_order = Order(uid=1, is_buy=True, qty=1, price=1)
    asks.add(highest_priority_order)
    
    order_between_highest_and_first = Order(uid=2, is_buy=True, qty=1, price=2)
    asks.add(order_between_highest_and_first)

    first_order = Order(uid=3, is_buy=True, qty=1, price=3)
    asks.add(first_order)

    order_between_first_and_lower = Order(uid=4, is_buy=True, qty=1, price=4)
    asks.add(order_between_first_and_lower)

    lower_priority_order = Order(uid=5, is_buy=True, qty=1, price=5)
    asks.add(lower_priority_order)    

    asks.remove_pricelevel(highest_priority_order.price)
    assert asks.head_pricelevel.head_order is order_between_highest_and_first
    assert asks.head_pricelevel.next.head_order is first_order

    asks.remove_pricelevel(first_order.price)
    assert asks.head_pricelevel.head_order is order_between_highest_and_first
    assert asks.head_pricelevel.next.head_order is order_between_first_and_lower

    asks.remove_pricelevel(lower_priority_order.price)
    assert asks.tail_pricelevel.head_order is order_between_first_and_lower

    asks.remove_pricelevel(order_between_first_and_lower.price)
    assert asks.head_pricelevel.head_order is order_between_highest_and_first
    assert asks.head_pricelevel is asks.tail_pricelevel

    asks.remove_pricelevel(order_between_highest_and_first.price)
    assert asks.head_pricelevel is None
    assert asks.tail_pricelevel is None
    




    




