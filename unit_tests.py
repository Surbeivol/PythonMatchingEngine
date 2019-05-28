#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 21:16:34 2019

@author: Francisco Merlos
"""

import unittest
from market import Market, Order 
import time
from collections import namedtuple
import numpy as np

class NewOrderTests(unittest.TestCase):
       
        
    def test_new_pricelevel(self):
        market = Market()
        bidprice = np.random.uniform(0.0001,100000)
        o1 = namedtuple('Order', 'is_buy, qty, price')
        o1 = o1(is_buy=True, qty=10, price=bidprice)
        o2 = namedtuple('Order', 'is_buy, qty, price')
        o2 = o2(is_buy=True, qty=5, price=bidprice)
        o3 = namedtuple('Order', 'is_buy, qty, price')
        o3 = o3(is_buy=True, qty=7, price=bidprice)
        
                
        # Check price level creation, heads and tails
        o1uid = market.send(*o1)
        self.assertIn(o1.price, market.bids.book.keys())
        self.assertEqual(market.bids.best.price, o1.price)        
        self.assertEqual(market.bids.best.head.uid, o1uid)
        self.assertEqual(market.bids.best.tail.uid, o1uid)
        self.assertEqual(market.orders[o1uid].uid, o1uid)
        o2uid = market.send(*o2)
        self.assertEqual(market.bids.best.price, bidprice)
        # Check time priority inside PriceLevel
        self.assertEqual(market.bids.best.head.uid, o1uid)        
        o3uid = market.send(*o3)
        self.assertEqual(market.bids.best.head.uid, o1uid)
        self.assertEqual(market.bids.best.head.next.uid, o2uid)
        self.assertIs(market.bids.best.tail.uid, o3uid)
        # Check list of orders
        
        
        ### SAME FOR ASKS
        askprice = bidprice+0.0001
        o4 = namedtuple('Order', 'is_buy, qty, price')
        o4 = o4(is_buy=False, qty=10, price=askprice)
        o5 = namedtuple('Order', 'is_buy, qty, price')
        o5 = o5(is_buy=False, qty=5, price=askprice)
        o6 = namedtuple('Order', 'is_buy, qty, price')
        o6 = o6(is_buy=False, qty=7, price=askprice)
                
        
        # Check price level creation, heads and tails
        o4uid = market.send(*o4)
        self.assertIn(askprice, market.asks.book.keys())
        self.assertEqual(market.asks.best.price, o4.price)        
        self.assertEqual(market.asks.best.head.uid, o4uid)
        self.assertEqual(market.asks.best.tail.uid, o4uid)
        self.assertEqual(market.orders[o4uid].uid, o4uid)
        o5uid = market.send(*o5)
        self.assertEqual(market.asks.best.price, askprice)
        # Check time priority inside PriceLevel
        self.assertIs(market.asks.best.head.uid, o4uid)        
        o6uid = market.send(*o6)
        self.assertEqual(market.asks.best.head.uid, o4uid)
        self.assertEqual(market.asks.best.head.next.uid, o5uid)
        self.assertEqual(market.asks.best.tail.uid, o6uid)
        
    def test_cancel_order(self):
        
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
    
        # REMOVE MIDDLE ORDER IN QUEUE
        market.cancel(o2.uid)
        # Check order is removed
        self.assertEqual(market.orders[o2.uid].leavesqty, 0)
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
        self.assertEqual(o4.leavesqty, 0)
        # Check Doubly Linked List
        self.assertIs(o1.next, o3)
        self.assertIs(o3.prev, o1)
        self.assertIsNone(o3.next)
        self.assertIs(market.bids.best.head, o1)
        self.assertIs(market.bids.best.tail, o3)
        
        # REMOVE HEADmarket = Market()
        # alternate oders in PriceLevels
    
        market.cancel(o1.uid)
        # Check order is removed
        self.assertEqual(o1.leavesqty, 0)
        # Check Doubly Linked List
        self.assertIsNone(o3.prev)
        self.assertIsNone(o3.next)
        self.assertIs(market.bids.best.head, o3)
        self.assertIs(market.bids.best.tail, o3)
        
        # REMOVE HEAD+TAIL => REMOVE PRICE_LEVEL
        market.cancel(o3.uid)
        # Check order is removed
        self.assertEqual(o3.leavesqty, 0)
        # Check PriceLevel removed
        self.assertNotIn(0.2, market.bids.book)
        # Check new best bid
        self.assertIs(market.bids.best.head, o5)
        market.cancel(o5.uid)
        self.assertIs(len(market.bids.book), 0)
        
        ########################
        #### SAME FOR ASKS #####
        ########################        
        o1 = Order(uid=1,
                   is_buy=False,
                   qty=1000,
                   price=0.2,
                   timestamp=time.time())
        o2 = Order(uid=2,
                   is_buy=False,
                   qty=500,
                   price=0.2,
                   timestamp=time.time())
        o3 = Order(uid=3,
                   is_buy=False,
                   qty=600,
                   price=0.2,
                   timestamp=time.time())
        o4 = Order(uid=4,
                   is_buy=False,
                   qty=200,
                   price=0.2,
                   timestamp=time.time())
        o5 = Order(uid=5,
                   is_buy=False,
                   qty=77,
                   price=0.21,
                   timestamp=time.time())
        
        market.send(o1)
        market.send(o2)
        market.send(o3)
        market.send(o4)
        market.send(o5)
        
        market.cancel(o2.uid)
        
        # REMOVE MIDDLE ORDER IN QUEUE
        # Check order is removed
        self.assertEqual(o2.leavesqty, 0)
        # Check Doubly Linked List
        self.assertIs(o1.next, o3)
        self.assertIs(o3.prev, o1)
        self.assertIs(o3.next, o4)
        self.assertIs(o4.prev, o3)
        self.assertIs(market.asks.best.head, o1)
        self.assertIs(market.asks.best.tail, o4)
        
        # REMOVE TAIL
        market.cancel(o4.uid)
        # Check order is removed
        self.assertEqual(o4.leavesqty, 0)
        # Check Doubly Linked List
        self.assertIs(o1.next, o3)
        self.assertIs(o3.prev, o1)
        self.assertIsNone(o3.next)
        self.assertIs(market.asks.best.head, o1)
        self.assertIs(market.asks.best.tail, o3)
        
        # REMOVE HEAD
        market.cancel(o1.uid)
        # Check order is removed
        self.assertEqual(o1.leavesqty, 0)
        # Check Doubly Linked List
        self.assertIsNone(o3.prev)
        self.assertIsNone(o3.next)
        self.assertIs(market.asks.best.head, o3)
        self.assertIs(market.asks.best.tail, o3)
        
        # REMOVE HEAD+TAIL => REMOVE PRICE_LEVEL
        market.cancel(o3.uid)
        # Check order is removed
        self.assertEqual(o3.leavesqty, 0)
        # Check PriceLevel removed
        self.assertNotIn(0.2, market.asks.book)
        # Check new best bid
        self.assertIs(market.asks.best.head, o5)
        
    def test_aggressive_orders(self):
        market = Market()
        # alternate oders in PriceLevels        
        o1 = Order(uid=1,
                   is_buy=True,
                   qty=100,
                   price=10.001,
                   timestamp=time.time())
        o2 = Order(uid=2,
                   is_buy=True,
                   qty=100,
                   price=10.002,
                   timestamp=time.time())
        o3 = Order(uid=3,
                   is_buy=True,
                   qty=100,
                   price=10.001,
                   timestamp=time.time())
        o4 = Order(uid=4,
                   is_buy=True,
                   qty=100,
                   price=10.002,
                   timestamp=time.time())
        # latest order but best bid for price-time priority
        o5 = Order(uid=5,
                   is_buy=True,
                   qty=100,
                   price=10.003,
                   timestamp=time.time())
        
        for order in (o1, o2, o3, o4, o5):
            market.send(order)
            
        # aggressive order to sweep all positions and place rest
        o6 = Order(uid=6,
                   is_buy=False,
                   qty=100,
                   price=9.999,
                   timestamp=time.time())
        
        market.send(o6)
        # check new top of book
        self.assertIs(market.bids.best.head, o2)
        # check best price
        self.assertIs(market.trades[0][0], 10.003)
        
        o7 = Order(uid=7,
                   is_buy=False,
                   qty=100,
                   price=9.999,
                   timestamp=time.time())
        
        market.send(o7)           
        self.assertIs(market.bids.best.head, o4)
        self.assertIs(o5.leavesqty, 0)
        self.assertIs(market.trades[1][0], 10.002)
        
        o8 = Order(uid=8,
                   is_buy=False,
                   qty=500,
                   price=9.999,
                   timestamp=time.time())        
        market.send(o8)        
        
        # check worst price        
        self.assertIs(len(market.trades), 5)
        self.assertIs(market.trades[4][0], 10.001)
        # check empty bids book
        self.assertIs(len(market.bids.book), 0)
        # check new pricelevel at o8 price
        self.assertIs(market.asks.best.price, o8.price)
        
        
if __name__ == "__main__":
    unittest.main()
    