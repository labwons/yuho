"""
TITLE   : BUILD MARKET (BASELINE)
AUTHOR  : SNOB
CONTACT : snob.labwons@gmail.com
ROUTINE : 15:40+09:00UTC on weekday
"""
if __name__ == "__main__":
    try:
        from ..fetch.market.state import MarketState
        from ..fetch.market.group import MarketGroup
        from ..fetch.market.spec import MarketSpec
    except ImportError:
        from src.fetch.market.state import MarketState
        from src.fetch.market.group import MarketGroup
        from src.fetch.market.spec import MarketSpec


