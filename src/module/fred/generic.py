try:
    from .core import FREDMETA
except ImportError:
    from dev.module.fred.core import FREDMETA
from datetime import datetime, timedelta
from pandas import DataFrame, Series
from pandas_datareader import get_data_fred
from typing import Dict, Union
import pandas as pd


class _fred:

    def __init__(self):
        self.__mem__: Dict[str, Union[DataFrame, Series]] = {}
        return

    def __getitem__(self, item):
        if item in self.__mem__:
            return self.__mem__
        return self.data(item)

    def __repr__(self):
        return repr(self.block)

    @property
    def block(self) -> DataFrame:
        if not self.__mem__:
            return DataFrame()
        return pd.concat(self.__mem__, axis=1)

    def data(self, symbol:str, period:int=10) -> Series:
        if not symbol in self.__mem__:
            fetched = get_data_fred(
                symbols=symbol,
                start=datetime.today() - timedelta(365 * period),
                end=datetime.today()
            )
            self.__mem__[symbol] = Series(name=symbol, index=fetched.index, data=fetched[symbol], dtype=float)
        return self.__mem__[symbol]


# Alias
Fred = _fred()

if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    print(Fred["CPIAUCNS"])
    print(Fred["UNRATE"])
    print(Fred)