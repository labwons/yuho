from datetime import datetime, timedelta
from io import StringIO
from pandas import (
    concat,
    DataFrame,
    Index,
    read_html,
    read_json,
)
from pykrx.stock import (
    get_exhaustion_rates_of_foreign_investment,
    get_nearest_business_day_in_a_week,
    get_market_cap_by_ticker,
    get_market_fundamental,
    get_market_ohlcv_by_date
)
from requests import get
from requests.exceptions import JSONDecodeError, SSLError
from time import time
from typing import Dict, Iterable, List

if "PATH" not in globals():
    try:
        from ...common.path import PATH
    except ImportError:
        from src.common.path import PATH

IPO_LABEL: Dict[str, str] = {
    '회사명': 'name', '종목코드': 'ticker',
    '상장일': 'ipo', '주요제품': 'products', '결산월': 'settlementMonth'
}
CAP_LABEL: Dict[str, str] = {
    '종가': 'close', '시가총액': 'marketCap',
    '거래량': 'volume', '거래대금': 'amount', '상장주식수': 'shares'
}
MUL_LABEL: Dict[str, str] = {
    'PER': 'PER', 'PBR': 'PBR', 'DIV': 'dividendYield'
}
PCT_LABEL: Dict[str, str] = {"지분율": 'foreignRate'}
PRC_LABEL: Dict[str, str] = {
    "시가": "open", "고가": "high", "저가": "low", "종가": "close",
    "거래량": "volume", "거래대금": "amount"
}
INTERVALS: Dict[str, int] = {
    'D+0': 0, 'D-1': 1, 'W-1': 7,
    'M-1': 30, 'M-3': 91, 'M-6': 182, 'Y-1': 365
}


class MarketState(DataFrame):
    _log: List[str] = []

    def __init__(self, update: bool = True):
        stime = time()
        if not update:
            super().__init__(read_json(PATH.STATE, orient='index'))
            self.index = self.index.astype(str).str.zfill(6)
            return

        date = get_nearest_business_day_in_a_week()
        self.log = f'Begin [Market State Fetch] @{date}'

        fdef = [self.fetchMarketCap, self.fetchMultiples, self.fetchForeignRate]
        ks = concat([func(date, 'KOSPI') for func in fdef], axis=1)
        ks['market'] = 'kospi'
        self.log = f'... Fetch KOSPI Market State :: {"Fail" if ks.empty else "Success"}'
        kq = concat([func(date, 'KOSDAQ') for func in fdef], axis=1)
        kq['market'] = 'kosdaq'
        self.log = f'... Fetch KOSDAQ Market State :: {"Fail" if kq.empty else "Success"}'
        market = concat([ks, kq], axis=0)

        market = market[
            (~market.index.isin(self.fetchKonexList(date))) &
            (market.index.isin(self.fetchIpoList().index)) &
            (~market['shares'].isna())
            ]
        market = market[market['marketCap'] >= market['marketCap'].median()]

        returns = self.fetchReturns(date, market.index)
        self.log = f'... Fetch Returns :: {"Fail" if returns.empty else "Success"}'

        merge = returns.join(market, how='left')
        merge = merge.sort_values(by='marketCap', ascending=False)
        super().__init__(merge)

        self.log = f'End [Market State Fetch] / Elapsed: {time() - stime:.2f}s'
        return

    @property
    def log(self) -> str:
        return "\n".join(self._log)

    @log.setter
    def log(self, log: str):
        self._log.append(log)

    @classmethod
    def fetchKonexList(cls, date: str) -> Index:
        try:
            return get_market_cap_by_ticker(date=date, market='KONEX').index
        except (KeyError, RecursionError, JSONDecodeError, SSLError):
            return Index([])

    @classmethod
    def fetchIpoList(cls) -> DataFrame:
        _url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
        try:
            resp = StringIO(get(_url).text)
            df = read_html(io=resp, encoding='euc-kr')[0][IPO_LABEL.keys()] \
                .rename(columns=IPO_LABEL) \
                .set_index(keys='ticker')
            df.index = df.index.astype(str).str.zfill(6)
            return df
        except (KeyError, RecursionError, JSONDecodeError, SSLError):
            return DataFrame(columns=list(IPO_LABEL.values()))

    @classmethod
    def fetchMarketCap(cls, date: str, market: str = 'ALL') -> DataFrame:
        try:
            df = get_market_cap_by_ticker(date=date, market=market, alternative=True) \
                .rename(columns=CAP_LABEL)
            df.index.name = 'ticker'
            return df
        except (KeyError, RecursionError, JSONDecodeError, SSLError):
            return DataFrame(columns=list(CAP_LABEL.values()))

    @classmethod
    def fetchMultiples(cls, date: str, market: str = 'ALL') -> DataFrame:
        try:
            df = get_market_fundamental(date=date, market=market) \
                .rename(columns=MUL_LABEL)
            df.index.name = "ticker"
            return df[MUL_LABEL.values()]
        except (KeyError, RecursionError, JSONDecodeError, SSLError):
            return DataFrame(columns=list(MUL_LABEL.values()))

    @classmethod
    def fetchForeignRate(cls, date: str, market: str = 'ALL') -> DataFrame:
        try:
            df = get_exhaustion_rates_of_foreign_investment(date=date, market=market) \
                .rename(columns=PCT_LABEL)
            df.index.name = 'ticker'
            return round(df[PCT_LABEL.values()].astype(float), 2)
        except (KeyError, RecursionError, JSONDecodeError, SSLError):
            return DataFrame(columns=list(PCT_LABEL.values()))

    @classmethod
    def fetchReturns(cls, date: str, tickers: Iterable = None) -> DataFrame:
        tdate = datetime.strptime(date, "%Y%m%d")
        intv = {key: tdate - timedelta(val) for key, val in INTERVALS.items()}
        objs = {
            key: cls.fetchMarketCap(val.strftime("%Y%m%d"))
            for key, val in intv.items()
        }
        base = concat(objs, axis=1)
        base = base[base.index.isin(tickers)]

        returns = concat({
            dt: base[dt]['close'] / base['D+0']['close'] - 1 for dt in objs
        }, axis=1)
        returns.drop(columns=['D+0'], inplace=True)

        diff = base[base['Y-1']['shares'] != base['D+0']['shares']].index
        fdate = (tdate - timedelta(380)).strftime("%Y%m%d")
        for ticker in diff:
            ohlc = get_market_ohlcv_by_date(fromdate=fdate, todate=date, ticker=ticker)
            for interval in returns.columns:
                ohlc_copy = ohlc[ohlc.index >= intv[interval]]['종가']
                returns.loc[ticker, interval] = ohlc_copy.iloc[-1] / ohlc_copy.iloc[0] - 1
        return round(100 * returns, 2)


if __name__ == "__main__":
    marketState = MarketState(True)
    # print(marketState)
    print(marketState.log)

