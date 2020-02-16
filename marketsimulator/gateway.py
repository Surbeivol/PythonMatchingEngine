#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 22:32:58 2019

@author: paco
"""

import pandas as pd
import numpy as np
from marketsimulator.orderbook import Orderbook
from datetime import datetime, timedelta
from collections import deque, namedtuple
import pdb
import os


class Gateway:
    """ Creates an empty Python Matching Engine (orderbook simulator) and injects 
    real historical orders to it creating the real orderbooks and trades
    that happened in that orderbook session. It also allows you to send
    your own orders to make them interact (i.e. cross) with the historical
    orderbooks that were present that day. The orders you send to the orderbook 
    through this Gateway will also experience latency as they 
    would in real life.
    
    The Gateway allows us to run a synchronous simulation of the interaction
    of your algorithm with a Python Matching Engine (orderbook simulator)
    that will be injected with real life historical orders of a 
    past orderbook session while taking into account the effect
    of this latency. 
    
    For example, when your algorithm receives a new orderbook best bid price,
    actually this price happened "md_latency" microseconds in the past, 
    the time it took to reach your algorithm. Your algo will take "algo_latency"
    microseconds to make a decission and send a message (new/cancel/modif),
    and finally, this message will take "ob_latency" microseconds to reach
    the orderbook because of the physical distance and the different systems
    it needs to cross through before reaching the orderbook. 
    
    The total latency will be: 
        latency = md_latency + algo_latency + ob_latency
    
    When you send messages to a orderbook through this Gateway, 
    your messages will reach the orderbook "latency" microseconds 
    after the time of the last historical order that reached the orderbook
    and that produced the last orderbook data update upon which your
    algo made its last decission.     
        
    Args:
        ticker (str): symbol of the shares
        year (int): year
        month (int): month
        day (int): day
        latency (int): mean latency in microseconds that we expect 
                        our orders to have in real life when sent 
                        to the orderbook (orderbook data one way 
                                     + algo decission time
                                     + orderbook access one way)        
                
    """

    def __init__(self, **kwargs):

        self.path = os.path.dirname(__file__)
        ticker = kwargs.get('ticker')
        date = kwargs.get('date')
        year = date.year
        month = date.month
        day = date.day
        start_h = kwargs.get('start_h', 9)
        end_h = kwargs.get('end_h', 17.5)
        start_secs = int(start_h * 3600)
        end_secs = int(end_h * 3600)
        start_time = datetime(year, month, day) + timedelta(0, start_secs)
        end_time = datetime(year, month, day) + timedelta(0, end_secs)
        self.ob_time = start_time
        self.latency = kwargs.get('latency', 20000)
        self.my_queue = deque()
        self.ob_idx = 0
        self.ob = Orderbook(ticker=ticker)
        date = f'{year}-{month}-{day}'
        self.ob.date = ticker, date
        self.OrdTuple = namedtuple('Order',
                                   'ordtype uid is_buy qty price timestamp')
        self.my_last_uid = 0

        # load historical orders from csv file
        session = f'{self.path}/../data/historic_orders/orders-{ticker}-{date}.csv'
        csv = pd.read_csv(session, sep=';', float_precision='round_trip')
        csv['timestamp'] = pd.to_datetime(csv['timestamp'])

        # We will be working with ndarrays instead of DataFrames for speed
        self.hist_orders = csv.values
        self.ob_nord = csv.shape[0]

        # we store index positions of columns for array indexing
        columns = csv.columns
        self.col_idx = {}
        for col_name in csv.columns:
            self.col_idx.update({col_name:np.argmax(columns==col_name)})
            
        last_ord_time = self.hist_orders[-1][self.col_idx['timestamp']]
        self.end_time = min(last_ord_time, end_time)
        self.stop_time = self.end_time

        # book positions (bid+ask) available in historical data
        book_pos = 20
        # send first 20 orders that will compose first orderbook snapshot
        # this is the real orderbook that was present when the orderbook opened
        # right after the opening auction

        for ord_idx in range(book_pos):
            oborder = self.hist_orders[self.ob_idx]
            self._send_historical_order(oborder)

        self.move_historic_until(start_time)

        self.ob.reset_ob(reset_all=False)

        self.in_queue = dict()
        self.vol_in_queue = 0

    @property
    def next_ord_time(self):

        return self.hist_orders[self.ob_idx][self.col_idx['timestamp']]

    def _send_to_orderbook(self, order, is_mine):
        """ Send an order/modif/cancel to the orderbook
                order (ndarray): order to be sent
                is_mine (bool): False if historical, True if user sent
        """
        ord_type = order[self.col_idx['ordtype']]
        timestamp = order[self.col_idx['timestamp']]
        #        ob_open = self.check_ob_open(timestamp)
        if self.check_ord_in_time(timestamp):
            self.update_ob_time(timestamp)
            if ord_type == "new":
                self.ob.send(is_buy=order[self.col_idx['is_buy']],
                             qty=order[self.col_idx['qty']],
                             price=order[self.col_idx['price']],
                             uid=order[self.col_idx['uid']],
                             is_mine=is_mine,
                             timestamp=timestamp)
            elif ord_type == "cancel":
                self.ob.cancel(uid=order[self.col_idx['uid']])
            elif ord_type == "modif":
                self.ob.modif(uid=order[self.col_idx['uid']],
                              qty_down=order[self.col_idx['qty']])
            else:
                raise ValueError(f'Unexpected ordtype: {ord_type}')
            return
        else:
            self.update_ob_time(self.stop_time)
            if not is_mine:
                self.ob_idx -= 1
            return

    def update_ob_time(self, new_ob_time):

        self.ob_time = new_ob_time

    def move_until(self, stop_time):

        self.stop_time = stop_time

        while self.ob_time < stop_time:
            self.tick()

        self.update_ob_time(stop_time)
        self.stop_time = self.end_time

    def move_n_seconds(self, n_seconds):
        """ 
        """
        stop_time = min(self.ob_time + timedelta(0, n_seconds), self.end_time)
        self.move_until(stop_time)

    def move_delta(self, delta):

        stop_time = min(self.ob_time + delta, self.end_time)
        self.move_until(stop_time)

    def check_ord_in_time(self, ord_timestamp):
        """
        """
        return ord_timestamp <= self.stop_time

    def _send_historical_order(self, oborder):

        self.ob_idx += 1
        self._send_to_orderbook(oborder, is_mine=False)

    def move_historic_until(self, stop_time):

        """ 
        Params:
            stop_time (datetime):         
                
        """

        while self.ob_time <= stop_time:
            oborder = self.hist_orders[self.ob_idx]
            self._send_historical_order(oborder)

    def tick(self):
        """ Move the orderbook forward one tick (process next order)
        
            If the user has messages (new/cancel/modif) queued, it will
            decide whether to send a user or historical order based on
            their theoretical arrival time (timestamp)
        """

        # next historical order to be sent

        oborder = self.hist_orders[self.ob_idx]

        # if I have queued orders
        if self.my_queue:
            # if my order reaches the orderbook before the next historical order
            if self.my_queue[0].timestamp < oborder[self.col_idx['timestamp']]:
                my_order = self.my_queue.popleft()
                self._send_to_orderbook(my_order, is_mine=True)
                self.remove_vol_in_queue(my_order[self.col_idx['uid']])
                return

        # otherwise sent next historical order
        self._send_historical_order(oborder)

    def queue_my_new(self, is_buy, qty, price):
        """ Queue a user new order to be sent to the orderbook when time is due 
        
            Args:
                is_buy (bool): True for buy orders
                qty (int): quantity or volume
                price (float): limit price of the order
                
            Reuturns:
                An int indicating the uid that the orderbook will assign to
                it when it is introudced.
                NOTES: as the order is queued by this function, its uid does
                not exist yet in the orderbook. It will not exist until 
                the time is due and the order reaches the orderbook. Requesting
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

        self.add_vol_in_queue(self.my_last_uid, qty)

        return self.my_last_uid

    def queue_my_modif(self, uid, qty_down):
        """ Modify an order identified by its uid without loosing priority.
        Modifications can only downsize the volume. 
        If you attempt to increase the volume, the
        modification message will do nothing. Downsizing volume will 
        mantain your price-time priority in the orderbook. If you want to
        increase volume or change price, you need to cancel your previous
        order and send a new one. 
        
        Args:
            uid (int): uid of our order to be modified
            new_qty(int): new quantity. Only downsizing allowed. 
        
        """

        message = self.OrdTuple(ordtype="modif",
                                uid=uid,
                                is_buy=np.nan,
                                qty=qty_down,
                                price=np.nan,
                                timestamp=self._arrival_time())
        self.my_queue.append(message)

        leavesqty = self.ob.get(uid)['leavesqty']
        expected_vol_modified = (-1) * min(qty_down, leavesqty)
        self.add_vol_in_queue(uid, expected_vol_modified)

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

        expected_vol_cancelled = (-1) * self.ob.get(uid)['leavesqty']
        self.add_vol_in_queue(uid, expected_vol_cancelled)

    def add_vol_in_queue(self, uid, qty):

        self.in_queue[uid] = qty
        self.vol_in_queue += qty

    def remove_vol_in_queue(self, uid):

        qty = self.in_queue.pop(uid)
        self.vol_in_queue -= qty

    def ord_status(self, uid):
        """ Returns the current ob status of an order identified by its uid.
        
        Args:
            uid (int): unique order identifier
        
        NOTE: when an order is queued, its uid does not exist yet in the
        orderbook since it did not arrive there yet. Calling this function
        on a uid that is queued by not yet in the orderbook will raise a 
        KeyError exception that will have to be handled.        
        
        """
        # TODO: use ticker to select orderbook 
        return self.ob.get(uid)
    
    def price_is_mine(self, uid, is_buy):
        if uid == None:
            return
        else:
            try:
                my_price = self.ord_status(uid)['price']
            except KeyError:
                return None
        
        if is_buy:
            book = self.ob._bids.book
        else:
            book = self.ob._asks.book
            
        head = book[my_price].head
        tail = book[my_price].tail
        
        if head == tail:
            return my_price
        else:
            return 

    def _arrival_time(self):
        """ Returns the estimated time of arrival of an order
        
        """

        return self.ob_time + timedelta(0, 0, self.latency)

    def plot(self):
        trades = pd.DataFrame(self.ob.trades)
        return trades
