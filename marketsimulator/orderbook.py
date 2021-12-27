#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:
Created on Thu May 16 14:14:51 2019


@author: Francisco Merlos
"""
from datetime import datetime

from marketsimulator.prices_idx import get_band_dicts
import numpy as np
import pandas as pd
import pdb
import warnings

from config.configuration_yaml import Configuration
from .order import Order
from .pricelevel import PriceLevel
from .side import Side
from .asks import Asks
from .bids import Bids

config = Configuration()
TICKER_BANDS = config.get_liq_bands()
DEFAULT_BAND = 'band6'
AVG_TRANSACTS = config.get_trades_bands()
PX_IDXS, PRICES, MAX_TICK = get_band_dicts([1, 2, 3, 4, 5, 6])
STATS = ['price', 'vol', 'agg_ord', 'pas_ord', 'buy_init', 'timestamp']
MY_STATS = ['price', 'vol', 'my_uid', 'timestamp']
TICK_SIZE_REGIME_URL = 'https://www.emissions-euets.com/tick-size-regime'


class Orderbook:
    """ 
        An orderbook is composed of two sides. The Bid side and the Ask side.
        Each side will consist of a liked list of PriceLevels ordered by price.
        In the Asks side, the prices are ordered from lower (head) to higher (tail).
        In the Bids side, the prices go from higher (head) to lower (tail)
        Each PriceLevel consist of a linked list of Orders, ordered by arrival time
    """

    def __init__(self, ticker, max_impact=20, resilience=0):

        """        
        max_impact: maximum number of ticks to off-set historical 
            prices sent to the orderbook to reflect the effect of 
            the estimated market impact of your simulated trades.
        
        resiliance: how much you consider the market will move from the
            impact of your trades. 
            
            If set to 0, the orderbook performs a
            normal simulation without affecting historical prices by 
            the market impact.

            If set to 1, if you remove the liquidity of the book of
            a whole price level in the ask with an aggressive buy order,
            all historical prices 
            sent to the orderbook will be moved 1 tick upwards, to 
            reflect the 1-to-1 efect of your aggressive sweep
            into the prices the rest of the market would send after that
            
            Usually the market has some elasticity, so this value would
            be between 0 and 1. 
        """


        if ticker not in TICKER_BANDS:
            band = DEFAULT_BAND
            warnings.warn(f'Ticker {ticker} not found in liquidity bands'
                           ' configuration file. \n Band6 (highest liquidity'
                           ' stock) will be set as default for tick size calc.\n'
                          f' Check {TICK_SIZE_REGIME_URL} for more info')
        else:
            band = TICKER_BANDS[ticker]
            
        #        self.band_ticks = self.__class__.band_ticks[band]
        self.band_idxs = PX_IDXS[band]
        self.band_prices = PRICES[band]
        self.max_tick = MAX_TICK[band]
        self.init_size = int(AVG_TRANSACTS[band])
        self.inc = int(max(0.1 * AVG_TRANSACTS[band], 10))
        self.low_inc = 10
        # default day
        self.def_day = datetime(1970, 1, 1)
        self.max_impact = max_impact
        self.resilience = resilience
        self._bids = Bids()
        self._asks = Asks()
        self.create_stats_dict()
        # keeps track of all orders sent to the orderbook
        # allows fast access of orders status by uid
        self._orders = dict()
        self.n_my_orders = 0
        self.ntrds = 0
        self.my_ntrds = 0
        self.cumvol = 0
        self.my_cumvol = 0
        self.market_impact = 0
        self.my_cumvol_sent = 0
        self.last_px = None

    def reset_ob(self, reset_all):
        if reset_all:
            self._bids = Bids()
            self._asks = Asks()
            self.create_stats_dict()
            self._orders = dict()
        self.n_my_orders = 0
        self.ntrds = 0
        self.my_ntrds = 0
        self.cumvol = 0
        self.my_cumvol = 0
        self.market_impact = 0

    def create_stats_dict(self, stat_dict=None):
        if stat_dict == 'trades' or stat_dict is None:
            self.trades = {
                key: np.zeros(self.inc)
                for key in STATS
            }
            self.trades['timestamp'] = np.full(self.inc,
                                               self.def_day)

        if stat_dict == 'last_trades' or stat_dict is None:
            self.last_trades = {
                key: np.zeros(self.low_inc)
                for key in STATS
            }
            self.last_trades['timestamp'] = np.full(self.low_inc,
                                                    self.def_day)

        if stat_dict == 'my_trades' or stat_dict is None:
            self.my_trades = {
                key: np.zeros(self.inc)
                for key in MY_STATS
            }
            self.my_trades['timestamp'] = np.full(self.inc,
                                                  self.def_day)

        if stat_dict == 'my_last_trades' or stat_dict is None:
            self.my_last_trades = {
                key: np.zeros(self.low_inc)
                for key in MY_STATS
            }
            self.my_last_trades['timestamp'] = np.full(self.low_inc,
                                                       self.def_day)

    def inc_dict_size(self, stat_dict, inc):
        def_arr = np.zeros(inc)        
        def_day = np.full(inc, self.def_day)

        new_dict = {(key): (np.hstack([stat_dict[key], def_arr])
                            if key != 'timestamp' else np.hstack([stat_dict[key], def_day]))
                    for key in stat_dict.keys()
                    }

        return new_dict

    # Best Bid
    @property
    def best_bid(self):
        if self._bids.best_pricelevel is None:
            return None
        else:
            return self._bids.best_price, self._bids.best_vol

    # Best ask
    @property
    def best_ask(self):
        if self._asks.best_pricelevel is None:
            return None
        else:
            return self._asks.best_price, self._asks.best_vol

    def compute_vwap(self, trades):
        return (np.sum(trades['price'] * trades['vol'])
                / np.sum(trades['vol']))

    @property
    def vwap(self):
        if self.trades:
            return self.compute_vwap(self.trades)
        else:
            return np.nan

    @property
    def my_vwap(self):
        if self.my_trades:
            return self.compute_vwap(self.my_trades)
        else:
            return np.nan

    @property
    def my_pov(self):
        if self.cumvol > 0:
            return self.my_cumvol / self.cumvol
        else:
            return 0

    @property
    def trades_vol(self):
        return self.trades['vol'][:self.ntrds]

    @property
    def trades_px(self):
        return self.trades['price'][:self.ntrds]

    @property
    def trades_time(self):
        return self.trades['timestamp'][:self.ntrds]

    @property
    def my_trades_vol(self):
        return self.my_trades['vol'][:self.my_ntrds]

    @property
    def my_trades_px(self):
        return self.my_trades['price'][:self.my_ntrds]

    @property
    def my_trades_time(self):
        return self.my_trades['timestamp'][:self.my_ntrds]

    def get(self, uid):
        """  Get orderbook order by uid
            
            Params:
                uid (int): unique identifier of the Order
        
            Returns:
                order (dict): a dictionary with the order info
        
        """
        order = self._orders[uid]
        return {'uid': order.uid,
                'is_buy': order.is_buy,
                'qty': order.qty,
                'cumqty': order.cumqty,
                'leavesqty': order.leavesqty,
                'price': order.price,
                'timestamp': order.timestamp,
                'active': order.active}

    def get_new_price(self, price, n_moves):
        """ Given a price and a number of ticks of offset (n_moves)
            it returns the new price 

            The tick size will depend on the price and the liquidity
            band of the stock.

            This function allows you to move a price a certain number
            of ticks without needing to know which is the tick size
            corresponding to the stock a this price.
            
        """

        try:
            return self.band_prices[self.band_idxs[price] + n_moves]
        except (KeyError, IndexError):
            if n_moves >= 0:
                try:
                    assert price < self.band_prices[-1]
                except AssertionError:
                    pdb.set_trace()
                return price + n_moves * self.max_tick
            else:
                if price > self.band_prices[-1]:
                    n_above = (price - self.band_prices[-1]) / self.max_tick

                    if abs(n_moves) > n_above:
                        return self.band_prices[n_moves + n_above]
                    else:
                        return price + n_moves * self.max_tick
                else:
                    if price == self.band_prices[0]:
                        return price
                    else:
                        raise ValueError(f'Price {price} not found')

    def send(self, is_buy, qty, price, uid,
             is_mine=False, timestamp=datetime.now()):
        """ Send new order to orderbook
            Passive orders can't be matched and will be added to the book
            Aggressive orders are matched against opp. side's resting order
            
            Args:
                is_buy (bool): True if it is a buy order
                qty (int): initial quantity or size of the order 
                price (float): limit price of the order
                uid (int): universal identifier of the order
                is_mine (bool): False if the order corresponds to a
                historical order instead of you own orders
                uid (int)
                timestamp (float): time of processing 
                
        """
        if np.isnan(price):
            raise Exception("Price cannot be nan. Use np.Inf in needed")

        if not is_mine:
            price = self._affect_price_with_market_impact(price)
        else:
            self.n_my_orders += 1
            self.my_cumvol_sent += qty

        neword = Order(uid, is_buy, qty, price, timestamp)
        self._orders.update({uid: neword})
        while (neword.leavesqty > 0):
            if self._is_aggressive(neword):
                self._sweep_best_price(neword)
            else:
                if is_buy:
                    self._bids.add(neword)
                else:
                    self._asks.add(neword)
                return

    def _affect_price_with_market_impact(self, price):
        """ Modifies historical prices to be sent to the Orderbook by
            the cummulative effect of market impact that our own orders
            would have produced in a real trading session. 

            When we sweep a position in real life, this has an impact on
            the prices that the rest of the actors will be sending afterwards.
            We move the markets slightly with our orders.

        """
        if self.market_impact >= 1:
            nticks = min(int(self.resilience*self.market_impact),
                         self.max_impact)
            price = self.get_new_price(price=price, n_moves=nticks)
        elif self.market_impact <= -1:
            nticks = max(int(self.resilience*self.market_impact),
                         -1 * self.max_impact)
            price = self.get_new_price(price=price, n_moves=nticks)        
        return price

    def cancel(self, uid):

        """ Cancel order identified by its uid
        
        """
        order = self._orders[uid]
        if not order.active:
            return
        if order.is_buy:
            pricelevel = self._bids.pricelevel(order.price)
            pricelevel.remove(order)
            if pricelevel.is_empty():
                self._bids.remove_pricelevel(order.price)
        else:
            pricelevel = self._asks.pricelevel(order.price)
            pricelevel.remove(order)
            if pricelevel.is_empty():
                self._asks.remove_pricelevel(order.price)
    
        if uid <  0:
            self.my_cumvol_sent -= order.leavesqty
        order._cumqty = order.qty - order.leavesqty
        order.leavesqty = 0
        order.active = False
        

    def modif(self, uid, qty_down):
        """ Modify an order identified by its uid. 
        
        This transaction does not make the order lose its prite-time 
        priority in the queue, but has the limitation of only being
        able to downsize the order quantity. 
        
        For quantity increase or price modification, you need to cancel
        previous order and send a new one. 

        Args:
            uid (int): identifier of the order to be modified
            qty_down(int): quantity to substract to current order leavesqty
        
        """

        if uid in self._orders:
            prev_ord = self._orders[uid]            
            if prev_ord.leavesqty <= qty_down:
                self.cancel(uid)
            else:
                if prev_ord.uid < 0:
                    self.my_cumvol_sent -= qty_down
                prev_ord.leavesqty -= qty_down
                prev_ord.qty -= qty_down      

    def _is_aggressive(self, order):
        """ Aggressive orders are those that would be matched against
        resting orders in the book upon its arrival to the book. 
        
        Passive orders have a price that cannot result in immediate
        matching and would therefore rest in the orderbook increasing
        its liquidity. 
        
        Args:
            Order (Order): order to be checked for aggresiveness
            
        
        """

        is_agg = True
        if order.is_buy:
            if self._asks.best_pricelevel is None or \
                self._asks.best_price > order.price:
                is_agg = False
        else:
            if self._bids.best_pricelevel is None or \
                self._bids.best_price < order.price:
                is_agg = False
        return is_agg

    #    def update_metrics(self, trdpx, trdqty):
    #
    #        self.cumvol += trdqty
    #        self.cumefe += round(trdpx * trdqty, 3)
    #        self.obvwap = self.cumefe/self.cumvol

    def update_last_trades(self, stats, pos):

        for i in range(len(STATS)):

            try:
                self.last_trades[STATS[i]][pos] = stats[i]
            except IndexError:
                self.last_trades = self.inc_dict_size(self.last_trades,
                                                      inc=self.low_inc)
                self.last_trades[STATS[i]][pos] = stats[i]

    def update_my_last_trades(self, my_stats, pos):

        for i in range(len(MY_STATS)):

            try:
                self.my_last_trades[MY_STATS[i]][pos] = my_stats[i]
            except IndexError:
                self.my_last_trades = self.inc_dict_size(self.my_last_trades,
                                                         inc=self.low_inc)
                self.my_last_trades[MY_STATS[i]][pos] = my_stats[i]

    def update_trades(self, pos):

        end = self.ntrds + pos
        for stat in STATS:

            end = self.ntrds + pos
            if end < len(self.trades[stat]):
                self.trades[stat][self.ntrds:end
                ] = self.last_trades[stat][:pos]
            else:
                self.trades = self.inc_dict_size(self.trades,
                                                 inc=self.inc)
                self.trades[stat][self.ntrds:end
                ] = self.last_trades[stat][:pos]

        self.ntrds += pos

    def update_my_trades(self, pos):

        end = self.my_ntrds + pos
        for my_stat in MY_STATS:
            #            self.my_trades[my_stat] += self.my_last_trades[my_stat]
            if end < len(self.my_trades[my_stat]):
                self.my_trades[my_stat][self.my_ntrds:end
                ] = self.my_last_trades[my_stat][:pos]
            else:
                self.my_trades = self.inc_dict_size(self.my_trades,
                                                    inc=self.inc)
                self.my_trades[my_stat][self.my_ntrds:end
                ] = self.my_last_trades[my_stat][:pos]

        self.my_ntrds += pos

    def _sweep_best_price(self, order):
        """ Match Order against opposite side of the orderbook, 
        removing liquidity and generating the corresponding trades. 
        
        Args:
            order (order): order to be matched against the opp. side book
        
        """

        # TODO: Think of a different aggression effect

        my_agg_vol = 0
        ob_agg_vol = 0
        n_newtrd = 0
        n_my_newtrd = 0
        self.create_stats_dict(stat_dict='last_trades')
        restart_my_last_trades = True
        my_trade = False
        breaking = False

        if order.is_buy:
            best = self._asks.best_pricelevel
            agg_effect_side = 1
        else:
            best = self._bids.best_pricelevel
            agg_effect_side = -1

        init_best_vol = best.vol

        while order.leavesqty > 0:
            if best.head_order.leavesqty <= order.leavesqty:
                trdqty = best.head_order.leavesqty
                best.head_order.leavesqty = 0

                if best.head_order.uid < 0:
                    my_trade = True
                    my_uid = best.head_order.uid
                elif order.uid < 0:
                    my_trade = True
                    my_agg_vol += trdqty
                    my_uid = order.uid
                else:
                    my_trade = False
                    ob_agg_vol += trdqty

                price = best.price
                best_uid = best.head_order.uid

                best.pop()
                order.leavesqty -= trdqty
                if best.head_order is None:
                    # remove PriceLevel from the order's opposite side
                    self._remove_price(not order.is_buy, best.price)
                    breaking = True
            else:
                trdqty = order.leavesqty
                if best.head_order.uid < 0:
                    my_trade = True
                    my_uid = best.head_order.uid
                elif order.uid < 0:
                    my_trade = True
                    my_agg_vol += trdqty
                    my_uid = order.uid
                else:
                    my_trade = False
                    ob_agg_vol += trdqty

                price = best.price
                best_uid = best.head_order.uid

                best.head_order.leavesqty -= order.leavesqty
                order.leavesqty = 0

            if price == np.inf:
                raise ValueError("price is Infinite")

            self.cumvol += trdqty
            stats = [price, trdqty, order.uid, best_uid,
                     order.is_buy, order.timestamp]
            self.update_last_trades(stats=stats, pos=n_newtrd)
            n_newtrd += 1

            if my_trade:
                self.my_cumvol += trdqty
                if restart_my_last_trades:
                    self.create_stats_dict(stat_dict='my_last_trades')
                    restart_my_last_trades = False
                my_stats = [price, trdqty, my_uid, order.timestamp]
                self.update_my_last_trades(my_stats, pos=n_my_newtrd)
                n_my_newtrd += 1
                my_trade = False

            if breaking:
                break

        self.update_trades(pos=n_newtrd)
        if not restart_my_last_trades:
            self.update_my_trades(pos=n_my_newtrd)

        if my_agg_vol > 0:
            agg_effect = min(1., my_agg_vol / init_best_vol)
            self.market_impact += (agg_effect * agg_effect_side)

        if ob_agg_vol > 0:
            ob_correction = False
            if (self.market_impact > 0) and (agg_effect_side == -1):
                ob_correction = True
            elif (self.market_impact < 0) and (agg_effect_side == 1):
                ob_correction = True
            if ob_correction:
                agg_effect = min(1., ob_agg_vol / init_best_vol)
                pov_f = 1 - self.my_cumvol / self.cumvol
                self.market_impact += (agg_effect * agg_effect_side) * pov_f

        self.last_px = price

        return

    def _remove_price(self, is_buy, price):
        """ Remove a PriceLevel from the book
        
        Args:
            is_buy (bool): True to remove a PriceLevel from the Bids
        
        """
        if is_buy:
            self._bids.remove_pricelevel(price)
        else:
            self._asks.remove_pricelevel(price)

    def top_bidpx(self, nlevels):
        """ Returns the first nlevels of the Bids ordered by price desc
        
        Args:
            nlevels (int): number of price levels to return
        Returns:
            the first nlevels of the Bids ordered by price desc
        """

        best_bid_prices = self._bids.best_n_prices(nlevels)
        return [price if price is not None else np.nan 
                for price in best_bid_prices]


    def top_askpx(self, nlevels):
        """ Returns the first nlevels of the Ask ordered by price asc
        
        Args:
            nlevels (int): number of price levels to return
            
        Returns:
            first nlevels of the Ask ordered by price asc
        """

        best_ask_prices = self._asks.best_n_prices(nlevels)
        return [price if price is not None else np.nan 
                for price in best_ask_prices]

    def top_bids_cumvol(self, nlevels):

        nlvl_vol = 0

        try:
            best_bid = self._bids.best_price
        except:
            return nlvl_vol, None

        nlvl_vol += self._bids.book[best_bid].vol
        next_best_bidpx = best_bid
        n_px = min(nlevels, len(self._bids.book))
        px_found = 1

        while px_found < n_px:
            nextpx = self.get_new_price(next_best_bidpx, -1)
            next_best_bidpx = nextpx

            try:
                nlvl_vol += self._bids.book[next_best_bidpx].vol
                px_found += 1
            except KeyError:
                continue

        return nlvl_vol, next_best_bidpx

    def top_asks_cumvol(self, nlevels):

        nlvl_vol = 0

        try:
            best_ask = self._asks.best_price
        except:
            return nlvl_vol, None

        nlvl_vol += self._asks.book[best_ask].vol
        next_best_askpx = best_ask
        n_px = min(nlevels, len(self._asks.book))
        px_found = 1

        while px_found < n_px:
            nextpx = self.get_new_price(next_best_askpx, 1)
            next_best_askpx = nextpx

            try:
                nlvl_vol += self._asks.book[next_best_askpx].vol
                px_found += 1
            except KeyError:
                continue

        return nlvl_vol, next_best_askpx


    def top_bids(self, nlevels):
        """ Returns the first nlevels best bids of the book, including
        both price and volume in price desc order
        
        Args:
            nlevels (int): number of price levels to return
        Returns: 
            the first nlevels best bids of the book, including
            both price and volume in price desc order
        
        """
        pbids = nlevels * [np.nan]
        vbids = nlevels * [np.nan]
        try:
            best_bid = self._bids.best_price
        except:
            return [pbids, vbids]

        vbids[0] = self._bids.book[best_bid].vol
        next_best_bidpx = best_bid
        pbids[0] = next_best_bidpx
        n_px = min(nlevels, len(self._bids.book))
        px_found = 1

        while px_found < n_px:
            nextpx = self.get_new_price(next_best_bidpx, -1)
            next_best_bidpx = nextpx
            try:
                vbids[px_found] = self._bids.book[nextpx].vol
                pbids[px_found] = nextpx
                px_found += 1
            except KeyError:
                continue

        return [pbids, vbids]

    def top_asks(self, nlevels):
        """ Returns the first nlevels best asks of the book, including
        both price and volume in price asc order
        
        Args:
            nlevels (int): number of price levels to return
        Returns: 
            the first nlevels best asks of the book, including
            both price and volume in price asc order
        
        """

        pasks = nlevels * [np.nan]
        vasks = nlevels * [np.nan]
        try:
            best_ask = self._asks.best_price
        except:
            return [pasks, vasks]

        vasks[0] = self._asks.book[best_ask].vol
        next_best_askpx = best_ask
        pasks[0] = next_best_askpx
        n_px = min(nlevels, len(self._asks.book))
        px_found = 1

        while px_found < n_px:
            nextpx = self.get_new_price(next_best_askpx, 1)
            next_best_askpx = nextpx
            try:
                vasks[px_found] = self._asks.book[nextpx].vol
                pasks[px_found] = nextpx
                px_found += 1
            except KeyError:
                continue

        return [pasks, vasks]

    def __str__(self):
        pbid, vbid = self.top_bids(10)
        pask, vask = self.top_asks(10)
        df = pd.DataFrame({'vbid': vbid, 'pbid': pbid, 'pask': pask, 'vask': vask})
        return str(df)


