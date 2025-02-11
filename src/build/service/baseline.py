try:
    from ...fetch.market.state import MarketState
    from ...fetch.market.group import MarketGroup
    from ...fetch.market.spec import MarketSpec
except ImportError:
    from src.fetch.market.state import MarketState
    from src.fetch.market.group import MarketGroup
    from src.fetch.market.spec import MarketSpec
from numpy import nan
from pandas import DataFrame


METADATA = {
    'close': {
        'label': '종가',
        'description': '종가',
        'unit': '원',
		'round': 0,
    },
    'marketCap': {
        'label': '시가총액',
        'description': '시가총액',
        'unit': '억원',
		'round': 0,
    },
    'volume': {
        'label': '거래량',
        'description': '거래량',
        'unit': '',
		'round': 0,
    },
    'dividendYield': {
        'label': '예상 배당수익률',
        'description': '직전 주당 배당금(DPS) / 현재가',
        'unit': '%',
		'round': 2,
    },
    'foreignRate': {
        'label': '외인보유율',
        'description': '외국인 보유 지분율',
        'unit': '%',
		'round': 2,
    },
    'D-1': {
        'label': '1일 수익률',
        'description': '-1D 수익률',
        'unit': '%',
		'round': 2,
    },
    'W-1': {
        'label': '1주 수익률',
        'description': '-1W 수익률',
        'unit': '%',
		'round': 2,
    },
    'M-1': {
        'label': '1개월 수익률',
        'description': '-1M 수익률',
        'unit': '%',
		'round': 2,
    },
    'M-3': {
        'label': '3개월 수익률',
        'description': '-3M 수익률',
        'unit': '%',
		'round': 2,
    },
    'M-6': {
        'label': '6개월 수익률',
        'description': '-6M 수익률',
        'unit': '%',
		'round': 2,
    },
    'Y-1': {
        'label': '1년 수익률',
        'description': '-1Y 수익률',
        'unit': '%',
		'round': 2,
    },
    'beta': {
        'label': '베타',
        'description': '주가 지수 대비 변동성 지표: = 1 (시장과 동일 비율 움직임), < 1 (시장보다 덜 움직임), > 1 (시장보다 큰 폭으로 움직임)',
        'unit': '',
		'round': 4,
    },
    'floatShares': {
        'label': '유동주식비율',
        'description': '전체 발행 주식 대비 시장 유동 주식 비율',
        'unit': '%',
		'round': 2,
    },
    'trailingRevenue': {
        'label': '매출액',
        'description': '연속 4분기에 대한 매출(영업수익) 합산',
        'unit': '억원',
		'round': 2,
    },
    'trailingEps': {
        'label': 'EPS',
        'description': '연속 4분기에 대한 EPS 합산',
        'unit': '원',
		'round': 2,
    },
    'averageRevenueGrowth_A': {
        'label': '연평균 매출성장율',
        'description': '연간 매출(영업수익) 성장율의 평균',
        'unit': '%',
		'round': 2,
    },
    'averageProfitGrowth_A': {
        'label': '연평균 영업이익성장율',
        'description': '연간 영업이익 성장율의 평균',
        'unit': '%',
		'round': 2,
    },
    'averageEpsGrowth_A': {
        'label': '연평균 EPS성장율',
        'description': '연간 EPS 성장율의 평균',
        'unit': '%',
		'round': 2,
    },
    'RevenueGrowth_A': {
        'label': '매출성장율(연간)',
        'description': '연간 매출(영업수익) 성장율',
        'unit': '%',
		'round': 2,
    },
    'RevenueGrowth_Q': {
        'label': '매출성장율(분기)',
        'description': '분기별 매출(영업수익) 성장율',
        'unit': '%',
		'round': 2,
    },
    'ProfitGrowth_A': {
        'label': '영업이익성장율(연간)',
        'description': '연간 영업이익 성장율',
        'unit': '%',
		'round': 2,
    },
    'ProfitGrowth_Q': {
        'label': '영업이익성장율(분기)',
        'description': '분기별 영업이익 성장율',
        'unit': '%',
		'round': 2,
    },
    'EpsGrowth_A': {
        'label': 'EPS성장율(연간)',
        'description': '연간 EPS 성장율',
        'unit': '%',
		'round': 2,
    },
    'EpsGrowth_Q': {
        'label': 'EPS성장율(분기)',
        'description': '분기별 EPS 성장율',
        'unit': '%',
		'round': 2,
    },
    'fiscalDividendYield': {
        'label': '배당수익률',
        'description': '직전 회계연도 기준 배당수익률',
        'unit': '%',
		'round': 2,
    },
    'fiscalDebtRatio': {
        'label': '부채율',
        'description': '직전 회계연도 기준 부채율',
        'unit': '%',
		'round': 2,
    },
    'pct52wHigh': {
        'label': '52주 최고가 대비',
        'description': '52주 최고가 대비 수익률',
        'unit': '%',
		'round': 2,
    },
    'pct52wLow': {
        'label': '52주 최저가 대비',
        'description': '52주 최저가 대비 수익률',
        'unit': '%',
		'round': 2,
    },
    'pctEstimated': {
        'label': '목표가 대비',
        'description': '목표가 대비 수익률(목표가 존재 시)',
        'unit': '%',
		'round': 2,
    },
    'estimatedPE': {
        'label': 'Forward PE',
        'description': '현재가 / 12개월 선행 EPS',
        'unit': '',
		'round': 2,
    },
    'trailingPS': {
        'label': 'PSR',
        'description': '주가 매출 비율(4분기 합산)',
        'unit': '',
		'round': 2,
    },
    'trailingPE': {
        'label': 'PER',
        'description': '주가 수익 비율(4분기 합산)',
        'unit': '',
		'round': 2,
    },
    'name': {
        'label': '종목명',
        'description': '종목명',
        'unit': '',
		'round': -1,
    },
    'industryCode': {
        'label': '산업코드',
        'description': '산업코드',
        'unit': '',
		'round': -1,
    },
    'industryName': {
        'label': '산업명',
        'description': '산업 분류명',
        'unit': '',
		'round': -1,
    },
    'sectorCode': {
        'label': '섹터코드',
        'description': '섹터코드',
        'unit': '',
		'round': -1,
    },
    'sectorName': {
        'label': '섹터명',
        'description': '섹터 분류명',
        'unit': '',
		'round': -1,
    },
    'stockSize': {
        'label': '대형주여부',
        'description': '대형주 여부',
        'unit': '',
		'round': -1,
    },
}


