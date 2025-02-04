try:
    from ...common.web import Web
    from .core import str2num
except ImportError:
    from dev.module.fng.core import str2num
    from dev.common.web import Web
from pandas import DataFrame, Series
from requests.exceptions import JSONDecodeError, SSLError
import pandas as pd
import xml.etree.ElementTree as ET
import requests, io


def fetchIpo() -> DataFrame:
    CDIPO = {
        '회사명':'name', '종목코드':'ticker',
        '상장일':'ipo', '주요제품':'products', '결산월':'settlementMonth'
    }
    _url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
    try:
        resp = io.StringIO(requests.get(_url).text)
        df = pd.read_html(io=resp, encoding='euc-kr')[0][CDIPO.keys()]
        df = df.rename(columns=CDIPO).set_index(keys='ticker').copy()
        df.index = df.index.astype(str).str.zfill(6)
        return df
    except (KeyError, RecursionError, JSONDecodeError, SSLError):
        return DataFrame(columns=list(CDIPO.values()))

def fetchOverviewSpec(ticker:str) -> Series:
    url = f"http://cdn.fnguide.com/SVO2/xml/Snapshot_all/{ticker}.xml"
    root = ET.fromstring(Web.text(url, encoding='euc-kr'))
    tags = {
        # 'date': 'price/date',
        'high52': 'price/high52week',
        'low52': 'price/low52week',
        'beta': 'price/beta',
        'floatShares': 'price/ff_sher_rt',
        'estPrice': 'consensus/target_price',
        'estEps': 'consensus/eps'
    }
    data = {}
    for key, tag in tags.items():
        elem = root.find(tag)
        data[key] = None if elem is None else elem.text
    return Series(data=data, name=ticker).apply(str2num)

def fetchOverviewStatement(
        ticker:str,
        report:str='consolidated',
        period:str='annual',
        include_estimated:bool=True
    ) -> DataFrame:
    if not (report.lower().startswith('con') or report.lower().startswith('sep')):
        raise KeyError(f'Invalid Argument for @report: {report}')
    if not (period.lower().startswith('a') or period.lower().startswith('q')):
        raise KeyError(f'Invalid Argument for @period: {period}')

    ifrs = 'D' if report.lower().startswith('con') else 'B'
    stamp = 'annual' if period.lower().startswith('a') else 'quarter'
    tag = f'financial_highlight_ifrs_{ifrs}/financial_highlight_{stamp}'

    url = f"http://cdn.fnguide.com/SVO2/xml/Snapshot_all/{ticker}.xml"
    root = ET.fromstring(Web.text(url, encoding='euc-kr'))
    if root.find(tag) is None:
        return DataFrame()
    cols = [val.text for val in root.findall(f'{tag}/field')]
    index, data = [], []
    for elem in root.findall(f'{tag}/record'):
        index.append(elem.find('date').text)
        data.append([val.text for val in elem.findall('value')])
    df = DataFrame(index=index, columns=cols, data=data)
    if not include_estimated:
        df = df[(~df.index.str.endswith('(E)')) & (~df.index.str.endswith('(P)'))]
    return df.applymap(str2num)


if __name__ == "__main__":
    tester = '005930'
    fetchOverviewSpec(tester)
    fetchOverviewStatement(tester, 'con', 'q', False)
