#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

from .festivos_and_mid_close import FESTIVOS_BURSATILES
from .festivos_and_mid_close import MARKET_CLOSE_MID_DAY


def get_n_open_day(day, n_days=1):
    bday_offset_bme = pd.offsets.CustomBusinessDay(
        holidays=FESTIVOS_BURSATILES,
        weekmask='Mon Tue Wed Thu Fri')
    n_open_day = day + n_days*bday_offset_bme
    return n_open_day


def get_open_days(start, end):
    bday_offset_bme = pd.offsets.CustomBusinessDay(
        holidays=FESTIVOS_BURSATILES,
        weekmask='Mon Tue Wed Thu Fri')
    days = pd.date_range(start=start, end=end, freq=bday_offset_bme)
    #days = pd.date_range(start=start, end=end, freq='B')
    #days = days.drop(FESTIVOS_BURSATILES, errors='ignore')
    return days


def is_trading_date(vdate):
    if len(get_open_days(vdate, vdate)) > 0:
        return True
    else:   
        return False


def get_next_market_date_es(base_date):
    date = pd.to_datetime(base_date)
    fwd_date = date + pd.Timedelta(1, unit='w')
    near_dates = get_open_days(date, fwd_date)
    return near_dates[1].normalize()


def datetime_index(start='2018-01-01',
                   end='2018-12-31'):
    """
    """
    days = get_open_days(start, end)
    year_all_range = None
    for i, day in enumerate(days):
        day_range = pd.date_range(
            start=day.replace(hour=9, minute=1, second=0),
            end=day.replace(hour=17, minute=36, second=0),
            freq='min')
        day_range = day_range.drop(
            pd.date_range(
                start=day.replace(hour=17, minute=31, second=0),
                end=day.replace(hour=17, minute=35, second=0),
                freq='min'
            )
        )
        if day in MARKET_CLOSE_MID_DAY:
            day_range = pd.date_range(
                start=day.replace(hour=9, minute=1, second=0),
                end=day.replace(hour=14, minute=6, second=0),
                freq='min'
            )
            day_range = day_range.drop(
                pd.date_range(start=day.replace(hour=14, minute=1, second=0),
                              end=day.replace(hour=14, minute=5, second=0),
                              freq='min')
            )
        if i:
            year_all_range = year_all_range.append(day_range)
        else:
            year_all_range = day_range
    return year_all_range


def datetime_index_for_2018(start='2018-01-01', 
                            end='2018-12-31'):

    start = start.strftime(format="%Y%m%d")
    end = end.strftime(format="%Y%m%d")
    days = get_open_days(start, end)
    year_all_range = None
    for i, day in enumerate(days):
        day_range = pd.date_range(
            start=day.replace(hour=9, minute=1, second=0),
            end=day.replace(hour=17, minute=36, second=0),
            freq='min'
        )
        day_range = day_range.drop(
            pd.date_range(start=day.replace(hour=17, minute=31, second=0),
                          end=day.replace(hour=17, minute=35, second=0),
                          freq='min')
        )
        if day in MARKET_CLOSE_MID_DAY:
            day_range = pd.date_range(
                start=day.replace(hour=9, minute=1, second=0),
                end=day.replace(hour=14, minute=1, second=0),
                freq='min'
            )
            day_range = day_range.drop(
                pd.date_range(
                    start=day.replace(hour=13, minute=56, second=0),
                    end=day.replace(hour=14, minute=0, second=0),
                    freq='min'
                )
            )
        if i:
            year_all_range = year_all_range.append(day_range)
        else:
            year_all_range = day_range
    return year_all_range


def datetime_index_for_ibex_for_2018(start='2018-01-01',
                                     end='2018-12-31'):
    days = get_open_days(start, end)
    year_all_range = None
    for i, day in enumerate(days):
        day_range = pd.date_range(
            start=day.replace(hour=9, minute=1, second=0),
            end=day.replace(hour=17, minute=39, second=0),
            freq='min'
        )
        day_range = day_range.drop(
            pd.date_range(start=day.replace(hour=17, minute=31, second=0),
                          end=day.replace(hour=17, minute=38, second=0),
                          freq='min')
        )
        if day in MARKET_CLOSE_MID_DAY:
            day_range = pd.date_range(
                start=day.replace(hour=9, minute=1, second=0),
                end=day.replace(hour=14, minute=9, second=0),
                freq='min'
            )
            day_range = day_range.drop(
                pd.date_range(start=day.replace(hour=14, minute=1, second=0),
                              end=day.replace(hour=14, minute=8, second=0),
                              freq='min')
            )
        if i:
            year_all_range = year_all_range.append(day_range)
        else:
            year_all_range = day_range
    return year_all_range


