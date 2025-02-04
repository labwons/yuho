from pandas import DataFrame
import pandas as pd
import re

CDSEC = {
    'WI100': '에너지', 'WI110': '화학', 'WI200': '비철금속', 'WI210': '철강',
    'WI220': '건설', 'WI230': '기계', 'WI240': '조선', 'WI250': '상사,자본재',
    'WI260': '운송', 'WI300': '자동차', 'WI310': '화장품,의류',
    'WI320': '호텔,레저', 'WI330': '미디어,교육', 'WI340': '소매(유통)',
    'WI400': '필수소비재', 'WI410': '건강관리', 'WI500': '은행',
    'WI510': '증권', 'WI520': '보험', 'WI600': '소프트웨어',
    'WI610': 'IT하드웨어', 'WI620': '반도체', 'WI630': 'IT가전',
    'WI640': '디스플레이', 'WI700': '통신서비스', 'WI800': '유틸리티'
}
CDCOL = {
    'CMP_CD': 'ticker', 'CMP_KOR': 'name',
    'SEC_CD': 'sectorCode', 'SEC_NM_KOR': 'sectorName',
    'IDX_CD': 'industryCode', 'IDX_NM_KOR': 'industryName',
}

def convertNet2Date(timestamp:str):
    timestamp = int(re.search(r'\((\d+)\)', timestamp).group(1))
    return pd.to_datetime(timestamp, unit='ms', utc=True) \
            .tz_convert('Asia/Seoul') \
            .date()

def separateMediaAndEducation(df:DataFrame) -> DataFrame:
    df = df.copy()
    df.loc[df["SEC_NM_KOR"] == "커뮤니케이션서비스", "IDX_NM_KOR"] = "미디어"
    df.loc[df["SEC_NM_KOR"] != "커뮤니케이션서비스", "IDX_NM_KOR"] = "교육"
    df.loc[df["SEC_NM_KOR"] != "커뮤니케이션서비스", "IDX_CD"] = "WI332"
    return df

def separateSwAndITservice(df:DataFrame) -> DataFrame:
    df = df.copy()
    df.loc[df["SEC_NM_KOR"] == 'IT', 'IDX_NM_KOR'] = 'IT서비스'
    df.loc[df["SEC_NM_KOR"] == 'IT', 'IDX_CD'] = 'WI602'
    return df