try:
    from ...common.path import PATH
    from ...fetch.fng.generic import Stat
    from ...fetch.wise.generic import Groups
    from ...fetch.krx.generic import Price
    from .core import RELTs, num2cap
except ImportError:
    from dev.module.fng.generic import Stat
    from dev.module.wise.generic import Groups
    from dev.module.krx.generic import Price
    from dev.task.basis.core import RELTs, num2cap
    from dev.common.path import PATH
from pandas import DataFrame
import numpy as np


class Basis(DataFrame):

    def __init__(self, offline:bool=False):
        bs = Price(offline=offline) \
             .join(Groups(offline=True))

        # Preferred stocks, suspended stocks, and other stocks
        # that are not classified due to various reasons are not included.
        # Real estate (REITs) stocks are not provided by default,
        # So they are included at our discretion.
        dump = bs[bs['sectorCode'].isna() | bs['industryCode'].isna()]
        dump = dump[~dump.index.isin(RELTs.index)]
        bs = bs[~bs.index.isin(dump.index)]
        bs.loc[RELTs.index, 'name'] = RELTs.values
        bs.loc[RELTs.index, 'sectorCode'] = 'G99'
        bs.loc[RELTs.index, 'industryCode'] = 'WI999'
        bs.loc[RELTs.index, ['sectorName', 'industryName']] = "부동산"

        # State update
        # fifty-two week price is daily updated (close-wise)
        # new tickers are also updated daily (full-state)
        st = Stat()
        st.remove([t for t in st.index if not t in bs.index])
        new = [t for t in bs.index if not t in st.index]
        if new:
            st.update(new)
        st['close'] = [bs.loc[ticker, 'close'] for ticker in st.index]
        st['high52'] = st.apply(lambda row: max(row['high52'], row['close']), axis=1)
        st['low52'] = st.apply(lambda row: min(row['low52'], row['close']), axis=1)
        st.drop(columns=["close"], inplace=True)
        st.dump()
        bs = bs.join(st)

        # Refine
        # Size is calculated by dividing the market capitalization
        # by 100 million KRW. The keyword 'PR' stands for 'Price Ratio,',
        # which represents the rate of change compared to the reference price.
        # 'PE' stands for 'Price Earnings,' indicating the price-to-earnings
        # ratio. 'PS' stands for 'Price Sales,' indicating the price-to-sales
        # ratio. 'Estimated' refers to estimated values, while 'trailing'
        # refers to values based on the most recent four consecutive quarters.
        # 'Fiscal' refers to values confirmed for the last fiscal year.
        bs['size'] = round(bs['marketCap'] / 100000000, 2)
        bs['marketCap'] = bs['size'].apply(num2cap)
        bs['high52PR'] = round(100 * (bs['close'] / bs['high52'] - 1), 2)
        bs['low52PR'] = round(100 * (bs['close'] / bs['low52'] - 1), 2)
        bs['estimatedPR'] = round(100 * (bs['close'] / bs['estPrice'] - 1), 2)
        bs['estimatedPE'] = round(bs['close'] / bs['estEps'], 2)
        bs['trailingPS'] = round(bs['size'] / bs['trailingSales'], 2)
        bs['trailingPE'] = round(bs['close'] / bs['trailingEps'], 2)
        bs['fiscalPE'] = round(bs['close'] / bs['fiscalEps'], 2)
        bs['fiscalDividends'] = round(bs['fiscalDividends'], 2)
        bs['meta'] = bs['name'] + '(' + bs.index + ')<br>' \
                     + '시가총액: ' + bs['marketCap'] + '원<br>' \
                     + '종가: ' + bs['close'].apply(lambda x: f"{x:,d}") + '원'

        invOrDivByZeroProtection = ['trailingPS', 'trailingPE', 'estimatedPE']
        for col in invOrDivByZeroProtection:
            bs.loc[(bs[col] <= 0) | (bs[col] == np.inf), col] = np.nan

        bs = bs[[
            'name',  'close', 'marketCap', 'meta', 'foreignRate', 'volume',
            'sectorCode', 'industryCode', 'sectorName', 'industryName',
            'D-1', 'W-1', 'M-1', 'M-3', 'M-6', 'Y-1',
            'high52PR', 'low52PR', 'estimatedPR',
            'stockSize', 'beta', 'floatShares',
            'trailingPS', 'trailingPE', 'fiscalPE', 'estimatedPE', 'PBR',
            'trailingEarningRatio', 'fiscalEarningRatio', 'fiscalDividends',
            'trailingSales', 'trailingEarning', 'trailingNetIncome',
            'fiscalSales', 'fiscalEarning', 'fiscalNetIncome',
            'debtRatio', 'size', 'DIV'
        ]]
        super().__init__(bs)
        return

    def dump(self) -> str:
        string = self.to_json(orient='index').replace("nan", "")
        if not PATH.SPECS.startswith('http'):
            with open(PATH.SPECS, 'w') as f:
                f.write(string)
        return string


if __name__ == "__main__":
    specs = Basis(True)
    # specs.dump()
    # specs
