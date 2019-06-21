#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 22:32:03 2019

@author: paco
"""

import numpy as np
from collections import deque


class SimpleMarketMaker():
    """ Passive strategy that always has one buy and one sell 
    order close to the best bid and best ask of the market 
    in order to try to capture the spread.    
    """
    
    def __ini__(self, max_pos, child_vol):
        self.max_pos = max_pos
        self.child_vol = child_vol
        self.cur_pos = 0
        
    # TODO: complete
    # make my_last_trades and last_trades available through properties
    # make interactive plotting function available


class BuyTheBid():
    """ This execution algorithm just places one oder at the market
    best bid and moves it to try to always be in the best bid. 
    It sends one child of child_vol shares at a time and sends
    a new one as soon as the prev was filled. 
    
    """
    
    def __init__(self, care_vol, child_vol):
        self.child_vol = child_vol
        self.care_leave = care_vol
        self.leave_uid = None
        self.done = False


    def send_new_child(self, gtw):
        new_qty = min(self.child_vol, self.care_leave)                    
        self.leave_uid = gtw.queue_my_new(is_buy=True,
                                    qty=new_qty,
                                    price=gtw.ob.bbid[0])
        
        
    def eval_and_act(self, gtw):
                        
        if self.leave_uid is None:
            self.send_new_child(gtw)
        else:
            try:            
                leave_ord = gtw.ord_status(self.leave_uid)
            except KeyError:
                return
            
            # if my prev child order is filled
            if leave_ord['leavesqty'] == 0:
                # and the care is not totally filled
                if self.care_leave > 0:
                    self.send_new_child(gtw)
                else:
                    self.done = True
            # if not in best bid, modif price
            elif leave_ord['price'] != gtw.ob.bbid[0]:                
                gtw.queue_my_cancel(uid=self.leave_uid)
                self.send_new_child(gtw)
                

class Pegged():
    
    def __init__(self, is_buy, lmtpx, qty, anchor_lvl,
                 offset, gtw, quick=False, max_jump=np.Inf):
        self.is_buy = is_buy    
        self.lmtpx = lmtpx
        self.qty = qty
        self.anchor_lvl = anchor_lvl
        self.offset = offset
        self.quick = quick
        self.max_jump = max_jump
        self.done = False
        self.jumps = 0
        
        # send order
        self.uid = gtw.queue_my_new(is_buy=is_buy,
                                    qty=qty,
                                    price=self._target_px(gtw))        
        
        
    def _target_px(self, gtw):
        
        # check which price we will follow
        if self.is_buy:
            anchor_px = gtw.ob.top_bidpx(self.anchor_lvl)[self.anchor_lvl-1]
        else:
            anchor_px = gtw.ob.top_askpx(self.anchor_lvl)[self.anchor_lvl-1]
        
        # add corresponding offset in ticks                 
        pegged_px = gtw.ob.get_new_price(anchor_px, self.offset)
        
        # limit price
        if self.is_buy:
            target_px = min(pegged_px, self.lmtpx)
        else:
            target_px = max(pegged_px, self.lmtpx)
        
        return target_px
        
    
    def eval_and_act(self, gtw):
        
        # If checking it before it arrives to the market
        try:
            leave_ord = gtw.ord_status(self.uid)
        except KeyError:
            return
        
        if leave_ord['leavesqty'] == 0:
            self.done = True       
            return
        else:
            if self.jumps >= self.max_jump:
                return
            target_px = self._target_px(gtw)
            if self.quick:
                if self.is_buy:
                    if leave_ord['price'] >= target_px:
                        return
                else:
                    if leave_ord['price'] <= target_px:
                        return
                
            else:
                if leave_ord['price'] == target_px:
                    return
                
            gtw.queue_my_cancel(uid=self.uid)
            self.uid = gtw.queue_my_new(is_buy=self.is_buy,
                                    qty=self.qty,
                                    price=target_px)        
        
    

        
        
        