try:
    from ...fetch.market.state import MarketState
    from ...fetch.market.group import MarketGroup
    from ...fetch.market.spec import MarketSpec
except ImportError:
    from src.fetch.market.state import MarketState
    from src.fetch.market.group import MarketGroup
    from src.fetch.market.spec import MarketSpec
from numpy import nan
from pandas import (
    DataFrame,
    read_json
)


class MarketBaseline(DataFrame):

    def __init__(self, update:bool=True):
        # merge = MarketState(update=update)
        merge = MarketState(update=False) \
                .join(MarketSpec(update=False), how='left')\
                .join(MarketGroup(update=False), how='left')

        super().__init__(merge)

        self['high52'] = self[['close', 'high52']].max(axis=1)
        self['low52'] = self[['close', 'low52']].min(axis=1)
        self['pct52wHigh'] = 100 * (self['close'] / self['high52'] - 1)
        self['pct52wLow'] = 100 * (self['close'] / self['low52'] - 1)
        self['pctEstimated'] = 100 * (self['close'] / self['estPrice'] - 1)
        self['estimatedPE'] = self['close'] / self['estEps']
        self['trailingPS'] = (self['marketCap'] / 1e+8) / self['trailingRevenue']
        self['trailingPE'] = self['close'] / self['trailingEps']
        return


if __name__ == "__main__":
    from pandas import set_option

    set_option('display.expand_frame_repr', False)

    baseline = MarketBaseline()
    print(baseline)
