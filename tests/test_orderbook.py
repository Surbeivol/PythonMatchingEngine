from core.orderbook import Orderbook


class TestOrderbook:
    """ Look in conftest.py for fixtures like bid_lmt_orders
    """

    def test_send_bid_to_empty_book(self, bid1):
        orderbook = Orderbook('ticker')
        orderbook.send(*bid1)

        assert orderbook._bids.best.price == bid1.price
        assert orderbook._bids.best.head.uid == bid1.uid
        assert orderbook._bids.best.tail.uid == bid1.uid
        assert orderbook._orders[bid1.uid].uid == bid1.uid
        assert orderbook.get(bid1.uid)['active']
        
    def test_send_ask_to_empty_book(self, ask1):
        orderbook = Orderbook('ticker')
        orderbook.send(*ask1)

        assert orderbook._asks.best.price == ask1.price
        assert orderbook._asks.best.head.uid == ask1.uid
        assert orderbook._asks.best.tail.uid == ask1.uid
        assert orderbook._orders[ask1.uid].uid == ask1.uid
        assert orderbook.get(ask1.uid)['active']
        
    def test_bid_price_time_priority(self, bid_orderbook, bid1, bid2):
        assert bid_orderbook._bids.best.head.uid == bid1.uid
        assert bid_orderbook._bids.best.head.next.uid == bid2.uid
        assert bid_orderbook._bids.best.tail.uid == bid2.uid

    def test_ask_price_time_priority(self, ask_orderbook, ask1, ask2):
        assert ask_orderbook._asks.best.head.uid == ask1.uid
        assert ask_orderbook._asks.best.head.next.uid == ask2.uid
        assert ask_orderbook._asks.best.tail.uid == ask2.uid

    def test_canceled_bid_turns_inactive(self, bid_orderbook, bid1):
        assert bid_orderbook.get(bid2.uid)['active'] 
        
        
