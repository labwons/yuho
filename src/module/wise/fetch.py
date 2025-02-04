try:
    from .core import convertNet2Date
except ImportError:
    from dev.module.wise.core import convertNet2Date
from datetime import datetime
from pandas import DataFrame, Series
from requests.exceptions import JSONDecodeError
import requests, re, time


def fetchWiseDate() -> datetime.date:
    _url = 'https://www.wiseindex.com/Index/Index#/G1010.0.Components'
    pattern = re.compile(r"var\s+dt\s*=\s*'(\d{8})'")
    fetched = pattern.search(requests.get(_url).text)
    return datetime.strptime(fetched.group(1), "%Y%m%d").date()

def fetchWiseGroup(code:str, date:str="", countdown:int=5) -> DataFrame:
    _url = 'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt=%s&sec_cd=%s'
    date = fetchWiseDate().strftime("%Y%m%d") if date == "" else date
    resp = requests.get(_url % (date, code))
    try:
        return DataFrame(resp.json()['list'])
    except JSONDecodeError:
        if countdown > 0:
            time.sleep(5)
            return fetchWiseGroup(code, date, countdown - 1)
        return DataFrame()

def fetchWiseSeries(code:str, fromDT:str="", endDT:str="", countdown:int=5) -> Series:
    _url = 'http://www.wiseindex.com/DataCenter/GridData?currentPage=1&endDT=%s&fromDT=%s&index_ids=%s&isEnd=1&itemType=1&perPage=10000&term=1'
    edt = endDT if endDT else fetchWiseDate().strftime("%Y-%m-%d")
    sdt = fromDT if fromDT else '2000-01-01'
    resp = requests.get(_url % (edt, sdt, code))
    try:
        df = DataFrame(resp.json())[["TRD_DT", "IDX1_VAL1"]]
        df["TRD_DT"] = df["TRD_DT"].apply(convertNet2Date)
        return df.rename(columns={"IDX1_VAL1": code, "TRD_DT": "date"}).set_index("date")
    except JSONDecodeError:
        if countdown > 0:
            time.sleep(5)
            return fetchWiseSeries(code, sdt, edt, countdown - 1)
        return Series()