class MarketBaseline(DataFrame):

    def __init__(self, update:bool=True):
        spec = MarketSpec(update=False)
        group = MarketGroup(update=False)
        merge = MarketState(update=update).join(spec).join(group)

        print(merge[spec.columns].count())
        # merge = merge[merge[spec.columns].count().sum() > 0]
        merge['high52'] = merge[['close', 'high52']].max(axis=1)
        merge['low52'] = merge[['close', 'low52']].min(axis=1)
        merge['pct52wHigh'] = 100 * (merge['close'] / merge['high52'] - 1)
        merge['pct52wLow'] = 100 * (merge['close'] / merge['low52'] - 1)
        merge['pctEstimated'] = 100 * (merge['close'] / merge['estPrice'] - 1)
        merge['estimatedPE'] = merge['close'] / merge['estEps']
        merge.drop(columns=["high52", "low52", "estPrice", "estEps"], inplace=True)

        merge['trailingPS'] = (merge['marketCap'] / 1e+8) / merge['trailingRevenue']
        merge['trailingPE'] = merge['close'] / merge['trailingEps']
        merge['trailingPE'] = merge['trailingPE'].apply(lambda val: val if val > 0 else nan)
        merge['turnoverRatio'] = 100 * merge['amount'] / merge['marketCap']

        merge = merge[METADATA.keys()]
        for key, meta in METADATA.items():
            if not meta['round'] == -1:
                merge[key] = round(merge[key], meta['round'])

        super().__init__(merge)
        return


if __name__ == "__main__":
    from pandas import set_option

    set_option('display.expand_frame_repr', False)

    baseline = MarketBaseline(False)
    print(baseline)
    # print(baseline.columns)
    # print(baseline.loc[['005930', '005380']])
