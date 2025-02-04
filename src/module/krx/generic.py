try:
    from ...common.path import PATH
    from ...common.calendar import Calendar
    from ...common.logger import Log
    from .fetch import fetchKonex, fetchReturns, fetchForeignRate, fetchKrxMultiples, fetchMarketCap
except ImportError:
    from dev.module.krx.fetch import fetchKonex, fetchReturns, fetchForeignRate, fetchKrxMultiples, fetchMarketCap
    from dev.common.path import PATH
    from dev.common.calendar import Calendar
    from dev.common.logger import Log
from pandas import DataFrame
import pandas as pd


class Price(DataFrame):

    def __init__(self, offline:bool=True):
        if offline:
            super().__init__(pd.read_json(PATH.PRICE, orient='index'))
            return

        Log.active = not offline
        Log.append(f"Fetching Market Specification @Date: {Calendar}\n")

        Log.append(f"... Market Cap: ")
        df1 = fetchMarketCap()
        Log.append("Failed\n" if df1.empty else "Success\n")

        Log.append(f"...Multiples: ")
        df2 = fetchKrxMultiples()
        Log.append("Failed\n" if df2.empty else "Success\n")

        Log.append(f"... Foreign Rate: ")
        df3 = fetchForeignRate()
        Log.append("Failed\n" if df3.empty else "Success\n")

        df = pd.concat([df1, df2, df3], axis=1)
        df = df[~df.index.isin(fetchKonex())]
        if "marketCap" in df:
            df = df[df['marketCap'] >= df['marketCap'].median()]
        tickers = df.index.values

        Log.append(f"... Returns: ")
        df4 = fetchReturns(tickers)
        df = df.join(df4, how='left')
        Log.append("Failed\n" if df4.empty else "Success\n")

        super().__init__(df)
        return

    def dump(self) -> str:
        string = self.to_json(orient='index').replace("nan", "")
        if not PATH.PRICE.startswith('http'):
            with open(PATH.PRICE, 'w') as f:
                f.write(string)
        return string

# specs = Price(offline=False)
# specs.dump()