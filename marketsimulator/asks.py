from .side import Side

class Asks(Side):
    """
        In the Asks side, the highest priority PriceLevel is that
        with the lowest price (PriceLevels ordered by ascendent price)
    """

    def __init__(self):
        super().__init__()
    
    def price1_has_higher_priority_than_price2(self, price1, price2):
        return price1 < price2

