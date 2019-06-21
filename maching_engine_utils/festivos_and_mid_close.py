#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

FESTIVOS_BURSATILES = [
    # 2015
    pd.Timestamp(year=2015, month=1, day=1),
    pd.Timestamp(year=2015, month=4, day=3),
    pd.Timestamp(year=2015, month=4, day=6),
    pd.Timestamp(year=2015, month=5, day=1),
    pd.Timestamp(year=2015, month=12, day=25),
    # 2016
    pd.Timestamp(year=2016, month=1, day=1),
    pd.Timestamp(year=2016, month=3, day=25),
    pd.Timestamp(year=2016, month=3, day=28),
    pd.Timestamp(year=2016, month=12, day=26),
    # 2017
    pd.Timestamp(year=2017, month=4, day=14),
    pd.Timestamp(year=2017, month=4, day=17),
    pd.Timestamp(year=2017, month=5, day=1),
    pd.Timestamp(year=2017, month=12, day=25),
    pd.Timestamp(year=2017, month=12, day=26),
    # 2018
    pd.Timestamp(year=2018, month=1, day=1),
    pd.Timestamp(year=2018, month=3, day=30),
    pd.Timestamp(year=2018, month=4, day=2),
    pd.Timestamp(year=2018, month=5, day=1),
    pd.Timestamp(year=2018, month=12, day=25),
    pd.Timestamp(year=2018, month=12, day=26),
    # 2019
    pd.Timestamp(year=2019, month=1, day=1),
    pd.Timestamp(year=2019, month=4, day=19),
    pd.Timestamp(year=2019, month=4, day=22),
    pd.Timestamp(year=2019, month=5, day=1),
    pd.Timestamp(year=2019, month=12, day=25),
    pd.Timestamp(year=2019, month=12, day=26),
]

MARKET_CLOSE_MID_DAY = [
    pd.Timestamp(year=2015, month=12, day=31),
    pd.Timestamp(year=2015, month=12, day=24),
    pd.Timestamp(year=2016, month=12, day=31),
    pd.Timestamp(year=2016, month=12, day=24),
    pd.Timestamp(year=2017, month=12, day=31),
    pd.Timestamp(year=2017, month=12, day=24),
    pd.Timestamp(year=2018, month=12, day=31),
    pd.Timestamp(year=2018, month=12, day=24),
    pd.Timestamp(year=2019, month=12, day=24),
    pd.Timestamp(year=2019, month=12, day=31),
]
