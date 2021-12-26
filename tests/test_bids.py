from marketsimulator.bids import Bids
from marketsimulator.order import Order


def test_add_order():
    bids = Bids()
    first_order = Order(uid=1, is_buy=True, qty=1, price=5)
    bids.add(first_order)

    assert bids.head_pricelevel.head_order is first_order

    lower_priority_order = Order(uid=2, is_buy=True, qty=1, price=3)
    bids.add(lower_priority_order)

    assert bids.head_pricelevel.head_order is first_order
    assert bids.tail_pricelevel.head_order is lower_priority_order

    highest_priority_order = Order(uid=3, is_buy=True, qty=1, price=10)
    bids.add(highest_priority_order)

    assert bids.head_pricelevel.head_order is highest_priority_order
    assert bids.tail_pricelevel.head_order is lower_priority_order

    order_between_highest_and_first = Order(uid=4, is_buy=True, qty=1, price=7)
    bids.add(order_between_highest_and_first)

    assert bids.head_pricelevel.head_order is highest_priority_order
    assert bids.head_pricelevel.next.head_order is order_between_highest_and_first
    assert bids.head_pricelevel.next.next.head_order is first_order
    assert bids.tail_pricelevel.tail_order is lower_priority_order

    order_between_first_and_lower = Order(uid=5, is_buy=True, qty=1, price=4)
    bids.add(order_between_first_and_lower)

    assert bids.head_pricelevel.head_order is highest_priority_order
    assert bids.head_pricelevel.next.head_order is order_between_highest_and_first
    assert bids.head_pricelevel.next.next.head_order is first_order       
    assert bids.tail_pricelevel.tail_order is lower_priority_order
    assert bids.tail_pricelevel.prev.tail_order is order_between_first_and_lower

def test_add_order_start_with_highest_priority():

    bids = Bids()
    first_order = Order(uid=1, is_buy=True, qty=1, price=5)
    bids.add(first_order)

    highest_priority_order = Order(uid=3, is_buy=True, qty=1, price=10)
    bids.add(highest_priority_order)

    assert bids.head_pricelevel.head_order is highest_priority_order
    assert bids.tail_pricelevel.head_order is first_order
    
def test_remove():

    bids = Bids()
    
    highest_priority_order = Order(uid=1, is_buy=True, qty=1, price=10)
    bids.add(highest_priority_order)
    
    order_between_highest_and_first = Order(uid=2, is_buy=True, qty=1, price=7)
    bids.add(order_between_highest_and_first)

    first_order = Order(uid=3, is_buy=True, qty=1, price=5)
    bids.add(first_order)

    order_between_first_and_lower = Order(uid=4, is_buy=True, qty=1, price=4)
    bids.add(order_between_first_and_lower)

    lower_priority_order = Order(uid=5, is_buy=True, qty=1, price=3)
    bids.add(lower_priority_order)    

    bids.remove_pricelevel(highest_priority_order.price)
    assert bids.head_pricelevel.head_order is order_between_highest_and_first
    assert bids.head_pricelevel.next.head_order is first_order

    bids.remove_pricelevel(first_order.price)
    assert bids.head_pricelevel.head_order is order_between_highest_and_first
    assert bids.head_pricelevel.next.head_order is order_between_first_and_lower

    bids.remove_pricelevel(lower_priority_order.price)
    assert bids.tail_pricelevel.head_order is order_between_first_and_lower

    bids.remove_pricelevel(order_between_first_and_lower.price)
    assert bids.head_pricelevel.head_order is order_between_highest_and_first
    assert bids.head_pricelevel is bids.tail_pricelevel

    bids.remove_pricelevel(order_between_highest_and_first.price)
    assert bids.head_pricelevel is None
    assert bids.tail_pricelevel is None



    




