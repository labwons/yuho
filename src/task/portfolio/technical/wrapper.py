try:
    from . import core
except ImportError:
    from dev.portfolio.technical import core
from jsmin import jsmin
from json import dumps
from pandas import DataFrame


class TechnicalReporter:

    def __init__(self, ohlcv:DataFrame, to:str='js'):
        core.PRINT_MODE = to
        self.meta = {
            'ohlct': {
                'html': {
                    'tag':False,
                    'label':'',
                    'pos':'top'
                },
                'core': core.OHLCT(ohlcv)
            },
            'sma': {
                'html': {
                    'tag': True,
                    'label': '이동평균선',
                    'pos': 'top'
                },
                'core': core.MovingAverage(ohlcv)
            },
            'bb': {
                'html': {
                    'tag': True,
                    'label': '볼린저밴드',
                    'pos': 'top'
                },
                'core': core.BollingerBand(ohlcv)
            },
            'trend': {
                'html': {
                    'tag': True,
                    'label': '통계적추세',
                    'pos': 'top'
                },
                'core': core.Trend(ohlcv)
            },
            'psar': {
                'html': {
                    'tag': True,
                    'label': 'PSAR',
                    'pos': 'top'
                },
                'core': core.PSAR(ohlcv)
            },
            'volume': {
                'html': {
                    'tag': True,
                    'label': '거래량',
                    'pos': 'bottom'
                },
                'core': core.Volume(ohlcv)
            },
            'macd': {
                'html': {
                    'tag': True,
                    'label': 'MACD',
                    'pos': 'bottom'
                },
                'core': core.MACD(ohlcv)
            },
            'rsi': {
                'html': {
                    'tag': True,
                    'label': 'RSI',
                    'pos': 'bottom'
                },
                'core': core.RSI(ohlcv)
            },
            'osc': {
                'html': {
                    'tag': True,
                    'label': '오실레이터',
                    'pos': 'bottom'
                },
                'core': core.StochasticOscillator(ohlcv)
            },
            'dv': {
                'html': {
                    'tag': True,
                    'label': '통계적추세 편차',
                    'pos': 'etc'
                },
                'core': core.Deviation(ohlcv)
            }
        }
        return

    def __iter__(self):
        for item in self.meta.values():
            yield item

    def __getitem__(self, item):
        return self.meta[item]

    @property
    def const(self) -> str:
        return f"""
            const X_RANGE = ['{self['ohlct']['core']['Date'].iloc[0]}', '{self['ohlct']['core']['Date'].iloc[-1]}'];
            const BELOW_INDICATORS = {str([key for key, val in self.meta.items() if val['html']['pos'] == 'bottom'])};
            const VARIABLE_MAP = {dumps({key: val['core'].mapvar for key, val in self.meta.items()}).replace('"', '').replace("'", "")};
            const GRID_RATIO = {{1:[0, 1.0], 2:[0.8, 0.2], 3:[0.6, 0.2, 0.2], 4:[0.55, 0.15, 0.15, 0.15]}};
        """[1:]

    @property
    def declaration(self) -> str:
        return jsmin(self.trace + self.const)

    @property
    def select(self) -> str:
        index = {'top': 1, 'bottom': 3, 'etc': 5}
        lines = [
            '<label><strong>상단 지표</strong></label>', '',
            '<label><strong>하단 지표</strong></label>', '',
            '<label><strong>기타 지표</strong></label>', '',
        ]
        for key, val in self.meta.items():
            if key == 'ohlct': continue
            html = val['html']
            checked = "checked" if key == 'volume' else ''
            lines[index[html['pos']]] += (f'<label class="dropdown-option">'
                                          f'<input type="checkbox" name="dropdown-group" value="{key}" {checked}/>'
                                          f'{html["label"]}'
                                          f'</label>')
        return f"""
            <div class="dropdown" data-control="checkbox-dropdown">
                <label class="dropdown-label">지표 선택</label>
                <div class="dropdown-list">{str().join(lines)}</div>
            </div>
        """.replace("\n", "").replace("\t", "")

    @property
    def trace(self) -> str:
        return "\n".join([item['core'].const for item in self]) \
                .replace('"ohlc.x"', 'ohlc.x') \
                .replace("NaN", "null")

    @classmethod
    def xaxis(cls, **kwargs):
        attr = {
            "autorange": True,  # [str | bool] one of ( True | False | "reversed" | "min reversed" |
            #                       "max reversed" | "min" | "max" )
            "color": "#444",  # [str]
            "showgrid": True,  # [bool]
            "gridcolor": "lightgrey",  # [str]
            "griddash": "solid",  # [str] one of ( "solid" | "dot" | "dash" | "longdash" | "dashdot" )
            "gridwidth": 0.5,  # [float]
            "showline": True,  # [bool]
            "linecolor": "black",  # [str]
            "linewidth": 2,  # [float]
            "mirror": False,  # [str | bool] one of ( True | "ticks" | False | "all" | "allticks" )
            "rangeslider": {
                "visible": False  # [bool]
            },
            "rangeselector": {
                "visible": True,  # [bool]
                "bgcolor": "#eee",  # [str]
                "bordercolor": "#444",  # [str]
                "borderwidth": 0,  # [float]
                "buttons": [
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all")
                ],
                "xanchor": "left",  # [str] one of ( "auto" | "left" | "center" | "right" )
                "x": 0.005,  # [float]
                "yanchor": "bottom",  # [str] one of ( "auto" | "top" | "middle" | "bottom" )
                "y": 1.0  # [float]
            },
            "showticklabels": True,  # [bool]
            "tickformat": "%Y/%m/%d",  # [str]
            "zeroline": True,  # [bool]
            "zerolinecolor": "lightgrey",  # [str]
            "zerolinewidth": 1  # [float]
        }
        attr.update(kwargs)
        return dumps(attr)

    @classmethod
    def yaxis(cls, **kwargs):
        attr = {
            "domain":[0, 1],
            "side":"right",
            "showticklabels": True,  # [bool]
            "tickformat": ',d',
            "autorange": True,  # [str | bool] one of ( True | False | "reversed" | "min reversed" |
                                #  "max reversed" | "min" | "max" )
            "color": "#444",  # [str]
            "showgrid": True,  # [bool]
            "gridcolor": "lightgrey",  # [str]
            "griddash": "solid",  # [str] one of ( "solid" | "dot" | "dash" | "longdash" | "dashdot" )
            "gridwidth": 0.5,  # [float]
            "showline": True,  # [bool]
            "linecolor": "grey",  # [str]
            "linewidth": 1,  # [float]
            "mirror": False,  # [str | bool] one of ( True | "ticks" | False | "all" | "allticks" )
            "zeroline": True,  # [bool]
            "zerolinecolor": "lightgrey",  # [str]
            "zerolinewidth": 1  # [float]
        }
        attr.update(kwargs)
        return dumps(attr)
