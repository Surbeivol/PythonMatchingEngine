# -*- coding: utf-8 -*-
"""
Created on Thu May 16 14:14:51 2019

@author: fmerlos
"""
import queue



class 

class Order():
    """ Represents an order inside the market with its current status 
    
    """
    __slots__ = ["uid", "volume", "price", "timestamp", "status"]
    
    def __init__(self, uid, qty, price, timestamp):
        self.uid =  uid
        self.qty = qty
        self.cumqty = 0
        self.leavesqty = qty
        self.price =  price
        self.timestamp
        # "pending"/"new"/"partfill"/"fill"/"cancelled"/"rejected"
        self.status = "pending" 
        
        
class OrderQueue():
    """ Represents a queue of Order objects
    
    """

    def __init__(self, )
        

        