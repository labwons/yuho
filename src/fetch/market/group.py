from datetime import datetime
from pandas import (
    DataFrame,
    concat,
    Index,
    read_json,
)
from pykrx.stock import get_index_portfolio_deposit_file
from re import compile
from requests import get
from requests.exceptions import JSONDecodeError, SSLError
from time import sleep, time
from typing import (
    Dict,
    List
)
if "PATH" not in globals():
    try:
        from ...common.path import PATH
    except ImportError:
        from src.common.path import PATH


SECTOR_CODE:Dict[str, str] = {
    'WI100': '에너지', 'WI110': '화학',
    'WI200': '비철금속', 'WI210': '철강', 'WI220': '건설', 'WI230': '기계', 'WI240': '조선', 'WI250': '상사,자본재', 'WI260': '운송',
    'WI300': '자동차', 'WI310': '화장품,의류', 'WI320': '호텔,레저', 'WI330': '미디어,교육', 'WI340': '소매(유통)',
    'WI400': '필수소비재', 'WI410': '건강관리',
    'WI500': '은행', 'WI510': '증권', 'WI520': '보험',
    'WI600': '소프트웨어', 'WI610': 'IT하드웨어', 'WI620': '반도체', 'WI630': 'IT가전', 'WI640': '디스플레이',
    'WI700': '통신서비스',
    'WI800': '유틸리티'
}
CODE_LABEL:Dict[str, str] = {
    'CMP_CD': 'ticker', 'CMP_KOR': 'name',
    'SEC_CD': 'sectorCode', 'SEC_NM_KOR': 'sectorName',
    'IDX_CD': 'industryCode', 'IDX_NM_KOR': 'industryName',
}
REITS_CODE:Dict[str, str] = {
    "088980": "맥쿼리인프라",
    "395400": "SK리츠",
    "365550": "ESR켄달스퀘어리츠",
    "330590": "롯데리츠",
    "348950": "제이알글로벌리츠",
    "293940": "신한알파리츠",
    "432320": "KB스타리츠",
    "094800": "맵스리얼티1",
    "357120": "코람코라이프인프라리츠",
    "448730": "삼성FN리츠",
    "451800": "한화리츠",
    "088260": "이리츠코크렙",
    "334890": "이지스밸류리츠",
    "377190": "디앤디플랫폼리츠",
    "404990": "신한서부티엔디리츠",
    "417310": "코람코더원리츠",
    "400760": "NH올원리츠",
    "350520": "이지스레지던스리츠",
}


class MarketGroup(DataFrame):

    _log:List[str] = []

    def __init__(self, update:bool=True):
        stime = time()
        if not update:
            super().__init__(read_json(PATH.GROUP, orient='index'))
            self.index = self.index.astype(str).str.zfill(6)
            self.index.name = 'ticker'
            return

        date = self.fetchTradingDate()
        self.log = f'RUN [Market Group Fetch] @{date}'
        objs, size = [], len(SECTOR_CODE) + 1
        for n, (code, name) in enumerate(SECTOR_CODE.items()):
            self.log = f"... {str(n + 1).zfill(2)} / {size} : {code} {name} :: "
            n_log = len(self._log) - 1
            obj = self.fetchWiseGroup(code, date)
            objs.append(obj)
            self._log[n_log] += ("FAILED" if obj.empty else "SUCCESS")

        reits = DataFrame(data={'CMP_KOR': REITS_CODE.values(), 'CMP_CD':REITS_CODE.keys()})
        reits[['SEC_CD', 'IDX_CD', 'SEC_NM_KOR', 'IDX_NM_KOR']] \
              = ['G99', 'WI999', '리츠', '리츠']
        objs.append(reits)

        self.log = f"... {size} / {size} : WI999 리츠 :: Success"

        super().__init__(concat(objs, axis=0, ignore_index=True))
        self.drop(columns=[key for key in self if not key in CODE_LABEL], inplace=True)
        self.drop(index=self[self['SEC_CD'].isna()].index, inplace=True)
        self.rename(columns=CODE_LABEL, inplace=True)
        self.set_index(keys="ticker", inplace=True)
        self['industryName'] = self['industryName'].str.replace("WI26 ", "")

        kq, lg = self.fetchKosdaqList(self.index), self.fetchLargeCapList(self.index)
        self.loc[kq, 'name'] = self.loc[kq, 'name'] + '*'
        self.loc[lg, 'stockSize'] = 'large'
        self.log = "... Identify Tickers: Success"

        sc_mdi = self[(self['industryCode'] == 'WI330') & (self['sectorCode'] == 'G50')].index
        sc_edu = self[(self['industryCode'] == 'WI330') & (self['sectorCode'] == 'G25')].index
        sc_sw = self[(self['industryCode'] == 'WI600') & (self['sectorCode'] == 'G50')].index
        sc_it = self[(self['industryCode'] == 'WI600') & (self['sectorCode'] == 'G45')].index
        self.loc[sc_mdi, 'industryCode'], self.loc[sc_mdi, 'industryName'] = 'WI331', '미디어'
        self.loc[sc_edu, 'industryCode'], self.loc[sc_edu, 'industryName'] = 'WI332', '교육'
        self.loc[sc_sw, 'industryCode'], self.loc[sc_sw, 'industryName'] = 'WI601', '소프트웨어'
        self.loc[sc_it, 'industryCode'], self.loc[sc_it, 'industryName'] = 'WI602', 'IT서비스'

        self.log = f'END [Market Group Fetch] / Elapsed: {time() - stime:.2f}s'
        return

    @property
    def log(self) -> str:
        return "\n".join(self._log)

    @log.setter
    def log(self, log:str):
        self._log.append(log)

    @classmethod
    def fetchTradingDate(cls) -> str:
        URL = 'https://www.wiseindex.com/Index/Index#/G1010.0.Components'
        pattern = compile(r"var\s+dt\s*=\s*'(\d{8})'")
        try:
            return pattern.search(get(URL).text).group(1)
        except (JSONDecodeError, SSLError):
            return datetime.today().strftime("%Y%m%d")

    @classmethod
    def fetchWiseGroup(cls, code:str, date:str="", countdown:int=5) -> DataFrame:
        proxies = {"http": "http://117.55.202.206:3128"}
        resp = get(
            url=f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={date}&sec_cd={code}',
            proxies=proxies
        )
        if not resp.status_code == 200:
            cls._log.append(f'{" " * 8}RESPONSE STATUS: {resp.status_code}')

        try:
            return DataFrame(resp.json()['list'])
        except JSONDecodeError:
            if countdown == 0:
                cls._log.append(f'{" " * 8}JSON FORMAT ERROR')
                return DataFrame()
            sleep(5)
            return cls.fetchWiseGroup(code, date, countdown - 1)

    @classmethod
    def fetchKosdaqList(cls, _tickers:Index=None) -> List[str]:
        tickers = get_index_portfolio_deposit_file('2001')
        if not _tickers.empty:
            tickers = [ticker for ticker in _tickers if ticker in tickers]
        return tickers

    @classmethod
    def fetchLargeCapList(cls, _tickers:Index=None) -> List[str]:
        tickers = get_index_portfolio_deposit_file('2203') \
                + get_index_portfolio_deposit_file('1028')
        if not _tickers.empty:
            tickers = [ticker for ticker in _tickers if ticker in tickers]
        return tickers

if __name__ == "__main__":
    marketGroup = MarketGroup(True)
    # print(marketGroup)
    print(marketGroup.log)
