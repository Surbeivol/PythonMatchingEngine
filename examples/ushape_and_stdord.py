#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import numpy as np
from datetime import datetime, timedelta

file_name = '../data/ushape'
with open(file_name, 'rb') as f:
    ushape = pickle.load(f)

file_name = '../data/std_ord'
with open(file_name, 'rb') as f:
    std_ord = pickle.load(f)


class StdordUshape:
    
    def __init__(self, vwap=False, **kwargs):
        
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
        
        self.open_time = datetime(date.year,
                                  date.month,
                                  date.day,
                                  9, 0, 0)
        self.close_time = datetime(date.year,
                                   date.month,
                                   date.day,
                                   17, 30, 0)
        self.bin_size = timedelta(0, 300)
        self.idx = self.get_new_idx(end=start_time, start=self.open_time)
        self.next_bin_t = self.open_time + (1 + self.idx) * self.bin_size
        std_ord_array = std_ord['tickers'][ticker][date]
        ushape_array = ushape['tickers'][ticker][date]
        self.n_bines = 102  # 5-min bin
        self.std_ord_dict = dict(zip(range(102), std_ord_array))
        if vwap:
            self.ushape_dict = self.build_ushape_dict(ushape_array,
                                                      start_time,
                                                      end_time)
    
    def get_new_idx(self, end, start):
        
        return int((end - start) / self.bin_size)
    
    def get_idx(self, mkt_time):
        
        if mkt_time > self.next_bin_t:   
            self.idx = self.get_new_idx(end=mkt_time, start=self.open_time)
            self.next_bin_t = self.open_time + (1 + self.idx) * self.bin_size
        
        return self.idx
    
    def std_ord(self, mkt_time, rnd=True):
        
        self.get_idx(mkt_time)
        
        if rnd:
            return self.randomize_value(self.std_ord_dict[self.idx])
        else:
            return self.std_ord_dict[self.idx]
    
    def ushape(self, mkt_time):
        
        self.get_idx(mkt_time)
        
        return self.ushape_dict[self.idx]
    
    def std_ord_and_ushape(self, mkt_time):
        
        self.get_idx(mkt_time)
        
        return self.std_ord_dict[self.idx], self.ushape_dict[self.idx]
    
    @staticmethod
    def randomize_value(value, pct=0.1):
        rnd_f = (1 - pct) + 2 * pct * np.random.rand() 
        return rnd_f * value
    
    def build_ushape_dict(self, ushape_array, start_time, end_time):
        
        u_shape = np.zeros(self.n_bines)
        start_idx = self.get_new_idx(end=start_time, start=self.open_time)
        end_idx = self.get_new_idx(end=end_time, start=self.open_time)
        
        sub_ushape_array = ushape_array[start_idx:(end_idx+1)]
        # First and last bins are not fully used
        first_usage = 1 - (((start_time - self.open_time) / self.bin_size) % 1)
        last_usage = ((end_time - self.open_time) / self.bin_size) % 1
        sub_ushape_array[0] = first_usage * sub_ushape_array[0] 
        sub_ushape_array[-1] = last_usage * sub_ushape_array[-1]
        new_ushape = sub_ushape_array / np.sum(sub_ushape_array)
        u_shape[start_idx:(end_idx+1)] = new_ushape
        
        return dict(zip(range(self.n_bines), u_shape))
