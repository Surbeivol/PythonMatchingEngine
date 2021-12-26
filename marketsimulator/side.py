from abc import ABC, abstractmethod
from .pricelevel import PriceLevel

class Side(ABC):
    """ 
        Represents half of the orderbook, either Bids or Asks.
        Contains common properties and methods for Bids and Asks
    """

    def __init__(self):
        self.book = dict()
        # Pointer to the highest priority PriceLevel
        self.head_pricelevel = None
        # Pointer to the lowest priority PriceLevel
        self.tail_pricelevel = None

    @property
    def best_pricelevel(self):
        return self.head_pricelevel

    @property
    def best_price(self):
        return self.head_pricelevel.price

    @property
    def best_vol(self):
        return self.head_pricelevel.vol
        
    def pricelevel(self, price):
        return self.book[price]

    def add(self, order):
        if order.price in self.book:
            pricelevel = self.book[order.price]
            pricelevel.append(order)
        else:
            pricelevel = self._new_pricelevel(order)
        order.active = True

    def remove_pricelevel(self, price):        
        pricelevel = self.book[price]
        del self.book[price]

        if pricelevel is self.head_pricelevel:
            if self.head_pricelevel is self.tail_pricelevel:
                self.head_pricelevel = None
                self.tail_pricelevel = None
            else:
                pricelevel.next.prev = None
                self.head_pricelevel = pricelevel.next
        elif pricelevel is self.tail_pricelevel:
            pricelevel.prev.next = None
            self.tail_pricelevel = pricelevel.prev
        else:
            pricelevel.prev.next = pricelevel.next
            pricelevel.next.prev = pricelevel.prev

    @abstractmethod
    def price1_has_higher_priority_than_price2(self, price1, price2):
        raise NotImplementedError

    def _new_pricelevel(self, order):
        new_pricelevel = PriceLevel(order)
        if self.head_pricelevel:
            current_pricelevel = self.head_pricelevel
            while(True):
                if self.price1_has_higher_priority_than_price2(
                    price1=current_pricelevel.price, 
                    price2=new_pricelevel.price):
                    if current_pricelevel.next:
                        current_pricelevel = current_pricelevel.next
                    else:
                        #pricelevel to the botton
                        current_pricelevel.next = new_pricelevel
                        new_pricelevel.prev = current_pricelevel
                        self.tail_pricelevel = new_pricelevel
                        break 
                else:
                    #if there is a pricelevel before, place in between
                    if current_pricelevel.prev:
                        current_pricelevel.prev.next = new_pricelevel
                        new_pricelevel.prev = current_pricelevel.prev
                    else: # otherwise, this is new head
                        self.head_pricelevel = new_pricelevel
                    current_pricelevel.prev = new_pricelevel
                    new_pricelevel.next = current_pricelevel                    
                    break
        else:
            self.head_pricelevel = new_pricelevel
            self.tail_pricelevel = new_pricelevel
        self.book[new_pricelevel.price] = new_pricelevel
        return new_pricelevel

    def best_n_prices(self, nlevels):
        best_prices = nlevels * [None]
        cur_pricelevel = self.head_pricelevel
        idx = 0
        while (cur_pricelevel is not None) and (idx < nlevels):
            best_prices[idx] = cur_pricelevel.price
            cur_pricelevel = cur_pricelevel.next
            idx += 1
        return best_prices