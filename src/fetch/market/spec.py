from datetime import datetime
from io import StringIO
from numpy import nan
from pandas import (
    concat,
    DataFrame,
    read_html,
    read_json,
    Series
)
from pykrx.stock import get_market_cap_by_ticker
from re import DOTALL, sub
from requests import get
from requests.exceptions import JSONDecodeError, SSLError
from time import time
from typing import Dict, List, Union, Tuple
from xml.etree.ElementTree import Element, fromstring
if "PATH" not in globals():
    try:
        from ...common.path import PATH
    except ImportError:
        from src.common.path import PATH


CAP_LABEL: Dict[str, str] = {
    '종가': 'close', '시가총액': 'marketCap',
    '거래량': 'volume', '거래대금': 'amount', '상장주식수': 'shares'
}
IPO_LABEL = {
    '회사명': 'name', '종목코드': 'ticker',
    '상장일': 'ipo', '주요제품': 'products', '결산월': 'settlementMonth'
}
OVERVIEW_TAG: Dict[str, str] = {
    'high52': 'price/high52week',
    'low52': 'price/low52week',
    'beta': 'price/beta',
    'floatShares': 'price/ff_sher_rt',
    'estPrice': 'consensus/target_price',
    'estEps': 'consensus/eps'
}
STATEMENT_TAG: Dict[str, str] = {
    'consolidateAnnual': f'financial_highlight_ifrs_D/financial_highlight_annual',
    'consolidateQuarter': f'financial_highlight_ifrs_D/financial_highlight_quarter',
    'separateAnnual': f'financial_highlight_ifrs_B/financial_highlight_annual',
    'separateQuarter': f'financial_highlight_ifrs_B/financial_highlight_quarter'
}


