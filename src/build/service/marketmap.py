from datetime import datetime
from pandas import (
    concat,
    DataFrame,
    Series
)
from scipy.stats import norm
from time import time
from typing import Any, Dict, List, Union


HEX2RGB = lambda x: (int(x[1:3], 16), int(x[3:5], 16), int(x[5:], 16))
CONNECT = lambda x, x1, y1, x2, y2: ( (y2 - y1) / (x2 - x1) ) * (x - x1) + y1

BLUE2RED = [
    '#1861A8', # R24 G97 B168
    '#228BE6', # R34 G139 B230
    '#74C0FC', # R116 G192 B252
    '#A6A6A6', # R168 G168 B168
    '#FF8787', # R255 G135 B135
    '#F03E3E', # R240 G62 B62
    '#C92A2A'  # R201 G42 B42
]
RED2GREEN = [
    '#F63538', # R246 G53 B56
    '#BF4045', # R191 G64 B69
    '#8B444E', # R139 G68 B78
    '#414554', # R65 G69 B84
    '#35764E', # R53 G118 B78
    '#2F9E4F', # R47 G158 B79
    '#30CC5A'  # R48 G204 B90
]
_KEYS = {
    'D-1': {
        'na': '(미제공)',
        'valueScale': [-3, -2, -1, 0, 1, 2, 3],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'W-1': {
        'na': '(미제공)',
        'valueScale': [-6, -4, -2, 0, 2, 4, 6],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'M-1': {
        'na': '(미제공)',
        'valueScale': [-10, -6.7, -3.3, 0, 3.3, 6.7, 10],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'M-3': {
        'na': '(미제공)',
        'valueScale': [-18, -12, -6, 0, 6, 12, 18],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'M-6': {
        'na': '(미제공)',
        'valueScale': [-24, -16, -8, 0, 8, 16, 24],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'Y-1': {
        'na': '(미제공)',
        'valueScale': [-30, -20, -10, 0, 10, 20, 30],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'pct52wHigh': {
        'na': '(미제공)',
        'valueScale': [-30, -20, -10, 0, None, None, None],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 0,
    },
    'pct52wLow': {
        'na': '(미제공)',
        'valueScale': [None, None, None, 0, 10, 20, 30],
        'colorScale': BLUE2RED,
        'defaultColorIndex': 3,
    },
    'dividendYield': {
        'na': '(미제공)',
        'valueScale': [0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        'colorScale': RED2GREEN,
        'defaultColorIndex': 0,
    },
    'fiscalDividendYield': {
        'na': '(미제공)',
        'valueScale': [0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        'colorScale': RED2GREEN,
        'defaultColorIndex': 0,
    },
    'foreignRate': {
        'na': '(미제공)',
        'valueScale': [None, None, None, 0, 20, 40, 60],
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'trailingProfitRate': {
        'na': '(미제공)',
        'valueScale': [-15, -10, -5, 0, 5, 10, 15],
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'trailingPE': {
        'na': '(적자 | 미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN[::-1],
        'defaultColorIndex': 6,
    },
    'trailingPS': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN[::-1],
        'defaultColorIndex': 6,
    },
    'estimatedPE': {
        'na': '(적자 | 미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN[::-1],
        'defaultColorIndex': 6,
    },
    'PBR': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN[::-1],
        'defaultColorIndex': 6,
    },
    'fiscalDebtRatio' : {
        'na': '(미제공)',
        'valueScale':  [30, 60, 90, 120, 150, 180, 210],
        'colorScale': RED2GREEN[::-1],
        'defaultColorIndex': 6,
    },
    'volume': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'beta': {
        'na': '(미제공)',
        'valueScale': [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'turnoverRatio': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'averageRevenueGrowth_A': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'averageProfitGrowth_A': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'averageEpsGrowth_A': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'RevenueGrowth_A': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'ProfitGrowth_A': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    },
    'EpsGrowth_A': {
        'na': '(미제공)',
        'valueScale': None,
        'colorScale': RED2GREEN,
        'defaultColorIndex': 3,
    }
}


class MarketMap(DataFrame):

    _log: List[str] = []
    meta: Dict[str, Dict[str, Any]] = _KEYS.copy()
    def __init__(self, baseline:DataFrame):
        stime = time()
        self.log = f'Begin [Build Market Map] @{datetime.today().strftime("%Y-%m-%d")[2:]}'

        super().__init__(baseline[baseline["stockSize"] == "large"])

        self['size'] = (self['marketCap'] / 1e+8).astype(int)
        self['ceiling'] = self['industryName']
        self['meta'] = self['name'] + '(' + self.index + ')<br>' \
                     + '시가총액: ' + self['size'].apply(self._format_cap) + '원<br>' \
                     + '종가: ' + self['close'].apply(lambda x: f"{x:,d}원")

        ws_industry = self._grouping("industryName")
        ws_industry.index = ws_industry.index.str.pad(width=6, side="left", fillchar='W')
        ws_sector = self._grouping("sectorName")
        ws_sector["ceiling"] = "대형주"
        ws_sector.index = ws_sector.index.str.pad(width=6, side="left", fillchar='W')
        ws_top = DataFrame(self.select_dtypes(include=['int']).sum()).T
        ws_top[['name', 'meta']] = ['대형주', self._format_cap(ws_top.iloc[0]['size'])]
        ws_top.index = ['WS0000']

        ns_industry = self._grouping("industryName", "005930")
        ns_industry.index = ns_industry.index.str.pad(width=6, side="left", fillchar='N')
        ns_sector = self._grouping("sectorName", "005930")
        ns_sector["ceiling"] = "대형주(삼성전자 제외)"
        ns_sector.index = ns_sector.index.str.pad(width=6, side="left", fillchar='N')
        ns_top = DataFrame(self[~self.index.isin(['005930'])].select_dtypes(include=['int']).sum()).T
        ns_top[['name', 'meta']] = ["대형주(삼성전자 제외)", self._format_cap(ns_top.iloc[0]['size'])]
        ns_top.index = ['NS0000']

        super().__init__(concat([self, ws_industry, ns_industry, ws_sector, ns_sector, ws_top, ns_top]))
        self.drop(inplace=True, columns=[
            "close", 'floatShares',
            'trailingRevenue', 'trailingEps', 'pctEstimated',
            'RevenueGrowth_Q', 'ProfitGrowth_Q', 'EpsGrowth_Q',
            "industryCode", "industryName", "sectorCode", "sectorName", "stockSize"
        ])

        self._check_metadata(baseline.meta)
        self._chunk()
        self._round_up()

        self.log = f'End [Build Market Map] {len(self)} Items / Elapsed: {time() - stime:.2f}s'
        return

    def _check_metadata(self, baseline_meta:Dict[str, Dict[str, Any]]):
        for key in self.meta:
            if not key in self:
                raise KeyError(f'MAP metadata: {key} is not in MAP data')
        for col in self.select_dtypes(include=['number']).columns:
            if col in ['size', 'amount', 'marketCap']: continue
            if not col in baseline_meta:
                raise ValueError(f'MAP data key : "{col}" is not found in Baseline metadata')
            if not col in self.meta:
                raise KeyError(f'column: {col} is not predefined in MAP metadata')
            self.meta[col].update(baseline_meta[col])
        return

    def _chunk(self):
        for key, meta in self.meta.items():
            if meta['valueScale']:
                continue

            mean, std, mn, mx = self[key].mean(), self[key].std(), self[key].min(), self[key].max()
            if key in ['volume', 'PBR']:
                self.meta[key]['valueScale'] = [None, None, None, 0, mean / 2, mean, mean + std]
            elif key in ['estimatedPE', 'trailingPE', 'trailingPS']:
                dv = (min(mx, mean + 2 * std) - mean) / 4
                self.meta[key]['valueScale'] = [0.25 * mean, 0.5 * mean, 0.75 * mean, mean, dv, 2 * dv, 3 * dv]
            elif key == 'turnoverRatio':
                ks, kq = self[self['market'] == 'kospi'], self[self['market'] == 'kosdaq']
                ks = 100 * ks['amount'].sum() / ks['marketCap'].sum()
                kq = 100 * kq['amount'].sum() / kq['marketCap'].sum()
                dvn = mean - ks
                dvp = kq - mean
                self.meta[key]['valueScale'] = [ks, ks + 0.33 * dvn, ks + 0.66 * dvn, mean, mean + 0.33 * dvp, mean + 0.66 * dvp, kq]
                self.drop(inplace=True, columns=['amount', 'market', 'marketCap'])
            else:
                en, ep = max(mn, mean - 2 * std), min(mx, mean + 2 * std)
                dvn, dvp = mean - en, ep - mean
                self.meta[key]['valueScale'] = [
                    en + 0.25*dvn, en + 0.5*dvn, en + 0.75*dvn, mean,
                    mean + 0.25*dvp, mean + 0.5*dvp, mean + 0.75*dvp
                ]
            self.meta[key]['valueScale'] = [round(v, 2) for v in self.meta[key]['valueScale'] if v]
        return

    def _grouping(self, key:str, *exclude:str) -> DataFrame:
        objs = []
        for value, group in self.groupby(by=key):
            if exclude:
                group = group[~group.index.isin(exclude)]
            '''
            Default Grouping Factors: 
            Weighted Mean
            '''
            size = group['size'].sum()
            w = group['size'] / size
            obj = {col: (w * group[col]).sum() for col in group if group[col].dtype == float}
            obj.update({
                "ticker": group.iloc[0][key.replace("Name", "Code")],
                "name": value,
                "size": size,
                "volume": group['volume'].sum(),
                "amount": group['amount'].sum(),
                "ceiling": 'TBD' if key.startswith('sector') else group.iloc[0]['sectorName'],
                'meta': f'{value}<br>시가총액: ' + self._format_cap(size) + '원<br>'
            })
            '''
            Exception Grouping Factors:
            Arithmetic Mean
            '''
            # Not Defined Yet

            '''
            Exception Grouping Factors:
            Customize
            '''
            obj['turnoverRatio'] = 100 * obj['amount'] / (obj['size'] * 1e+8)
            objs.append(obj)
        return DataFrame(data=objs).set_index(keys='ticker')

    def _round_up(self):
        for col in self:
            if col in self.meta and (not self.meta[col]['round'] == -1):
                self[col] = round(self[col], self.meta[col]['round'])
        return

    def show_gaussian(self):
        # INTERNAL
        import plotly.graph_objs as go

        gaussian = self.gaussian
        visibility = []
        fig = go.Figure()
        for n, col in enumerate(self.desc):
            subset = gaussian[col].sort_values(by='x')

            fig.add_trace(go.Scatter(
                x=subset.x,
                y=subset.y,
                mode='lines+markers',
                showlegend=False,
                visible=(n == 0),
                meta=subset.meta,
                hovertemplate="%{meta}: %{x}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=[subset.x.mean() - 2 * subset.x.std()] * len(subset),
                y=subset.y,
                mode='lines',
                showlegend=False,
                line={
                    'color':'black',
                    'dash':'dot'
                },
                visible=(n == 0),
                hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=[subset.x.mean() + 2 * subset.x.std()] * len(subset),
                y=subset.y,
                mode='lines',
                showlegend=False,
                line={
                    'color': 'black',
                    'dash': 'dot'
                },
                visible=(n == 0),
                hoverinfo='skip'
            ))

            visibility.append({
                "label": col,
                "method": "update",
                "args": [{"visible": [(j // 3) == n for j in range(3 * len(self.desc.columns))]}]
            })

        fig.update_layout(
            xaxis_title="Value",
            yaxis_title="Density",
            updatemenus=[{
                "buttons": visibility,
                "direction": "down",
                "showactive": True,
                "x": 0.0,
                "xanchor": "left",
                "y": 1.05,
                "yanchor": "top"
            }]
        )
        fig.show()
        return

    @property
    def colors(self) -> DataFrame:
        objs = {}
        for key, meta in self.meta.items():
            scale = [v if v else 0 for v in meta['valueScale']]
            rgb = [HEX2RGB(s) for s in meta['colorScale']]
            default = meta['colorScale'][meta['defaultColorIndex']]
            def _paint(value) -> str:
                if value == '':
                    return default
                value = float(value)
                if value <= scale[0]:
                    return meta['colorScale'][0]
                if value > scale[-1]:
                    return meta['colorScale'][-1]
                n = 0
                while n < len(meta['colorScale']) - 1:
                    if scale[n] < value <= scale[n + 1]:
                        break
                    n += 1
                r1, g1, b1 = rgb[n]
                r2, g2, b2 = rgb[n + 1]
                r = CONNECT(value, scale[n], r1, scale[n + 1], r2)
                g = CONNECT(value, scale[n], g1, scale[n + 1], g2)
                b = CONNECT(value, scale[n], b1, scale[n + 1], b2)
                return f'#{hex(int(r))[2:]}{hex(int(g))[2:]}{hex(int(b))[2:]}'.upper()
            objs[key] = self[key].fillna('').apply(_paint)
        colors = concat(objs, axis=1)
        colors.iloc[-2:] = "#C8C8C8"
        return colors

    @property
    def desc(self) -> DataFrame:
        # INTERNAL
        tg = self[self.index.str.isdigit()]
        desc = tg.describe()
        mn = {col: ",".join(tg[tg[col] == tg[col].min()].index) for col in desc}
        mx = {col: ",".join(tg[tg[col] == tg[col].max()].index) for col in desc}
        desc = concat([desc, DataFrame([mn, mx], index=["minT", "maxT"])])
        return desc

    @property
    def gaussian(self) -> DataFrame:
        # INTERNAL
        stocks = self[self.index.str.isdigit()]
        objs = {}
        for col in self.desc:
            x = stocks.sort_values(by=col, ascending=True)
            obj = DataFrame({
                'x': x[col].values,
                'y':norm.pdf(x[col], x[col].mean(), x[col].std()),
                'meta': x['name'] + '(' + x.index + ')',
            })
            objs[col] = obj
        return concat(objs=objs, axis=1)

    @property
    def log(self) -> str:
        return "\n".join(self._log)

    @log.setter
    def log(self, log: str):
        self._log.append(log)


    @classmethod
    def _format_cap(cls, market_cap:int) -> str:
        zo, euk = int(market_cap // 10000), int(market_cap % 10000)
        return f'{zo}조 {euk}억' if zo else f'{euk}억'



if __name__ == "__main__":
    from src.build.service.baseline import MarketBaseline
    from pandas import set_option

    set_option('display.expand_frame_repr', False)

    marketMap = MarketMap(MarketBaseline(update=False))
    print(marketMap)
    print(marketMap.log)
    # print(marketMap.meta)
    # print(marketMap.gaussian)
    # marketMap.show_gaussian()
    # print(marketMap.colors)
    print(marketMap.to_dict(orient='index'))