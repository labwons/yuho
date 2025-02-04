try:
    from ..basis.core import num2cap
    from .color import BLUE2RED, RED2GREEN
except ImportError:
    from dev.task.basis.core import num2cap
    from dev.task.treemap.color import BLUE2RED, RED2GREEN
from pandas import DataFrame, Series


KEYS = {
    'D-1': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-3, -2, -1, 0, 1, 2, 3],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '1일 수익률',
    },
    'W-1': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-6, -4, -2, 0, 2, 4, 6],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '1주 수익률',
    },
    'M-1': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-10, -6.7, -3.3, 0, 3.3, 6.7, 10],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '1개월 수익률',
    },
    'M-3': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-18, -12, -6, 0, 6, 12, 18],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '3개월 수익률',
    },
    'M-6': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-24, -16, -8, 0, 8, 16, 24],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '6개월 수익률',
    },
    'Y-1': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-30, -20, -10, 0, 10, 20, 30],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '1년 수익률',
    },
    'high52PR': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-30, -20, -10, 0, None, None, None],
        'scale': BLUE2RED,
        'scaleNa': 0,
        'label': '52주 최고가 대비',
    },
    'low52PR': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [None, None, None, 0, 10, 20, 30],
        'scale': BLUE2RED,
        'scaleNa': 3,
        'label': '52주 최저가 대비',
    },
    'DIV': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        'scale': RED2GREEN,
        'scaleNa': 0,
        'label': '배당수익률',
    },
    'foreignRate': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [None, None, None, 0, 20, 40, 60],
        'scale': RED2GREEN,
        'scaleNa': 3,
        'label': '외국인 지분율',
    },
    'trailingEarningRatio': {
        'unit': '%',
        'na': '(미제공)',
        'bound': [-15, -10, -5, 0, 5, 10, 15],
        'scale': RED2GREEN,
        'scaleNa': 3,
        'label': '영업이익률',
    },
    'trailingPE': {
        'unit': '',
        'na': '(적자 | 미제공)',
        'bound': None,
        'scale': RED2GREEN[::-1],
        'scaleNa': 6,
        'label': 'PER',
    },
    'trailingPS': {
        'unit': '',
        'na': '(미제공)',
        'bound': None,
        'scale': RED2GREEN[::-1],
        'scaleNa': 6,
        'label': 'PSR',
    },
    'estimatedPE': {
        'unit': '',
        'na': '(적자 | 미제공)',
        'bound': None,
        'scale': RED2GREEN[::-1],
        'scaleNa': 6,
        'label': '추정PER',
    },
    'PBR': {
        'unit': '',
        'na': '(미제공)',
        'bound': None,
        'scale': RED2GREEN[::-1],
        'scaleNa': 6,
        'label': 'PBR',
    }
}


def ceiling(data:DataFrame, name:str, ticker:str='', ceilName:str='') -> dict:
    total = round(data['size'].sum(), 2)
    ticker = ticker if ticker else data.iloc[0]['industryCode']
    ceilName = ceilName if ceilName else data.iloc[0]['sectorName']
    obj = {
        'ticker': ticker,
        'name': name,
        'marketCap': num2cap(total),
        'size': total,
        'volume': data['volume'].sum(),
        'ceiling': ceilName,
        'meta': name + '<br>시가총액: ' + num2cap(total) + '원<br>'
    }
    if name.startswith('TOP'):
        return obj
    for col in KEYS:
        pick = data[~data[col].isna()].copy()
        weight = pick['size'] / pick['size'].sum()
        obj[col] = round((pick[col] * weight).sum(), 2)
    return obj

def grouping(*args) -> DataFrame:
    return DataFrame([ceiling(group, name) for (name, ), group in args]) \
           .set_index(keys='ticker')

def bounds(data:Series) -> list:
    col = str(data.name)
    if col in KEYS and KEYS[col]['bound']:
        return KEYS[col]['bound']

    align = data.dropna().sort_values(ascending=True).dropna()
    if col in [
        'trailingPE',
        'trailingPS',
        'estimatedPE',
        'PBR'
    ]: # 개수 기반
        length = len(data.dropna())
        index = [length * n // 8 for n in range(1, 8)]
        return round(align.iloc[index], 2).tolist()
    elif col in [
        'beta'
    ]: # 최대 값 기반
        return [(data.max() - data.min()) * n / 8 for n in range(1, 8)]
    elif col == 'volume':
        return [
            (data.mean() - data.min()) * (1/4),
            (data.mean() - data.min()) * (2/4),
            (data.mean() - data.min()) * (3/4),
            data.mean(),
            (data.max() - data.mean()) * (1/4),
            (data.max() - data.mean()) * (2/4),
            (data.max() - data.mean()) * (3/4),
        ]
    return []