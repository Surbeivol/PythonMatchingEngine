# -*- coding: utf-8 -*-
"""
Created on Thu May 16 14:14:51 2019

@author: Francisco Merlos
"""
from abc import ABC, abstractmethod

class Market():

    def __init__(self):
        self.bids = Bids()
        self.asks = Asks()
        self.trades = []
		
    def send(self, Order):
        #pdb.set_trace()
        while (Order.leavesqty > 0):
            if self.is_aggressive(Order):            
                self.sweep_best_price(Order)    
            else:
                if Order.is_buy:
                    self.bids.add(Order)            
                else:
                    self.asks.add(Order)
                break
			
    def is_aggressive(self, Order):
        is_agg = True
        if Order.is_buy:
            if self.asks.best is None or self.asks.best.price > Order.price:
                is_agg = False
        else:
            if self.bids.best is None or self.bids.best.price < Order.price:
                is_agg = False
        return is_agg 
    
    def sweep_best_price(self, Order):        
        if Order.is_buy:            
            best = self.asks.best
        else:
            best = self.bids.best        
        while(Order.leavesqty > 0):
            if best.head.leavesqty <= Order.leavesqty:                
                trdqty = best.head.leavesqty
                self.trades.append([best.price, trdqty])
                best.pop()
                Order.leavesqty -= trdqty
                if best.head is None:
                    self.remove_price(Order.is_buy, best.price)
                    break
            else:
                self.trades.append([best.price, Order.leavesqty])
                best.head.leavesqty -= Order.leavesqty
                Order.leavesqty = 0
        
    def remove_price(self, is_buy, price):
        if is_buy:
            del self.asks.book[price]
            if len(self.asks.book)>0:
                self.asks.best = self.asks.book[min(self.asks.book.keys())]
            else:
                self.asks.best = None
        else:
            del self.bids.book[price]
            if len(self.bids.book)>0:
                self.bids.best = self.bids.book[max(self.bids.book.keys())]
            else:
                self.bids.best = None
                   
                
class Order():
    """ Represents an order inside the market with its current status 
    
    """
    #__slots__ = ["uid", "is_buy", "qty", "price", "timestamp", "status"]
    
    def __init__(self, uid, is_buy, qty, price, timestamp):
        self.uid = uid
        self.is_buy = is_buy
        self.qty = qty
        self.cumqty = 0
        self.leavesqty = qty
        self.price = price
        self.timestamp = timestamp    
        # DDL attributes 
        self.prev = None
        self.next = None
        

class PriceLevel():
    """ Represents a price in the orderbook with its order queue
    
    """
    def __init__(self, Order):
        self.price = Order.price 
        self.head = Order
        self.tail = Order
            
    def append(self, Order):        
        self.tail.next = Order
        Order.prev = self.tail
        self.tail = Order
    
    def pop(self):
        if self.head.next is None:         
            self.head = None
            self.tail = None
        else:
            self.head.next.prev = None            
            self.head = self.head.next
            
        
class OrderBook():
    def __init__(self):        
        self.book = dict()
        self.best = None
	
    def add(self, Order):
        if Order.price in self.book:
            self.book[Order.price].append(Order)
        else:
            new_pricelevel = PriceLevel(Order)
            self.book.update({Order.price:new_pricelevel})
            if self.best is None or self.is_new_best(Order):
                self.best = new_pricelevel
    
    @abstractmethod
    def is_new_best(self, Order):
        pass
        

class Bids(OrderBook):
    
    def __init__(self):
        super().__init__()
    
    def is_new_best(self, Order):        
        if Order.price > self.best.price:
            return True
        else:
            return False
    
class Asks(OrderBook):
    def __init__(self):
        super().__init__()
        
    def is_new_best(self, Order):
        if Order.price < self.best.price:
            return True
        else:
            return False
        