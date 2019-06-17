# -*- coding: utf-8 -*-
"""
Created on Thu May 16 14:14:51 2019

@author: Francisco Merlos
"""
from abc import ABC, abstractmethod
import time 
import numpy as np

class Market():

    def __init__(self):
        self._bids = Bids()
        self._asks = Asks()
        self.trades = []
        # keeps track of all orders sent to the market
        # allows fast access of orders status by uid
        self._orders = dict()        
        self.last_uid = 0 

    # Best Bid    
    @property    
    def bbid(self):
        if self._bids.best is None:
            return None
        else:
            return self._bids.best.price, self._bids.best.vol
    
    # Best ask
    @property
    def bask(self):
        if self._asks.best is None:
            return None
        else:
            return self._asks.best.price, self._asks.best.vol
    
    
    def get(self, uid):
        """  Get market order by uid
            
            Params:
                uid (int): unique identifier of the Order
        
            Returns:
                order (Order): a copy of the order identified by this uid
        
        """
        order = self._orders[uid]
        return {'uid':order.uid,
                'is_buy':order.is_buy,                
                'qty':order.qty,
                'leavesqty':order.leavesqty,
                'price':order.price,
                'timestamp':order.timestamp,
                'active':order.active}
    
    
    def send(self, is_buy, qty, price, uid=None,
             timestamp = time.time()):
        """ Send new order to market
            Passive orders can't be matched and will be added to the book
            Aggressive orders are matched against opp. side's resting orders
            
            Params:
                is_buy (bool): True if it is a buy order
                qty (int): initial quantity or size of the order 
                price (float): limit price of the order
                timestamp (float): time of processing 
                
            Returns:
                self.last_uid (int): order unique id set by the market 
        """
        if uid is None:
            self.last_uid += 1 
            uid = self.last_uid
        neword = Order(self.last_uid, is_buy, qty, price, timestamp)
        self._orders.update({self.last_uid:neword})
        while (neword.leavesqty > 0):
            if self._is_aggressive(neword):            
                self._sweep_best_price(neword)    
            else:
                if is_buy:
                    self._bids.add(neword)            
                else:
                    self._asks.add(neword)            
                return uid
    
    def cancel(self, uid): 
        """ Cancel order identified by its uid
        
        """
        order = self._orders[uid]
        if order.is_buy:
            pricelevel = self._bids.book[order.price]
        else:
            pricelevel = self._asks.book[order.price]
    
        # right side
        if order.next is None:
            pricelevel.tail = order.prev
            if order is pricelevel.head:
                self._remove_price(order.is_buy, order.price)                
            else:
                order.prev.next = None        
        # left side
        elif order is pricelevel.head:
            pricelevel.head = order.next
            order.next.prev = None
        # middle
        else:
            order.next.prev = order.prev
            order.prev.next = order.next            

        order.leavesqty = 0 
        order.active = False
        return
    
    
    def modif(self, uid, new_is_buy, new_qty, new_price):
        """ Currently modif is cancel + send 
        
        """
        prev_ord = self._orders[uid]
        if new_qty < prev_ord.leaves and new_price == prev_ord.price :
            ## modification without loosing priority
            prev_ord.qty=new_qty
        else:            
            ## modif implies go to to the end of the queue
            raise ValueError("We did not expect this to happen")
            self.cancel(uid)
            self.send(is_buy=new_is_buy,
                      qty=new_qty,
                      price=new_price,
                      uid=uid)        
    

    def _is_aggressive(self, Order):
        is_agg = True
        if Order.is_buy:
            if self._asks.best is None or self._asks.best.price > Order.price:
                is_agg = False
        else:
            if self._bids.best is None or self._bids.best.price < Order.price:
                is_agg = False
        return is_agg 
    
    
    def _sweep_best_price(self, Order):        
        if Order.is_buy:            
            best = self._asks.best
        else:
            best = self._bids.best        
        while(Order.leavesqty > 0):
            if best.head.leavesqty <= Order.leavesqty:                
                trdqty = best.head.leavesqty
                best.head.leavesqty = 0
                self.trades.append([best.price, trdqty])
                best.pop()                
                Order.leavesqty -= trdqty
                if best.head is None:
                    # remove PriceLevel from the order's opposite side
                    self._remove_price(not Order.is_buy, best.price)
                    break
            else:
                self.trades.append([best.price, Order.leavesqty])
                best.head.leavesqty -= Order.leavesqty
                Order.leavesqty = 0
        
        
    def _remove_price(self, is_buy, price):
        if is_buy:
            del self._bids.book[price]
            if len(self._bids.book)>0:
                self._bids.best = self._bids.book[max(self._bids.book.keys())]
            else:
                self._bids.best = None
        else:
            del self._asks.book[price]
            if len(self._asks.book)>0:
                self._asks.best = self._asks.book[min(self._asks.book.keys())]
            else:
                self._asks.best = None
        
        
    def top_bids(self, nlevels):
        """ Returns the first nlevels best bids of the book
        
        """
        prices = np.fromiter(self._bids.book.keys(), float)
        pbids = np.full(nlevels, np.nan)
        vbids = np.full(nlevels, np.nan)
        for i in range(min(nlevels, len(prices))):
            maxidx = np.argmax(prices)
            maxpx = prices[maxidx]
            if maxpx is -np.inf:
                break
            pbids[i] = maxpx
            vbids[i] = self._bids.book[maxpx].vol
            prices[maxidx] = -np.inf        
        return [pbids, vbids]        
       
        
    def top_asks(self, nlevels):
        """ Returns the first nlevels best asks of the book
        
        """
        prices = np.fromiter(self._asks.book.keys(), float)
        pasks = np.full(nlevels, np.nan)
        vasks = np.full(nlevels, np.nan)
        for i in range(min(nlevels, len(prices))):
            maxidx = np.argmin(prices)
            maxpx = prices[maxidx]
            if maxpx is np.inf:
                break
            pasks[i] = maxpx
            vasks[i] = self._asks.book[maxpx].vol
            prices[maxidx] = np.inf        
        return [pasks, vasks]                           
    
            
