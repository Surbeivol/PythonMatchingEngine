#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 21:16:34 2019

@author: Francisco Merlos
"""

import unittest
from market import Market, Order 
import time

class NewOrderTests(unittest.TestCase):
    
    def test_new_pricelevel(self):
        market = Market()
        o1 = Order(uid=1,
                   is_buy=True,
                   qty=10,
                   price=10.4,
                   timestamp=time.time())
        o2 = Order(uid=2,
                   is_buy=True,
                   qty=5,
                   price=10.4,
                   timestamp=time.time())
        o3 = Order(uid=3,
                   is_buy=True,
                   qty=7,
                   price=10.4,
                   timestamp=time.time())
        
        # Check price level creation, heads and tails
        market.send(o1)
        self.assertIn(10.4, market.bids.book.keys())
        self.assertEqual(market.bids.best.price, 10.4)        
        self.assertIs(market.bids.best.head, o1)
        self.assertIs(market.bids.best.tail, o1)
        self.assertIs(market.orders[1], o1)
        market.send(o2)
        self.assertEqual(market.bids.best.price, 10.4)
        # Check time priority inside PriceLevel
        self.assertIs(market.bids.best.head, o1)        
        market.send(o3)
        self.assertIs(market.bids.best.head, o1)
        self.assertIs(market.bids.best.head.next, o2)
        self.assertIs(market.bids.best.tail, o3)
        # Check list of orders
        
        
        ### SAME FOR ASKS
        
        o4 = Order(uid=4,
                   is_buy=False,
                   qty=10,
                   price=10.5,
                   timestamp=time.time())
        o5 = Order(uid=5,
                   is_buy=False,
                   qty=5,
                   price=10.5,
                   timestamp=time.time())
        o6 = Order(uid=6,
                   is_buy=False,
                   qty=7,
                   price=10.5,
                   timestamp=time.time())
        
        # Check price level creation, heads and tails
        market.send(o4)
        self.assertIn(10.5, market.asks.book.keys())
        self.assertEqual(market.asks.best.price, 10.5)        
        self.assertIs(market.asks.best.head, o4)
        self.assertIs(market.asks.best.tail, o4)
        self.assertIs(market.orders[4], o4)
        market.send(o5)
        self.assertEqual(market.asks.best.price, 10.5)
        # Check time priority inside PriceLevel
        self.assertIs(market.asks.best.head, o4)        
        market.send(o6)
        self.assertIs(market.asks.best.head, o4)
        self.assertIs(market.asks.best.head.next, o5)
        self.assertIs(market.asks.best.tail, o6)
        
    def test_cancel_order(self):
        
        # 
        market = Market()
        o1 = Order(uid=1,
                   is_buy=True,
                   qty=1000,
                   price=0.2,
                   timestamp=time.time())
        o2 = Order(uid=2,
                   is_buy=True,
                   qty=500,
                   price=0.2,
                   timestamp=time.time())
        o3 = Order(uid=3,
                   is_buy=True,
                   qty=600,
                   price=0.2,
                   timestamp=time.time())
        o4 = Order(uid=4,
                   is_buy=True,
                   qty=200,
                   price=0.2,
                   timestamp=time.time())
        o5 = Order(uid=5,
                   is_buy=True,
                   qty=77,
                   price=0.19,
                   timestamp=time.time())
        market.send(o1)
        market.send(o2)
        market.send(o3)
        market.send(o4)
        market.send(o5)
        market.cancel(o2.uid)
        
        # REMOVE MIDDLE ORDER IN QUEUE
        # Check order is removed
        self.assertNotIn(o2.uid, market.orders)
        # Check Doubly Linked List
        self.assertIs(o1.next, o3)
        self.assertIs(o3.prev, o1)
        self.assertIs(o3.next, o4)
        self.assertIs(o4.prev, o3)
        self.assertIs(market.bids.best.head, o1)
        self.assertIs(market.bids.best.tail, o4)
        
        # REMOVE TAIL
        market.cancel(o4.uid)
        # Check order is removed
        self.assertNotIn(o4.uid, market.orders)
        # Check Doubly Linked List
        self.assertIs(o1.next, o3)
        self.assertIs(o3.prev, o1)
        self.assertIsNone(o3.next)
        self.assertIs(market.bids.best.head, o1)
        self.assertIs(market.bids.best.tail, o3)
        
        # REMOVE HEAD
        market.cancel(o1.uid)
        # Check order is removed
        self.assertNotIn(o1.uid, market.orders)
        # Check Doubly Linked List
        self.assertIsNone(o3.prev)
        self.assertIsNone(o3.next)
        self.assertIs(market.bids.best.head, o3)
        self.assertIs(market.bids.best.tail, o3)
        
        # REMOVE HEAD+TAIL => REMOVE PRICE_LEVEL
        market.cancel(o3.uid)
        # Check order is removed
        self.assertNotIn(o3.uid, market.orders)
        # Check PriceLevel removed
        self.assertNotIn(0.2, market.bids.book)
        # Check new best bid
        self.assertIs(market.bids.best.head, o5)
        
    
    
if __name__ == "__main__":
    unittest.main()
    