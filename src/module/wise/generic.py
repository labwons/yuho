try:
    from .core import CDCOL, CDSEC, separateMediaAndEducation, separateSwAndITservice
    from .fetch import fetchWiseDate, fetchWiseGroup, fetchWiseSeries
    from ...common.calendar import Calendar
    from ...common.logger import Log
    from ...common.path import PATH
except ImportError:
    from dev.common.calendar import Calendar
    from dev.common.logger import Log
    from dev.common.path import PATH
    from dev.module.wise.core import CDCOL, CDSEC, separateMediaAndEducation, separateSwAndITservice
    from dev.module.wise.fetch import fetchWiseDate, fetchWiseGroup, fetchWiseSeries
from pandas import DataFrame
from pykrx import stock
from datetime import datetime, timedelta
from requests.exceptions import SSLError
import pandas as pd

try:
    GEN_TIME = fetchWiseDate()
except SSLError:
    GEN_TIME = (datetime.today() - timedelta(days=1)).date()
class Groups(DataFrame):

    def __init__(self, offline:bool=True):
        if offline:
            super().__init__(pd.read_json(PATH.GROUP, orient='index'))
            self.index = self.index.astype(str).str.zfill(6)
            self.index.name = 'ticker'
            return

        Log.active = not offline
        Log.append(f"Fetching WISE Group @Date: {GEN_TIME}\n")

        objs = []
        for n, (code, name) in enumerate(CDSEC.items()):
            Log.append(f"... ({n + 1} / {len(CDSEC)}) {code} / {name}: ")
            fetch = fetchWiseGroup(code, GEN_TIME.strftime("%Y%m%d"))
            if fetch.empty:
                Log.append("Failed\n")
                continue
            if code == 'WI330':
                fetch = separateMediaAndEducation(fetch)
            if code == 'WI600':
                fetch = separateSwAndITservice(fetch)
            objs.append(fetch)
            Log.append("Success\n")
        wrap = pd.concat(objs, axis=0, ignore_index=True)[CDCOL.keys()]
        wrap["IDX_NM_KOR"] = wrap["IDX_NM_KOR"].str.replace("WI26 ", "")
        wrap = wrap.rename(columns=CDCOL).set_index("ticker")

        kq = stock.get_index_portfolio_deposit_file('2001')
        lg = stock.get_index_portfolio_deposit_file('2203') \
           + stock.get_index_portfolio_deposit_file('1028')
        kq = [ticker for ticker in kq if ticker in wrap.index]
        lg = [ticker for ticker in lg if ticker in wrap.index]
        wrap.loc[kq, 'name'] = wrap.loc[kq, 'name'] + '*'
        wrap.loc[lg, 'stockSize'] = 'large'
        super().__init__(wrap)
        Log.append("--- \n\n")
        return

    def dump(self) -> str:
        string = self.to_json(orient='index').replace("nan", "")
        if not PATH.GROUP.startswith('http'):
            with open(PATH.GROUP, 'w') as f:
                f.write(string)
        return string


class Indices(DataFrame):

    def __init__(self, offline:bool=True):
        df = pd.read_json(PATH.INDEX, orient='index')
        df.index = df.index.date
        if offline:
            super().__init__(df)
            return

        Log.active = not offline
        Log.append(f"\nFetching INDEX @Date: {GEN_TIME}\n")
        df = df.iloc[:-1]
        for n, col in enumerate(df):
            name = CDSEC[col] if col in CDSEC else col
            Log.append(f"... ({n + 1} / {len(df.columns)}) {col} / {name}: ")
            latest = Calendar[-1] if col in ["KOSPI", "KOSDAQ"] else GEN_TIME
            index = df[col].dropna()
            if latest == index.index[-1]:
                continue

            if col in ["KOSPI", "KOSDAQ"]:
                ticker = {'KOSPI':'1001', 'KOSDAQ':'2001'}[col]
                fetch = stock.get_index_ohlcv_by_date(
                    ticker=ticker,
                    fromdate=str(index.index[-1]),
                    todate=str(Calendar[-1]),
                    name_display=False
                ).rename(columns={'종가': col})
                fetch.index = fetch.index.date
            else:
                fetch = fetchWiseSeries(
                    code=col,
                    fromDT=str(index.index[-1]),
                    endDT=GEN_TIME.strftime("%Y-%m-%d")
                )
            for i in fetch.index:
                df.loc[i, col] = fetch.loc[i, col]
            Log.append("Success\n")
        super().__init__(df)
        Log.append("--- \n\n")
        return

    def dump(self) -> str:
        string = self.to_json(orient='index').replace("nan", "")
        if not PATH.INDEX.startswith('http'):
            with open(PATH.INDEX, 'w') as f:
                f.write(string)
        return string
