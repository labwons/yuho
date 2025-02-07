try:
    from ...common.path import PATH
except ImportError:
    from src.common.path import PATH
from pandas import (
    DataFrame,
    read_json,
    to_datetime
)
from pykrx.stock import (
    get_index_ohlcv_by_date,
    get_nearest_business_day_in_a_week
)
from re import compile, search
from requests import get
from requests.exceptions import JSONDecodeError
from time import sleep, time
from typing import (
    Dict,
    List
)
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)


INDEX_CODE:Dict[str, str] = {
    '1001': 'KOSPI', '2001': 'KOSDAQ',
    'WI100': '에너지', 'WI110': '화학',
    'WI200': '비철금속', 'WI210': '철강', 'WI220': '건설', 'WI230': '기계', 'WI240': '조선', 'WI250': '상사,자본재', 'WI260': '운송',
    'WI300': '자동차', 'WI310': '화장품,의류', 'WI320': '호텔,레저', 'WI330': '미디어,교육', 'WI340': '소매(유통)',
    'WI400': '필수소비재', 'WI410': '건강관리',
    'WI500': '은행', 'WI510': '증권', 'WI520': '보험',
    'WI600': '소프트웨어', 'WI610': 'IT하드웨어', 'WI620': '반도체', 'WI630': 'IT가전', 'WI640': '디스플레이',
    'WI700': '통신서비스',
    'WI800': '유틸리티'
}


class MarketIndex(DataFrame):

    _log:List[str] = []

    def __init__(self, update:bool=True):
        stime = time()
        super().__init__(read_json(PATH.INDEX, orient='index'))
        self.index = self.index.date
        if not update:
            return

        trading_date = get_nearest_business_day_in_a_week()
        server_date = self.fetchServerDate()
        self.log = f'Begin [Market Index Fetch] @{trading_date}'

        for n, (code, name) in enumerate(INDEX_CODE.items()):
            proc = f'... ({n + 1} / {len(INDEX_CODE)}) : {code} {name} :: '
            start = self[code].dropna().index[-1]
            end = trading_date if code in ['1001', '2001'] else server_date
            if start == end:
                continue
            fetch = self.fetchWiseSeries(code, f'{start}', f'{end}')
            if fetch.empty:
                self.log = f'{proc}Fail'
                continue
            for dt in fetch.index:
                self.at[dt, code] = fetch.loc[dt, code]
            self.log = f'{proc}Success '
        self.log = f'End [Market Index Fetch] / Elapsed: {time() - stime:.2f}s'
        return

    @property
    def log(self) -> str:
        return "\n".join(self._log)

    @log.setter
    def log(self, log:str):
        self._log.append(log)

    @classmethod
    def _netDate2normDate(cls, timestamp:str):
        timestamp = int(search(r'\((\d+)\)', timestamp).group(1))
        return to_datetime(timestamp, unit='ms', utc=True) \
               .tz_convert('Asia/Seoul') \
               .date()

    @classmethod
    def fetchServerDate(cls) -> str:
        URL = 'https://www.wiseindex.com/Index/Index#/G1010.0.Components'
        pattern = compile(r"var\s+dt\s*=\s*'(\d{8})'")
        return pattern.search(get(URL).text).group(1)

    @classmethod
    def fetchWiseSeries(cls, code:str, start:str, end:str, countdown:int=5) -> DataFrame:
        if code in ['1001', '2001']:
            fetch = get_index_ohlcv_by_date(start, end, code, 'd', False)
            fetch.index = fetch.index.date
            fetch = fetch.rename(columns={"종가": code})
            return fetch

        resp = get(f'http://www.wiseindex.com/DataCenter/GridData?currentPage=1&endDT={end}&fromDT={start}&index_ids={code}&isEnd=1&itemType=1&perPage=10000&term=1')
        try:
            fetch = DataFrame(resp.json())[["TRD_DT", "IDX1_VAL1"]]
            fetch["TRD_DT"] = fetch["TRD_DT"].apply(cls._netDate2normDate)
            return fetch.rename(columns={"IDX1_VAL1": code}).set_index(keys="TRD_DT")
        except JSONDecodeError:
            if countdown == 0:
                return DataFrame()
            sleep(5)
            return cls.fetchWiseSeries(code, start, end, countdown - 1)


if __name__ == "__main__":
    marketIndex = MarketIndex(True)
    # print(marketIndex)
    print(marketIndex.log)
