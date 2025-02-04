from datetime import datetime, timedelta
from pytz import timezone
from pykrx import stock
from typing import Union
from yfinance import Ticker
import pandas as pd


class Calendar(object):

    # Set Current Time-Zone
    NOW = datetime.now(timezone('Asia/Seoul'))

    # Time Span
    SPAN = []

    # Display Format
    FORMAT = "%Y-%m-%d"

    def __init__(self):

        self.__mem__ = {}

        # Fetching Time-span of the Market
        # looking for 5year market data. reference point is executive datetime(@NOW).
        # resourced from pykrx(; NAVER, KRX) or yfinance(; Yahoo Finance).
        # pykrx is prior to yfinance (incase of server block).
        # datetime interval (or frequency) is 1 day, weekend and holiday not included(automatic)
        _start = self.NOW - timedelta(days=365 * 5)
        _basis = stock.get_market_ohlcv_by_date(
            fromdate=_start.strftime("%Y%m%d"),
            todate=self.NOW.strftime("%Y%m%d"),
            ticker='005930',
            freq='d',
            adjusted=True,
            name_display=False
        )
        if _basis.empty:
            _basis = Ticker('005930.KS').history(
                start=_start.date(),
                end=self.NOW.date(),
                interval='1d'
            )
        else:
            if not self.NOW.strftime("%A") in ['Saturday', 'Sunday']:
                if 930 <= int(self.NOW.strftime("%H%M")) < 1531:
                    _basis = _basis.iloc[:-1]
        self.SPAN = _basis.index.date
        return

    @property
    def format(self) -> str:
        return self.FORMAT

    @format.setter
    def format(self, _format:str):
        self.FORMAT = _format

    def __contains__(self, date:Union[str, datetime, datetime.date]) -> bool:
        if isinstance(date, str):
            if "-" in date:
                date = datetime.strptime(date, "%Y-%m-%d")
            elif "." in date:
                date = datetime.strptime(date, "%Y.%m.%d")
            else:
                date = datetime.strptime(date, "%Y%m%d")
        if isinstance(date, datetime):
            date = date.date()
        return date in self.SPAN

    def __iter__(self) -> iter:
        for interval in ('D-1', 'W-1', 'M-1', 'M-3', 'M-6', 'Y-1'):
            yield interval, self[interval]

    def __len__(self) -> int:
        return len(self.SPAN)

    def __getitem__(self, n_or_interval:Union[int, str]) -> datetime.date:
        if isinstance(n_or_interval, int):
            return self.SPAN[n_or_interval]
        if not '-' in n_or_interval:
            raise KeyError(f'Wrong interval format: {n_or_interval}')
        if n_or_interval in self.__mem__:
            return self.__mem__[n_or_interval]
        interval = n_or_interval.lower()
        if interval.startswith('d'):
            key = 'days'
        elif interval.startswith('w'):
            key = 'weeks'
        elif interval.startswith('m'):
            key = 'months'
        elif interval.startswith('y'):
            key = 'years'
        else:
            raise KeyError(f'Wrong interval format: {n_or_interval}')

        offset = (self[-1] - pd.DateOffset(**{key: int(interval[2:])})).date()
        while not offset in self:
            offset = (offset - pd.DateOffset(days=1)).date()
        self.__mem__[n_or_interval] = offset
        return offset

    def __str__(self) -> str:
        return self[-1].strftime(self.format)


# Alias Override
Calendar = Calendar()


if __name__ == "__main__":
    print(Calendar)