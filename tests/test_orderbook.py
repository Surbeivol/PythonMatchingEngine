from marketsimulator.orderbook import Orderbook
from collections import namedtuple
import numpy as np


class TestOrderbook:
    """ Look in conftest.py for fixtures like bid1, ask1, full_orderbook, etc 
    """

    def test_send_bid_to_empty_book(self, bid1):
        orderbook = Orderbook('band6stock')
        orderbook.send(*bid1)

        assert orderbook._bids.best.price == bid1.price
        assert orderbook._bids.best.head.uid == bid1.uid
        assert orderbook._bids.best.tail.uid == bid1.uid
        assert orderbook._orders[bid1.uid].uid == bid1.uid
        assert orderbook.get(bid1.uid)['active']
        
    def test_send_ask_to_empty_book(self, ask1):
        orderbook = Orderbook('band6stock')
        orderbook.send(*ask1)

        assert orderbook._asks.best.price == ask1.price
        assert orderbook._asks.best.head.uid == ask1.uid
        assert orderbook._asks.best.tail.uid == ask1.uid
        assert orderbook._orders[ask1.uid].uid == ask1.uid
        assert orderbook.get(ask1.uid)['active']

    def test_get_best_bid_px_and_vol(self, bid_orderbook, bid1, bid2):
        assert bid_orderbook.bbid[0] == bid1.price
        assert bid_orderbook.bbid[1] == (bid1.qty + bid2.qty)

    def test_get_best_ask_px_and_vol(self, ask_orderbook, ask1, ask2):
        assert ask_orderbook.bask[0] == ask1.price
        assert ask_orderbook.bask[1] == (ask1.qty + ask2.qty)

    def test_get_order_by_uid(self, full_orderbook, bid3, ask4):
        bid3_order_info = full_orderbook.get(uid=bid3.uid)
        expected = {'uid': bid3.uid, 'is_buy': bid3.is_buy, 
                    'qty': bid3.qty, 'price': bid3.price,
                    'cumqty': 0, 'leavesqty': bid3.qty, 'active': True}
        for key in expected:
            assert bid3_order_info[key] == expected[key]

        ask4_order_info = full_orderbook.get(uid=ask4.uid)
        expected = {'uid': ask4.uid, 'is_buy': ask4.is_buy, 
                    'qty': ask4.qty, 'price': ask4.price,
                    'cumqty': 0, 'leavesqty': ask4.qty, 'active': True}
        for key in expected:
            assert ask4_order_info[key] == expected[key]

    def test_reset_ob_all(self, full_orderbook):
        full_orderbook.reset_ob(reset_all=True)
        assert full_orderbook.bbid is None
        assert full_orderbook.bask is None
        assert len(full_orderbook._orders) == 0

    def test_bid_price_time_priority(self, bid_orderbook, bid1, bid2):
        assert bid_orderbook._bids.best.head.uid == bid1.uid
        assert bid_orderbook._bids.best.head.next.uid == bid2.uid
        assert bid_orderbook._bids.best.tail.uid == bid2.uid

    def test_ask_price_time_priority(self, ask_orderbook, ask1, ask2):
        assert ask_orderbook._asks.best.head.uid == ask1.uid
        assert ask_orderbook._asks.best.head.next.uid == ask2.uid
        assert ask_orderbook._asks.best.tail.uid == ask2.uid

    def test_canceled_bid_turns_inactive(self, bid_orderbook, bid1):
        assert bid_orderbook.get(bid1.uid)['active'] 
        bid_orderbook.cancel(bid1.uid)
        assert not bid_orderbook.get(bid1.uid)['active'] 
        
    def test_canceled_ask_turns_inactive(self, ask_orderbook, ask1):
        assert ask_orderbook.get(ask1.uid)['active'] 
        ask_orderbook.cancel(ask1.uid)
        assert not ask_orderbook.get(ask1.uid)['active'] 
        
    def test_cancel_bestbid_sets_new_bestbid(self, bid_orderbook, bid1, bid2):
        assert bid_orderbook.bbid == (bid1.price, bid1.qty + bid2.qty)
        bid_orderbook.cancel(bid1.uid)
        assert not bid_orderbook.get(bid1.uid)['active'] 
        assert bid_orderbook.bbid == (bid2.price, bid2.qty)
        assert bid_orderbook._bids.best.head.uid == bid2.uid
        assert bid_orderbook._bids.best.tail.uid == bid2.uid
        
    def test_cancel_bestask_sets_new_bestask(self, ask_orderbook, ask1, ask2):
        assert ask_orderbook.bask == (ask1.price, ask1.qty + ask2.qty)
        ask_orderbook.cancel(ask1.uid)
        assert not ask_orderbook.get(ask1.uid)['active'] 
        assert ask_orderbook.bask == (ask2.price, ask2.qty)
        assert ask_orderbook._asks.best.head.uid == ask2.uid
        assert ask_orderbook._asks.best.tail.uid == ask2.uid
    
    def test_empty_trades(self, full_orderbook):
        assert len(full_orderbook.trades_vol) == 0
    
    def test_agg_buy_sweeps_all_positions(self, full_orderbook, ask_lmt_orders):
        ask_px_positions = [order.price for order in ask_lmt_orders]
        ask_vol_positions = [order.qty for order in ask_lmt_orders]
        ask_liquidity = sum(ask_vol_positions)
        order = namedtuple('Order', 'is_buy, qty, price, uid')
        agg_ord = order(is_buy=True, qty=5000, price=0.4, uid=11)
        full_orderbook.send(*agg_ord)
        # ask halfbook is now empty
        assert full_orderbook.bask is None
        # aggressive order swept all positions and rested in the book
        # setting the new best bid
        assert full_orderbook.bbid == (agg_ord.price, agg_ord.qty - ask_liquidity)
        # trades were done in the corresponding order by price-time priority 
        assert (full_orderbook.trades_vol == ask_vol_positions).all()
        assert (full_orderbook.trades_px == ask_px_positions).all()

    def test_agg_sell_sweeps_all_positions(self, full_orderbook, bid_lmt_orders):
        bid_px_positions = [order.price for order in bid_lmt_orders]
        bid_vol_positions = [order.qty for order in bid_lmt_orders]
        bid_liquidity = sum(bid_vol_positions)
        order = namedtuple('Order', 'is_sell, qty, price, uid')
        agg_ord = order(is_sell=False, qty=5000, price=0.1, uid=12)
        full_orderbook.send(*agg_ord)
        # bid halfbook is now empty
        assert full_orderbook.bbid is None
        # aggressive order swept all positions and rested in the book
        # setting the new best ask
        assert full_orderbook.bask == (agg_ord.price, agg_ord.qty - bid_liquidity)
        # trades were done in the corresponding order by price-time priority 
        assert (full_orderbook.trades_vol == bid_vol_positions).all()
        assert (full_orderbook.trades_px == bid_px_positions).all()
    
    def test_top_bidpx(self, full_orderbook):
        expected = [0.2, 0.19, 0.18, np.nan, np.nan]
        assert full_orderbook.top_bidpx(5) == expected

    def test_top_askpx(self, full_orderbook):
        expected = [0.3, 0.31, 0.32, np.nan, np.nan]
        assert full_orderbook.top_askpx(5) == expected

    def test_top_asks(self, full_orderbook):
        expected = [[0.3, 0.31, 0.32, np.nan, np.nan],
                    [600+700, 800+900, 1000, np.nan, np.nan]] 
        assert full_orderbook.top_asks(nlevels=5) == expected

    def test_top_bids(self, full_orderbook):
        expected = [[0.2, 0.19, 0.18, np.nan, np.nan],
                    [100+200, 300+400, 500, np.nan, np.nan]] 
        assert full_orderbook.top_bids(nlevels=5) == expected
    
    def test_top_bids_cumvol_part_of_book(self, full_orderbook):
        expected = (1000, 0.19)
        assert full_orderbook.top_bids_cumvol(2) == expected

    def test_top_asks_cumvol_part_of_book(self, full_orderbook):
        expected = (3000, 0.31)
        assert full_orderbook.top_asks_cumvol(2) == expected

    def test_top_bids_cumvol_whole_book(self, full_orderbook):
        expected = (1500, 0.18)
        assert full_orderbook.top_bids_cumvol(10) == expected

    def test_top_asks_cumvol_whole_book(self, full_orderbook):
        expected = (4000, 0.32)
        assert full_orderbook.top_asks_cumvol(10) == expected
    
    def test_modif_reduce_third_leavesqty(self, full_orderbook, ask5):
        down_qty = ask5.qty // 3 
        full_orderbook.modif(uid=ask5.uid, qty_down=down_qty)
        leavesqty = full_orderbook.get(uid=ask5.uid)['leavesqty']
        assert leavesqty == (ask5.qty - down_qty)
    
    def test_modif_reduce_all_leavesqty(self, full_orderbook, ask5):
        down_qty = ask5.qty 
        full_orderbook.modif(uid=ask5.uid, qty_down=down_qty)
        leavesqty = full_orderbook.get(uid=ask5.uid)['leavesqty']
        assert leavesqty == 0
        assert full_orderbook.get(uid=ask5.uid)['active'] == False
        
    def test_modif_reduce_more_than_leavesqty(self, full_orderbook, ask5):
        down_qty = 2 * ask5.qty 
        full_orderbook.modif(uid=ask5.uid, qty_down=down_qty)
        leavesqty = full_orderbook.get(uid=ask5.uid)['leavesqty']
        assert leavesqty == 0
        assert full_orderbook.get(uid=ask5.uid)['active'] == False
        
    def test_band6_stock_get_new_price(self):
        # we test in the price boundary of tick size change 
        orderbook = Orderbook('band6stock') 
        assert orderbook.get_new_price(5, n_moves=-1) == 4.9995
        assert orderbook.get_new_price(5, n_moves=1) == 5.001
        assert orderbook.get_new_price(10, n_moves=-1) == 9.999
        assert orderbook.get_new_price(10, n_moves=1) == 10.002
        assert orderbook.get_new_price(20, n_moves=-1) == 19.998
        assert orderbook.get_new_price(20, n_moves=1) == 20.005
        assert orderbook.get_new_price(100, n_moves=-1) == 99.99
        assert orderbook.get_new_price(100, n_moves=1) == 100.02

    def test_band5_stock_get_new_price(self):
        # we test in the price boundary of tick size change 
        orderbook = Orderbook('band5stock') 
        assert orderbook.get_new_price(5, n_moves=-1) == 4.999
        assert orderbook.get_new_price(5, n_moves=1) == 5.002
        assert orderbook.get_new_price(10, n_moves=-1) == 9.998
        assert orderbook.get_new_price(10, n_moves=1) == 10.005
        assert orderbook.get_new_price(20, n_moves=-1) == 19.995
        assert orderbook.get_new_price(20, n_moves=1) == 20.01
        assert orderbook.get_new_price(100, n_moves=-1) == 99.98
        assert orderbook.get_new_price(100, n_moves=1) == 100.05





        