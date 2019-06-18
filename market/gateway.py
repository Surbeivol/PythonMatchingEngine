#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 22:32:58 2019

@author: paco
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from market.market import Market
from datetime import datetime, timedelta
from tqdm import tqdm
from numba import jit
from collections import deque, namedtuple

class Gateway():
    """ Creates an empty Python Matching Engine (market simulator) and injects 
    real historical orders to it creating the real orderbooks and trades
    that happened in that market session. It also allows you to send
    your own orders to make them interact (i.e. cross) with the historical
    orderbooks that were present that day. The orders you send to the market 
    through this Gateway will also experience latency as they 
    would in real life.
    
    The Gateway allows us to run a synchronous simulation of the interaction
    of your algorithm with a Python Matching Engine (market simulator)
    that will be injected with real life historical orders of a 
    past market session while taking into account the effect
    of this latency. 
    
    For example, when your algorithm receives a new market best bid price,
    actually this price happened "md_latency" microseconds in the past, 
    the time it took to reach your algorithm. Your algo will take "algo_latency"
    microseconds to make a decission and send a message (new/cancel/modif),
    and finally, this message will take "mkt_latency" microseconds to reach
    the market because of the physical distance and the different systems
    it needs to cross through before reaching the market. 
    
    The total latency will be: 
        latency = md_latency + algo_latency + mkt_latency
    
    When you send messages to a market through this Gateway, 
    your messages will reach the market "latency" microseconds 
    after the time of the last historical order that reached the market
    and that produced the last market data update upon which your
    algo made its last decission.     
        
    Args:
        ticker (str): symbol of the shares
        year (int): year
        month (int): month
        day (int): day
        latency (int): mean latency in microseconds that we expect 
                        our orders to have in real life when sent 
                        to the market (market data one way 
                                     + algo decission time
                                     + market access one way)        
                
    """
    
    def __init__(self, ticker, year, month, day, latency):
        self.ticker = ticker
        self.year = year
        self.month = month
        self.day = day
        self.latency = latency
        self.my_queue = deque()
        self.mkt_idx = 0
        self.mkt = Market(ticker=ticker)
        date = f'{year}-{month}-{day}'
        self.mkt.date = ticker, date
        self.OrdTuple = namedtuple('Order',
                                   'ordtype uid is_buy qty price timestamp')
        self.my_last_uid = 0 
        # book positions (bid+ask) available in historical data
        BOOK_POS = 20
        
        # load historical orders from csv file
        session = f'./data/orders-{ticker}-{date}.csv'
        csv = pd.read_csv(session, sep=';', float_precision='round_trip')
        csv['timestamp'] = pd.to_datetime(csv['timestamp'])

        # We will be working with ndarrays instead of DataFrames for speed
        self.hist_orders = csv.values
        self.mkt_nord = csv.shape[0]
        
        # we store index positions of columns for array indexing
        columns = csv.columns
        self.col_idx = {}
        for col_name in csv.columns:
            self.col_idx.update({col_name:np.argmax(columns==col_name)})

        # send first 20 orders that will compose first market snapshot
        # this is the real orderbook that was present when the market opened
        # right after the opening auction
        for ord_idx in range(BOOK_POS):   
            self._send_to_market(self.hist_orders[ord_idx], is_mine=False)
        self.mkt_idx = BOOK_POS - 1
        self.mkt_time = self.hist_orders[BOOK_POS-1][self.col_idx['timestamp']]

    

    def _send_to_market(self, order, is_mine):
        """ Send an order/modif/cancel to the market
        
            Args:
                order (ndarray): order to be sent
                is_mine (bool): False if historical, True if user sent
        """
        
        
        ord_type = order[self.col_idx['ordtype']]
        if ord_type == "new":
            self.mkt.send(is_buy=order[self.col_idx['is_buy']],
                            qty=order[self.col_idx['qty']],
                            price=order[self.col_idx['price']],
                            uid=order[self.col_idx['uid']],
                            is_mine=is_mine,
                            timestamp=order[self.col_idx['timestamp']])
        elif ord_type == "cancel":
            self.mkt.cancel(uid=order[self.col_idx['uid']])
        elif ord_type == "modif":
            self.mkt.modif(uid=order[self.col_idx['uid']],                           
                           new_qty=order[self.col_idx['qty']])
        else:
            raise ValueError(f'Unexpected ordtype: {ord_type}')
            
    
    def move_n_seconds(self, n_seconds):
        """ 
        """
        
        stop_time = self.mkt_time + timedelta(0, n_seconds)
        
        while (self.mkt_time<=stop_time):
            self.tick()
        
        self.mkt_time = stop_time


    def _send_historical_order(self, mktorder):
        self.mkt_idx += 1        
        self._send_to_market(mktorder, is_mine=False)
        self.mkt_time = mktorder[self.col_idx['timestamp']]


    def move_until(self, stop_time):
        """ 
        
        Params:
            stop_time (datetime):         
                
        """
        
        while (self.mkt_time <= stop_time):
            mktorder = self.hist_orders[self.mkt_idx+1]
            self._send_historical_order(mktorder)


    def tick(self):
        """ Move the market forward one tick (process next order)
        
            If the user has messages (new/cancel/modif) queued, it will
            decide whether to send a user or historical order based on
            their theoretical arrival time (timestamp)
        """
        
        # next historical order to be sent
        mktorder = self.hist_orders[self.mkt_idx+1]
        # if I have queued orders
        if self.my_queue:
            # if my order reaches the market before the next historical order
            if self.my_queue[0].timestamp < mktorder[self.col_idx['timestamp']]:
                my_order = self.my_queue.popleft()
                self._send_to_market(my_order, is_mine=True)
                self.mkt_time = my_order[self.col_idx['timestamp']]
                return
        
        # otherwise sent next historical order
        self._send_historical_order(mktorder)

        
    def queue_my_new(self, is_buy, qty, price):
        """ Queue a user new order to be sent to the market when time is due 
        
            Args:
                is_buy (bool): True for buy orders
                qty (int): quantity or volume
                price (float): limit price of the order
                
            Reuturns:
                An int indicating the uid that the market will assign to
                it when it is introudced.
                NOTES: as the order is queued by this function, its uid does
                not exist yet in the market. It will not exist until 
                the time is due and the order reaches the market. Requesting
                the status of this uid will therefore raise a KeyError
                meanwhile.
                Uids of user orders will be negative, this
                way we ensure no collisions with historical positive uids and 
                have an easy way to know if an order is ours                
                
        """        
        
        self.my_last_uid -= 1                
        message = self.OrdTuple(ordtype="new",
                                    uid=self.my_last_uid,
                                    is_buy=is_buy,
                                    qty=qty,
                                    price=price,                              
                                    timestamp=self._arrival_time())        
        self.my_queue.append(message)        
        return self.my_last_uid 

    
    def queue_my_modif(self, uid, new_qty):
        """ Modify an order identified by its uid without loosing priority.
        Modifications can only downsize the volume. 
        If you attempt to increase the volume, the
        modification message will do nothing. Downsizing volume will 
        mantain your price-time priority in the market. If you want to
        increase volume or change price, you need to cancel your previous
        order and send a new one. 
        
        Args:
            uid (int): uid of our order to be modified
            new_qty(int): new quantity. Only downsizing allowed. 
        
        """
                
        message = self.OrdTuple(ordtype="modif",
                                    uid=uid,
                                    is_buy=np.nan,
                                    qty=new_qty,
                                    price=np.nan,                              
                                    timestamp=self._arrival_time())        
        self.my_queue.append(message)        
    
    
    def queue_my_cancel(self, uid):
        """ Cancel an order by its uid
        
        """
                
        message = self.OrdTuple(ordtype="cancel",
                                    uid=uid,
                                    is_buy=np.nan,
                                    qty=np.nan,
                                    price=np.nan,                              
                                    timestamp=self._arrival_time())        
        self.my_queue.append(message)        
    
    
    def ord_status(self, uid):
        """ Returns the current mkt status of an order identified by its uid.
        
        Args:
            uid (int): unique order identifier
        
        NOTE: when an order is queued, its uid does not exist yet in the
        market since it did not arrive there yet. Calling this function
        on a uid that is queued by not yet in the market will raise a 
        KeyError exception that will have to be handled.        
        
        """
        # TODO: use ticker to select market orderbook
        return self.mkt.get(uid)

    
    def _arrival_time(self):
        """ Returns the estimated time of arrival of an order
        
        """
        
        return self.mkt_time + timedelta(0, 0, self.latency)



        
        
        
        