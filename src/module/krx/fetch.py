try:
    from ...common.calendar import Calendar
except ImportError:
    from dev.common.calendar import Calendar
from pandas import DataFrame, Series
from pykrx import stock
from requests.exceptions import JSONDecodeError, SSLError
from typing import Iterable
import pandas as pd


def fetchKonex() -> list:
    try:
        df = stock.get_market_cap_by_ticker(date=str(Calendar), market='KONEX')
        return df.index.tolist()
    except (KeyError, RecursionError, JSONDecodeError, SSLError):
        return []

def fetchMarketCap() -> DataFrame:
    CDCAP = {
        '종가':'close', '시가총액':'marketCap',
        '거래량':'volume', '거래대금':'amount', '상장주식수':'shares'
    }
    try:
        df = stock.get_market_cap_by_ticker(
            date=str(Calendar),
            market='ALL',
        ).rename(columns=CDCAP)
        df.index.name = 'ticker'
        return df
    except (KeyError, RecursionError, JSONDecodeError, SSLError):
        return DataFrame(columns=list(CDCAP.values()))

def fetchKrxMultiples() -> DataFrame:
    COLS = ['PER', 'PBR', 'DIV']
    try:
        df = stock.get_market_fundamental(
            date=str(Calendar),
            market="ALL",
        )[COLS]
        df.index.name = "ticker"
        return df
    except (KeyError, RecursionError, JSONDecodeError, SSLError):
        return DataFrame(columns=COLS)

def fetchForeignRate() -> Series:
    try:
        df = stock.get_exhaustion_rates_of_foreign_investment(
            date=str(Calendar),
            market='ALL'
        )["지분율"]
        df.index.name, df.name = 'ticker', 'foreignRate'
        return round(df.astype(float), 2)
    except (KeyError, RecursionError, JSONDecodeError, SSLError):
        return Series(name="foreignRate")

def fetchReturns(tickers:Iterable=None) -> DataFrame:
    def _base_return() -> DataFrame:
        _objs = {}
        _base = stock.get_market_ohlcv_by_ticker(date=str(Calendar), market="ALL")['종가']
        for interval, date in Calendar:
            _fetch = stock.get_market_ohlcv_by_ticker(date=str(date), market="ALL")['종가']
            _objs[interval] = round(100 * (_base / _fetch - 1), 2)
        return pd.concat(objs=_objs, axis=1)

    def _update_return(_tickers:Iterable) -> DataFrame:
        fromdate, todate = Calendar['Y-2'].strftime("%Y%m%d"), str(Calendar)
        objs = []
        for ticker in _tickers:
            src = stock.get_market_ohlcv_by_date(ticker=ticker, fromdate=fromdate, todate=todate)['종가']
            obj = {"ticker": ticker}
            for interval, date in Calendar:
                src_copy = src[src.index.date >= date]
                obj[interval] = round(100 * (src_copy.iloc[-1] / src_copy.iloc[0] - 1), 2)
            objs.append(obj)
        return DataFrame(objs).set_index(keys='ticker')

    _shares = pd.concat({dt: stock.get_market_cap_by_ticker(
        date=str(Calendar[dt]),
        market='ALL',
    )['상장주식수'] for dt in ['D-0', 'Y-1']}, axis=1)
    _shares = _shares[~_shares['D-0'].isna()]
    if not tickers is None:
        _shares = _shares[_shares.index.isin(tickers)]

    _normal = _shares[_shares['D-0'] == _shares['Y-1']].index
    _change = _shares[_shares['D-0'] != _shares['Y-1']].index
    _return = _base_return()
    return pd.concat([_return[_return.index.isin(_normal)], _update_return(_change)])