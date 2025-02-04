try:
    from src.common.web import Web
except ImportError:
    from dev.common.web import Web
from datetime import datetime
from pandas import DataFrame, Series, isna
from numpy import nan
from typing import Union


class naver:
    """
    Fetch source data from Naver

    @currentPrice
        type        : Union[int, float]
        description : current price (close)

    @resemblances
        type        : DataFrame
        description : current price (close)
        columns     : ['종목명', '현재가', '등락률', '시가총액(억)', '외국인비율(%)', '매출액(억)', '영업이익(억)',
                       '조정영업이익(억)', '영업이익증가율(%)', '당기순이익(억)', '주당순이익(원)', 'ROE(%)', 'PER(%)',
                       'PBR(배)']
        example     :
                        종목명  현재가 등락률 시가총액(억) 외국인비율(%)  매출액(억) 영업이익(억)  ...  PER(%) PBR(배)
            058470    리노공업  143800  -1.57        21918         37.25         751          336  ...   21.69    4.35
            005930    삼성전자   70600   0.14      4214666         53.21      600055         6685  ...   13.47    1.37
            000660  SK하이닉스  132000   1.15       960963         52.59       73059       -28821  ...  -11.73    1.58
            402340    SK스퀘어   48450   0.41        67336         45.29       -1274        -7345  ...   -3.64    0.43
            042700  한미반도체   60200  -9.20        58598         12.38         491          112  ...   29.07   10.80

    @multiplesTrailing
        type        : Series
        description : trailing multiples
        example     :
            trailingPE         30.53
            trailingEps     16642.00
            estimatePE         22.00
            estimateEps     22901.00
            priceToBook         1.22
            bookValue      416754.00
            dividendYield        2.1
            dtype: float64

    @ipo
        type        : Union[int, float]
        description : current price (close)

    @currentPrice
        type        : Union[int, float]
        description : current price (close)

    @currentPrice
        type        : Union[int, float]
        description : current price (close)
    """

    def __init__(self, ticker:str):
        self._url_main = f"https://finance.naver.com/item/main.naver?code={ticker}"
        return
    
    @classmethod
    def str2num(cls, src: str) -> Union[int, float]:
        if isinstance(src, float):
            return src
        src = "".join([char for char in src if char.isdigit() or char == "."])
        if not src or src == ".":
            return nan
        if "." in src:
            return float(src)
        return int(src)

    @property
    def currentPrice(self) -> Union[int, float]:
        html = Web.parser(self._url_main)
        curr = [d.text for d in html.find_all("dd") if d.text.startswith("현재가")][0]
        return self.str2num(curr[curr.index("현재가 ") + 4: curr.index(" 전일대비")])

    @property
    def resemblances(self) -> DataFrame:
        data = Web.tables(self._url_main)[4]
        data = data.set_index(keys='종목명').drop(index=['전일대비'])
        data.index.name = None
        for col in data:
            data[col] = data[col].apply(self.str2num)
        data = data.T
        data["종목명"] = [i.replace('*', '')[:-6] for i in data.index]
        data.index = [i[-6:] for i in data.index]
        return data

    @property
    def multiplesTrailing(self) -> Series:
        data = Web.tables(self._url_main)[8]
        per, eps = map(str, data.columns[-1].split('l'))
        estPE, estEps = map(str, data.iloc[0, -1].split('l'))
        pbr, bps = map(str, data.iloc[1, -1].split('l'))
        return Series({
            "trailingPE": self.str2num(per),
            "trailingEps": self.str2num(eps),
            "estimatePE": self.str2num(estPE),
            "estimateEps": self.str2num(estEps),
            "priceToBook": self.str2num(pbr),
            "bookValue": self.str2num(bps),
            "dividendYield": self.str2num(data.iloc[-1, -1])
        })

    @property
    def ipo(self) -> Union[datetime.date, float]:
        data = self.meta.ipo
        if not isna(data) and data:
            return data
        try:
            return datetime.strptime(str(self.str2num(Web.tables(self._url_main)[6].iloc[-1, -1])), "%Y%m%d").date()
        except (AttributeError, KeyError, TypeError, ValueError):
            return nan

    @property
    def underlyingAsset(self) -> str:
        return Web.tables(self._url_main)[6].columns[-1]

    @property
    def nav(self) -> Union[int, float]:
        return self.str2num(Web.tables(self._url_main)[8].columns[-1])


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    naver = naver(
        "005930"
        # "069500"
    )
    print(naver.currentPrice)
    print(naver.resemblances)
    print(naver.multiplesTrailing)
    print(naver.ipo)