class Order():
    """ Represents an order inside the market with its current status 
    
    """
    #__slots__ = ["uid", "is_buy", "qty", "price", "timestamp", "status"]        
    
    def __init__(self, uid, is_buy, qty, price, timestamp = time.time()):
        self.uid = uid
        self.is_buy = is_buy
        self.qty = qty
        # outstanding volume in market. If filled or canceled => 0. 
        self.leavesqty = qty
        self.price = price
        self.timestamp = timestamp  
        # is the order active and resting in the orderbook?
        self.active = False         
        # DDL attributes import unittest
        self.prev = None
        self.next = None
    
class PriceLevel():
    """ Represents a price in the orderbook with its order queue
    
    """
    def __init__(self, Order):
        self.price = Order.price 
        self.head = Order
        self.tail = Order

    #Cummulative volume of all orders at this PriceLevel             
    @property    
    def vol(self):
        vol = 0
        next_order = self.head
        while(next_order is not None):
            vol += next_order.leavesqty
            next_order = next_order.next
        return vol
    
    def append(self, Order):        
        self.tail.next = Order
        Order.prev = self.tail
        self.tail = Order        
    
    def pop(self):
        self.head.active = False
        if self.head.next is None:         
            self.head = None
            self.tail = None
        else:
            self.head.next.prev = None            
            self.head = self.head.next
    
    
class OrderBook():
    """ Bids or Asks orderbook with different PriceLevels
    
    """
    def __init__(self):        
        self.book = dict()
        # Pointer to Best PriceLevel 
        self.best = None
	
    def add(self, Order):
        if Order.price in self.book:
            self.book[Order.price].append(Order)
        else:
            new_pricelevel = PriceLevel(Order)
            self.book.update({Order.price:new_pricelevel})
            if self.best is None or self.is_new_best(Order):
                self.best = new_pricelevel
        Order.active = True
    
    @abstractmethod
    def is_new_best(self, Order):
        pass
        

class Bids(OrderBook):
    """ Bids Orderbook where best PriceLevel has highest price
        Implements is_new_best abstract method that behaves differently
        for Bids or Asks
    """
    def __init__(self):
        super().__init__()
    
    def is_new_best(self, Order):        
        if Order.price > self.best.price:
            return True
        else:
            return False
    
class Asks(OrderBook):
    """ Asks Orderbook where best PriceLevel has lowest price
        Implements is_new_best abstract method that behaves differently
        for Bids or Asks
    """
    def __init__(self):
        super().__init__()
        
    def is_new_best(self, Order):
        if Order.price < self.best.price:
            return True
        else:
            return False
        