#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 21:16:34 2019

@author: Francisco Merlos
"""
import unittest
from core.orderbook import Orderbook
import time
from collections import namedtuple
import numpy as np

class NewOrderTests(unittest.TestCase):
       
    def test_new_pricelevel(self):
        """ Add new bid and ask orders and checks price-time priority
        
        """
        
        orderbook = Orderbook('san')
        bidprice = np.random.uniform(0.0001,100000)
        o1uid = 1
        o2uid = 2
        o3uid = 3
        order = namedtuple('Order', 'is_buy, qty, price, uid')
        o1 = order(is_buy=True, qty=10, price=bidprice, uid=o1uid)
        o2 = order(is_buy=True, qty=5, price=bidprice, uid=o2uid)
        o3 = order(is_buy=True, qty=7, price=bidprice, uid=o3uid)     
                
        # Check price level creation, heads and tails, uid & order active
        orderbook.send(*o1)
        self.assertIn(o1.price, orderbook._bids.book.keys())
        self.assertEqual(orderbook._bids.best.price, o1.price)        
        self.assertEqual(orderbook._bids.best.head.uid, o1uid)
        self.assertEqual(orderbook._bids.best.tail.uid, o1uid)
        self.assertEqual(orderbook._orders[o1uid].uid, o1uid)
        self.assertEqual(orderbook.get(o1uid)['active'], True)
        orderbook.send(*o2)
        self.assertEqual(orderbook._bids.best.price, bidprice)
        # Check time priority inside PriceLevel
        self.assertEqual(orderbook._bids.best.head.uid, o1uid)        
        orderbook.send(*o3)
        self.assertEqual(orderbook._bids.best.head.uid, o1uid)
        self.assertEqual(orderbook._bids.best.head.next.uid, o2uid)
        self.assertEqual(orderbook._bids.best.tail.uid, o3uid)
        # Check list of orders        
        
        ### SAME FOR ASKS
        askprice = bidprice+0.0001
        o4uid = 4
        o5uid = 5
        o6uid = 6
        o4 = order(is_buy=False, qty=10, price=askprice, uid=o4uid)
        o5 = order(is_buy=False, qty=5, price=askprice, uid=o5uid)
        o6 = order(is_buy=False, qty=7, price=askprice, uid=o6uid)
                     
        # Check price level creation, heads and tails
        orderbook.send(*o4)
        self.assertIn(askprice, orderbook._asks.book.keys())
        self.assertEqual(orderbook._asks.best.price, o4.price)        
        self.assertEqual(orderbook._asks.best.head.uid, o4uid)
        self.assertEqual(orderbook._asks.best.tail.uid, o4uid)
        self.assertEqual(orderbook._orders[o4uid].uid, o4uid)
        orderbook.send(*o5)

        # Check time priority inside PriceLevel
        self.assertIs(orderbook._asks.best.head.uid, o4uid)        
        orderbook.send(*o6)
        self.assertEqual(orderbook._asks.best.head.uid, o4uid)
        self.assertEqual(orderbook._asks.best.head.next.uid, o5uid)
        self.assertEqual(orderbook._asks.best.tail.uid, o6uid)
        
    def test_cancel_order(self):
        """ Cancels active orders and checks PriceLevel deletion,
            price-time priority of left resting orders, and doubly linked
            list of orders inside Price Level
        
        """
        
        orderbook = Orderbook('san')
        o1uid = 1
        o2uid = 2
        o3uid = 3
        o4uid = 4
        o5uid = 5
        order = namedtuple('Order', 'is_buy, qty, price, uid')
        o1 = order(is_buy=True, qty=1000, price=0.2, uid=o1uid)
        o2 = order(is_buy=True, qty=500, price=0.2, uid=o2uid)
        o3 = order(is_buy=True, qty=600, price=0.2, uid=o3uid)
        o4 = order(is_buy=True, qty=200, price=0.2, uid=o4uid)
        o5 = order(is_buy=True, qty=77, price=0.19, uid=o5uid)        
        orderbook.send(*o1)
        orderbook.send(*o2)
        orderbook.send(*o3)
        orderbook.send(*o4)
        orderbook.send(*o5)
    
        # CANCEL MIDDLE ORDER IN QUEUE
        orderbook.cancel(o2uid)
        # Check order is not active & leavesqty is 0
        self.assertEqual(orderbook.get(o2uid)['active'], False)
        self.assertEqual(orderbook.get(o2uid)['leavesqty'], 0)
    
        # Check Doubly Linked List
        self.assertIs(orderbook._orders[o1uid].next.uid, o3uid)
        self.assertIs(orderbook._orders[o3uid].prev.uid, o1uid)
        self.assertIs(orderbook._orders[o3uid].next.uid, o4uid)
        self.assertIs(orderbook._orders[o4uid].prev.uid, o3uid)
        self.assertIs(orderbook.bbid[0], o1.price)
        self.assertIs(orderbook._bids.best.tail.uid, o4uid)
        
        # CANCEL TAIL
        orderbook.cancel(o4uid)
        # Check order is removed
        self.assertEqual(orderbook.get(o4uid)['leavesqty'], 0)
        # Check Doubly Linked List
        self.assertIs(orderbook._orders[o1uid].next.uid, o3uid)
        self.assertIs(orderbook._orders[o3uid].prev.uid, o1uid)
        self.assertIsNone(orderbook._orders[o3uid].next)
        self.assertIs(orderbook._bids.best.head.uid, o1uid)
        self.assertIs(orderbook._bids.best.tail.uid, o3uid)
        
        # CANCEL HEAD 
        # alternate oders in PriceLevels    
        orderbook.cancel(o1uid)
        # Check order is removed
        self.assertEqual(orderbook.get(o1uid)['leavesqty'], 0)
        # Check Doubly Linked List
        self.assertIsNone(orderbook._orders[o3uid].prev)
        self.assertIsNone(orderbook._orders[o3uid].next)
        self.assertIs(orderbook._bids.best.head.uid, o3uid)
        self.assertIs(orderbook._bids.best.tail.uid, o3uid)
        
        # CANCEL HEAD&TAIL ORDER => REMOVE PRICE_LEVEL
        orderbook.cancel(o3uid)
        # Check order is removed
        self.assertEqual(orderbook.get(o3uid)['leavesqty'], 0)
        # Check PriceLevel removed
        self.assertNotIn(0.2, orderbook._bids.book)
        # Check new best bid
        self.assertIs(orderbook._bids.best.head.uid, o5uid)
        orderbook.cancel(o5uid)
        self.assertIs(len(orderbook._bids.book), 0)
        
        ########################
        #### SAME FOR ASKS #####
        ########################        
        orderbook = Orderbook('san')
        o1uid = 1
        o2uid = 2
        o3uid = 3
        o4uid = 4
        o5uid = 5
        order = namedtuple('Order', 'is_buy, qty, price, uid')
        o1 = order(is_buy=False, qty=1000, price=0.2, uid=o1uid)
        o2 = order(is_buy=False, qty=500, price=0.2, uid=o2uid)
        o3 = order(is_buy=False, qty=600, price=0.2, uid=o3uid)
        o4 = order(is_buy=False, qty=200, price=0.2, uid=o4uid)
        o5 = order(is_buy=False, qty=77, price=0.21, uid=o5uid)        
        orderbook.send(*o1)
        orderbook.send(*o2)
        orderbook.send(*o3)
        orderbook.send(*o4)
        orderbook.send(*o5)
    
        # CANCEL MIDDLE ORDER IN QUEUE
        orderbook.cancel(o2uid)
        # Check order is not active & leavesqty is 0
        self.assertEqual(orderbook.get(o2uid)['active'], False)
        self.assertEqual(orderbook.get(o2uid)['leavesqty'], 0)
    
        # Check Doubly Linked List
        self.assertIs(orderbook._orders[o1uid].next.uid, o3uid)
        self.assertIs(orderbook._orders[o3uid].prev.uid, o1uid)
        self.assertIs(orderbook._orders[o3uid].next.uid, o4uid)
        self.assertIs(orderbook._orders[o4uid].prev.uid, o3uid)
        self.assertIs(orderbook.bask[0], o1.price)
        self.assertIs(orderbook._asks.best.tail.uid, o4uid)
        
        # CANCEL TAIL ORDER
        orderbook.cancel(o4uid)
        # Check order is removed
        self.assertEqual(orderbook.get(o4uid)['leavesqty'], 0)
        # Check Doubly Linked List
        self.assertIs(orderbook._orders[o1uid].next.uid, o3uid)
        self.assertIs(orderbook._orders[o3uid].prev.uid, o1uid)
        self.assertIsNone(orderbook._orders[o3uid].next)
        self.assertIs(orderbook._asks.best.head.uid, o1uid)
        self.assertIs(orderbook._asks.best.tail.uid, o3uid)
        
        # CANCEL HEAD 
        # alternate oders in PriceLevels    
        orderbook.cancel(o1uid)
        # Check order is removed
        self.assertEqual(orderbook.get(o1uid)['leavesqty'], 0)
        # Check Doubly Linked List
        self.assertIsNone(orderbook._orders[o3uid].prev)
        self.assertIsNone(orderbook._orders[o3uid].next)
        self.assertIs(orderbook._asks.best.head.uid, o3uid)
        self.assertIs(orderbook._asks.best.tail.uid, o3uid)
        
        # CANCEL HEAD&TAIL ORDER => REMOVE PRICE_LEVEL
        orderbook.cancel(o3uid)
        # Check order is removed
        self.assertEqual(orderbook.get(o3uid)['leavesqty'], 0)
        # Check PriceLevel removed
        self.assertNotIn(0.2, orderbook._asks.book)
        # Check new best ask
        self.assertIs(orderbook._asks.best.head.uid, o5uid)
        orderbook.cancel(o5uid)
        self.assertIs(len(orderbook._asks.book), 0)
        
    def test_aggressive_orders(self):
        orderbook = Orderbook('san')
        # alternate oders in PriceLevels    
        order = namedtuple('Order', 'is_buy, qty, price, uid')
        o1uid = 1
        o2uid = 2
        o3uid = 3
        o4uid = 4
        o5uid = 5
        o1 = order(is_buy=True, qty=100, price=10.001, uid=o1uid)
        o2 = order(is_buy=True, qty=100, price=10.002, uid=o2uid)
        o3 = order(is_buy=True, qty=100, price=10.001, uid=o3uid)
        o4 = order(is_buy=True, qty=100, price=10.002, uid=o4uid)
        o5 = order(is_buy=True, qty=100, price=10.003, uid=o5uid)       
        orderbook.send(*o1)
        orderbook.send(*o2)
        orderbook.send(*o3)
        orderbook.send(*o4)
        orderbook.send(*o5)
                
        # aggressive order to sweep all positions and place rest
        o6uid = 6        
        o6 = order(is_buy=False, qty=100, price=9.999, uid=o6uid)  
        orderbook.send(*o6)
        # check new top of book
        self.assertIs(orderbook.bbid[0], o2.price)
        # check best price
        self.assertEqual(orderbook.trades_px[0], 10.003)        
        
        # send copy of o6 order 
        o7uid = 7        
        o7 = order(is_buy=False, qty=100, price=9.999, uid=o7uid)  
        orderbook.send(*o7)
        self.assertIs(orderbook._bids.best.head.uid, o4uid)
        self.assertIs(orderbook.get(o5uid)['leavesqty'], 0)
        self.assertEqual(orderbook.trades_px[1], 10.002)
        
        # send order and sweep 4 positions and leave rest in book as ask
        o8uid=8
        o8 = order(is_buy=False, qty=500, price=9.999, uid=o8uid)   
        orderbook.send(*o8)        
        # check worst price        
        self.assertEqual(orderbook.trades_px[4], 10.001)
        # check empty bids book
        self.assertIs(len(orderbook._bids.book), 0)
        # check new pricelevel at o8 price
        self.assertIs(orderbook._asks.best.price, o8.price)
        
        
if __name__ == "__main__":
    unittest.main()
    
