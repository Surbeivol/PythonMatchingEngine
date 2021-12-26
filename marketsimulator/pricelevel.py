from collections import deque

class PriceLevel:
    """ Represents a price in the orderbook with its order queue
    
    """

    def __init__(self, order):
        self.price = order.price
        self.head_order = order
        self.tail_order = order
        self.prev = None
        self.next = None

    # Cummulative volume of all orders at this PriceLevel
    @property
    def vol(self):
        vol = 0
        next_order = self.head_order
        while next_order is not None:
            vol += next_order.leavesqty
            next_order = next_order.next
        return vol

    def is_empty(self):
        return (self.head_order is None)

    def append(self, order):        
        self.tail_order.next = order
        order.prev = self.tail_order
        self.tail_order = order
        
    def pop(self):
        self.head_order.active = False
        if self.head_order.next is None:
            self.head_order = None
            self.tail_order = None
        else:
            self.head_order.next.prev = None
            self.head_order = self.head_order.next

    def remove(self, order):        
        # right side
        if order.next is None:
            self.tail_order = order.prev
            if order is self.head_order:
                self.head_order = None
                self.tail_order = None
            else:
                order.prev.next = None
                # left side
        elif order is self.head_order:
            self.head_order = order.next
            order.next.prev = None
        # middle
        else:
            order.next.prev = order.prev
            order.prev.next = order.next
    


            