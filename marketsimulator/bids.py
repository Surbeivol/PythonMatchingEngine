from .side import Side
from .pricelevel import PriceLevel

class Bids(Side):
    """
        In the Bids side, the highest priority PriceLevel is that
        with the highest price (PriceLevels ordered by descendent price)
    """

    def __init__(self):
        super().__init__()
   
    def price1_has_higher_priority_than_price2(self, price1, price2):
        return price1 > price2


                


        
        
                
    