class MarketSpec(DataFrame):
    _log: List[str] = []

    def __init__(self, update: bool = True):
        stime = time()
        if not update:
            super().__init__(read_json(PATH.SPEC, orient='index'))
            self.index = self.index.astype(str).str.zfill(6)
            return

        date = datetime.today().strftime("%Y%m%d")
        self.log = f'Begin [Market Spec Fetch] @{date}'

        market = concat([self.fetchMarketCap(date, 'KOSPI'), self.fetchMarketCap(date, 'KOSDAQ')])
        market = market[
            (market.index.isin(self.fetchIpoList().index)) &
            (~market['shares'].isna())
        ]
        market = market[market['marketCap'] >= market['marketCap'].median()]

        objs = []
        for n, ticker in enumerate(market.index):
            try:
                xml = self.fetchXml(ticker)
                obj = self.fetchOverview(xml)
                obj.name = ticker
                A, Q = self.fetchStatement(xml)
                if A.empty or Q.empty:
                    objs.append(obj)
                    continue

                Aa, Qq = self.customizeStatement(A), self.customizeStatement(Q)
                obj['trailingRevenue'] = Qq.iloc[-1]['trailingRevenue']
                obj['trailingEps'] = Qq.iloc[-1]['trailingEps']
                obj['trailingProfitRate'] = Qq.iloc[-1]['trailingProfitRate']
                obj['averageRevenueGrowth_A'] = Aa['revenueGrowth'].mean()
                obj['averageProfitGrowth_A'] = Aa['profitGrowth'].mean()
                obj['averageEpsGrowth_A'] = Aa['epsGrowth'].mean()
                obj['RevenueGrowth_A'] = Aa.iloc[-1]['revenueGrowth']
                obj['RevenueGrowth_Q'] = Qq.iloc[-1]['revenueGrowth']
                obj['ProfitGrowth_A'] = Aa.iloc[-1]['profitGrowth']
                obj['ProfitGrowth_Q'] = Qq.iloc[-1]['profitGrowth']
                obj['EpsGrowth_A'] = Aa.iloc[-1]['epsGrowth']
                obj['EpsGrowth_Q'] = Qq.iloc[-1]['epsGrowth']

                dividend = Aa['배당수익률(%)'].dropna()
                obj['fiscalDividendYield'] = dividend.values[-1] if not dividend.empty else nan

                debt = Aa['부채비율(%)'].dropna()
                obj['fiscalDebtRatio'] = debt.values[-1] if not debt.empty else nan
                objs.append(obj)
            except Exception as reason:
                self.log = f'... Failed to fetch: {ticker} / {reason}'

        super().__init__(concat(objs, axis=1).T)
        for col in self:
            self[col] = round(self[col], 4 if col == 'beta' else 2)

        self.log = f'End [Market Spec Fetch] {len(self)} Stocks / Elapsed: {time() - stime:.2f}s'
        return

    @property
    def log(self) -> str:
        return "\n".join(self._log)

    @log.setter
    def log(self, log: str):
        self._log.append(log)

    @classmethod
    def _format(cls, num) -> Union[int, float]:
        if not num:
            return nan
        try:
            return float(num) if "." in num else int(num)
        except ValueError:
            num = "".join([c for c in num if c.isdigit() or c in [".", "-"]])
            if not num or num == "." or num == "-":
                return nan
            return float(num) if "." in num else int(num)

    @classmethod
    def fetchMarketCap(cls, date: str, market:str='ALL') -> DataFrame:
        try:
            df = get_market_cap_by_ticker(date=date, market=market, alternative=True) \
                .rename(columns=CAP_LABEL)
            df.index.name = 'ticker'
            return df
        except (KeyError, RecursionError, JSONDecodeError, SSLError):
            return DataFrame(columns=list(CAP_LABEL.values()))

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
    def fetchXml(cls, ticker: str, debug: bool = False) -> Union[str, Element]:
        resp = get(url=f"http://cdn.fnguide.com/SVO2/xml/Snapshot_all/{ticker}.xml")
        resp.encoding = 'euc-kr'
        text = resp.text.replace("<![CDATA[", "").replace("]]>", "")
        text = sub(r'<business_summary>.*?</business_summary>', '', text, flags=DOTALL)
        return text if debug else fromstring(text)

    @classmethod
    def fetchOverview(cls, xml: Element) -> Series:
        data = {}
        for key, tag in OVERVIEW_TAG.items():
            ftag = xml.find(tag)
            data[key] = None if ftag is None else ftag.text
        return Series(data=data).apply(cls._format)

    @classmethod
    def fetchStatement(cls, ticker_or_xml: Union[str, Element]) -> Tuple[DataFrame, DataFrame]:
        xml = cls.fetchXml(ticker_or_xml) if isinstance(ticker_or_xml, str) else ticker_or_xml

        def _statement(tag: str) -> DataFrame:
            obj = xml.find(tag)
            if obj is None:
                return DataFrame()
            columns = [val.text for val in obj.findall('field')]
            index, data = [], []
            for record in obj.findall('record'):
                index.append(record.find('date').text)
                data.append([val.text for val in record.findall('value')])
            df = DataFrame(index=index, columns=columns, data=data)
            return df.map(cls._format)

        B_A = _statement(STATEMENT_TAG['separateAnnual'])
        D_A = _statement(STATEMENT_TAG['consolidateAnnual'])
        if B_A.empty or D_A.empty:
            return DataFrame(), DataFrame()
        if B_A.count().sum() > D_A.count().sum():
            A = B_A
            Q = _statement(STATEMENT_TAG['separateQuarter'])
        else:
            A = D_A
            Q = _statement(STATEMENT_TAG['consolidateQuarter'])
        return A, Q

    @classmethod
    def customizeStatement(cls, statement: DataFrame, include_estimated: bool = False) -> DataFrame:
        st = statement.copy()
        if not include_estimated:
            st = st[~st.index.str.endswith('(E)')].copy()
        if st[st.index.str.endswith('(P)')].count().sum() == 0:
            st = st[~st.index.str.endswith('(P)')].copy()
        else:
            st.index = st.index.str.replace(r'\(P\)', '', regex=True)
        st['trailingRevenue'] = st[st.columns[0]].rolling(window=4, min_periods=1).sum()
        st['trailingProfit'] = st['영업이익(억원)'].rolling(window=4, min_periods=1).sum()
        st['trailingEps'] = st['EPS(원)'].rolling(window=4, min_periods=1).sum()
        st['trailingProfitRate'] = st['trailingProfit'] / st['trailingRevenue'] * 100
        st['revenueGrowth'] = 100 * st[st.columns[0]].pct_change(fill_method=None)
        st['profitGrowth'] = 100 * st['영업이익(억원)'].pct_change(fill_method=None)
        st['epsGrowth'] = 100 * st['EPS(원)'].pct_change(fill_method=None)
        return st


if __name__ == "__main__":
    marketSpec = MarketSpec(True)
    # print(marketSpec)
    print(marketSpec.log)
