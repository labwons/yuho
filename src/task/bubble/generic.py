try:
    from ...common.path import PATH
    from ...common.calendar import Calendar
except ImportError:
    from dev.common.path import PATH
    from dev.common.calendar import Calendar
from pandas import DataFrame
from typing import Dict
import pandas as pd
import json


class Bubble(DataFrame):
    DUMP = {
        'DATE': f"{Calendar} 기준",
        'META': {            
            'D-1':{
                'label':'1일 수익률',
                'unit':'%'
            },
            'W-1':{
                'label':'1주 수익률', 
                'unit':'%'
            },
            'M-1':{
                'label':'1개월 수익률', 
                'unit':'%'
            },
            'M-3':{
                'label':'3개월 수익률', 
                'unit':'%'
            },
            'M-6':{
                'label':'6개월 수익률', 
                'unit':'%'
            },
            'Y-1':{
                'label':'1년 수익률', 
                'unit':'%'
            },
            'high52PR':{
                'label':'52주 최고가 대비', 
                'unit':'%'
            },
            'low52PR':{
                'label':'52주 최저가 대비', 
                'unit':'%'
            },
            'estimatedPR':{
                'label':'목표가 대비',
                'unit':'%'
            },
            'volume':{
                'label':'거래량',
                'unit':''
            },
            'foreignRate':{
                'label':'외국인 지분율', 
                'unit':'%'
            },
            'beta':{
                'label':'베타', 
                'unit':''
            },
            'floatShares':{
                'label':'유동주식비율', 
                'unit':'%'
            },
            'trailingPS':{
                'label':'PSR', 
                'unit':''
            },
            'trailingPE':{
                'label':'PER',
                'unit':''
            },
            'estimatedPE':{
                'label':'추정PER', 
                'unit':''
            },
            'PBR':{
                'label':'PBR', 
                'unit':''
            },
            'trailingEarningRatio':{
                'label':'영업이익률',
                'unit':'%'
            },
            'fiscalDividends':{
                'label':'배당수익률', 
                'unit':'%'
            },
            'DIV':{
                'label':'예상배당수익률',
                'unit':'%'
            },
            'debtRatio':{
                'label':'부채비율',
                'unit':'%'
            }
        }
    }
    def __init__(self, basis:DataFrame=DataFrame()):
        normalize = lambda x, mn, mx: mn + (x - x.min()) * (mx - mn) / (x.max() - x.min())
        if basis.empty:
            basis = pd.read_json(PATH.SPECS, orient='index')
            basis.index = basis.index.astype(str).str.zfill(6)
        basis = basis.copy()
        basis = basis.sort_values(by='size', ascending=True)
        basis['size'] = round(normalize(basis['size'], 7, 100), 4)
        keys = ['name', 'size', 'meta', 'sectorCode', 'industryCode'] + list(self.DUMP['META'].keys())
        for key in self.DUMP['META'].keys():
            if not key == 'volume':
                basis[key] = round(basis[key], 4 if key == 'beta' else 2)
            self.DUMP['META'][key]['mean'] = mean = basis[key].mean()
            self.DUMP['META'][key]['std'] = std = basis[key].std()
            
        super().__init__(basis[keys])
        category = {'all': "전체"}
        category.update(basis[["sectorCode", "sectorName"]] \
                        .drop_duplicates() \
                        .set_index(keys="sectorCode") \
                        .to_dict()["sectorName"])
        category.update(basis[["industryCode", "industryName"]] \
                        .drop_duplicates() \
                        .set_index(keys="industryCode") \
                        .to_dict()["industryName"])
        self.DUMP["CATEGORY"] = category
        self.DUMP["DATA"] = self.to_dict(orient="index")
        return

    def dump(self):
        string = json.dumps(self.DUMP).replace("NaN", "null")
        if not PATH.BUBBLE.startswith('http'):
            with open(PATH.BUBBLE, 'w') as f:
                f.write(string)
        return string


if __name__ == "__main__":
    from pandas import set_option
    import plotly.graph_objects as go
    set_option('display.expand_frame_repr', False)

    # 'WI100', 'WI110', 'WI200', 'WI210', 'WI220', 'WI230',
    # 'WI240', 'WI250', 'WI260', 'WI300', 'WI310', 'WI320', 'WI330', 'WI340',
    # 'WI400', 'WI410', 'WI500', 'WI510', 'WI520', 'WI600', 'WI610', 'WI620',
    # 'WI630', 'WI640', 'WI700', 'WI800', 'ALL'
    rank = Rank()
    