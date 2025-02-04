from datetime import timedelta
from json import dumps
from numpy import nan
from pandas import DataFrame, Series
from scipy.stats import linregress
from ta.trend import MACD as taMACD
from ta.trend import PSARIndicator
from ta.momentum import RSIIndicator
from ta.momentum import StochasticOscillator as stochOsc
from typing import Any, Dict
import pandas as pd
BASE_PRICE:str = "Typical"
PRINT_MODE:str = "json"


class OHLCT(DataFrame):

    __slot__ = {}

    @classmethod
    def dump(cls, attr:dict) -> str:
        attr_copy = attr.copy()
        for key, val in attr.items():
            if isinstance(val, Series):
                attr_copy[key] = val.tolist()
        return dumps(attr_copy)

    def __init__(self, ohlcv:DataFrame):
        super().__init__(ohlcv)
        self["Date"] = self.index.astype(str)
        self["Typical"] = (ohlcv.High + ohlcv.Low + ohlcv.Close) / 3

        __slot__ = self.__slot__ = {}
        __slot__["trace"] = {
            "ohlc": {
                "x": self["Date"],
                "open": self["Open"],
                "high": self["High"],
                "low": self["Low"],
                "close": self["Close"],
                "increasing": {
                    "line": {
                        "color": 'red'
                    }
                },
                "decreasing": {
                    "line": {
                        "color": 'royalblue'
                    }
                },
                "showlegend": False,
                "hoverinfo": 'x+y',
                "yhoverformat": ",d",
                "type": 'candlestick'
            },
        }
        __slot__["label"] = list(__slot__["trace"].keys())
        __slot__["const"] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__["trace"].items()
        ])
        __slot__['mapvar'] = str(self.__slot__['label']).replace("'", "").replace('"', '')
        return

    @property
    def const(self) -> str:
        return self.__slot__["const"]

    @property
    def label(self) -> list:
        return self.__slot__['label']

    @property
    def trace(self) -> dict:
        return self.__slot__["trace"]

    @property
    def mapvar(self) -> str:
        return self.__slot__['mapvar']

class Volume(OHLCT):

    def __init__(self, ohlcv:DataFrame):
        super().__init__(ohlcv)

        __slot__ = {
            'trace': {
                'volume': {
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": self["Volume"],
                    "marker": {
                        "color": self.apply(lambda r: "red" if r.Close >= r.Open else "royalblue", axis=1).tolist()
                    },
                    "showlegend": False,
                    "yhoverformat": ",d",
                    "hovertemplate": ": %{y}<extra></extra>",
                    "yaxis": "y2",
                    "type": 'bar'
                },
                'vol_1w': {
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": self["Volume"].rolling(window=5).mean(),
                    "mode":"lines",
                    "line": {
                        "color": 'royalblue'
                    },
                    "showlegend": False,
                    "yhoverformat": ".1f",
                    "hovertemplate": ": %{y}<extra></extra>",
                    "yaxis": "y2",
                }
            }
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return


class MovingAverage(OHLCT):

    WINDOWS = [5, 20, 60, 120, 200]

    def __init__(self, ohlcv:DataFrame):
        super().__init__(ohlcv)
        self._construct()

        __slot__ = {
            'trace': {
                col.lower(): {
                    "name": f'{col.replace("MA", "")}일',
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self[col], 1),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": True,
                    "line": {
                        "dash": "dot"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".1f",
                    "hovertemplate": f"{col.replace('MA', '')}일: %{{y}}원<extra></extra>"
                } for col in self if col.startswith('MA')
            }
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        for win in self.WINDOWS:
            self[f'MA{win}'] = self[BASE_PRICE].rolling(win).mean()
        return


class Trend(OHLCT):

    WINDOWS = [5, 2, 1, 0.5, 0.25]
    STDDEVS = {}
    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        self._construct()

        trace = {}
        for col in self:
            if not col.endswith('추세'):
                continue
            dat1 = self[col].dropna()
            dat1.index = dat1.index.astype(str)

            var1 = f'tr_{col.lower().replace("추세", "").replace("전구간", "all")}'
            trace[var1] = {
                "name": col,
                "x": "ohlc.x" if PRINT_MODE.startswith("js") and col.startswith('전구간') else dat1.index.tolist(),
                "y": dat1.astype(int).tolist(),
                "mode": "lines",
                "visible": True if col.startswith("전구간") else 'legendonly',
                "showlegend": True,
                "legendgroup": f"{var1}_t2",
                "line": {
                    "dash": "dash",
                    "color": "black"
                },
                "connectgaps": True,
                "yhoverformat": ",d",
                "hovertemplate": f"{col}: %{{y}}원<extra></extra>"
            }

            var2 = f'trUp_{col.lower().replace("추세", "").replace("전구간", "all")}'
            dat2 = dat1 + 2 * self.STDDEVS[col]
            trace[var2] = {
                "name": col,
                "x": "ohlc.x" if PRINT_MODE.startswith("js") and col.startswith('전구간') else dat2.index.tolist(),
                "y": dat2.astype(int),
                "mode": "lines",
                "visible": True if col.startswith("전구간") else 'legendonly',
                "showlegend": False,
                "legendgroup": f"{var1}_t2",
                "line": {
                    "dash": "dot",
                    "color": "Red"
                },
                "connectgaps": True,
                "yhoverformat": ",d",
                "hovertemplate": f"상단: %{{y}}원<extra></extra>"
            }

            var3 = f'trDn_{col.lower().replace("추세", "").replace("전구간", "all")}'
            dat3 = dat1 - 2 * self.STDDEVS[col]
            trace[var3] = {
                "name": col,
                "x": "ohlc.x" if PRINT_MODE.startswith("js") and col.startswith('전구간') else dat3.index.tolist(),
                "y": dat3.astype(int),
                "mode": "lines",
                "visible": True if col.startswith("전구간") else 'legendonly',
                "showlegend": False,
                "legendgroup": f"{var1}_t2",
                "line": {
                    "dash": "dot",
                    "color": "Red"
                },
                "connectgaps": True,
                "yhoverformat": ",d",
                "hovertemplate": f"하단: %{{y}}원<extra></extra>"
            }
        __slot__ = {
            'trace': trace
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        def _fit(price: Series, _key:str) -> Series:
            data = price.reset_index(level=0)
            data.columns = ['Date', 'data']
            xrange = (data['Date'].diff()).dt.days.fillna(1).astype(int).cumsum()

            r = linregress(x=xrange, y=data[data.columns[-1]])
            fitted = r.slope * xrange + r.intercept
            fitted.name = f'{price.name}Fit'
            self.STDDEVS[_key] = (price.values - fitted).std()
            return pd.concat(objs=[data, fitted], axis=1).set_index(keys='Date')[fitted.name]

        basePrice = self[BASE_PRICE]
        self['전구간추세'] = _fit(basePrice, '전구간추세')
        for yy in self.WINDOWS:
            key = f"{yy}Y추세" if isinstance(yy, int) else f"{int(yy * 12)}M추세"
            date = basePrice.index[-1] - timedelta(int(yy * 365))
            if basePrice.index[0] > date:
                fit = Series(name=key, index=basePrice.index)
            else:
                fit = _fit(basePrice[basePrice.index >= date], key)
            self[key] = fit
        return


class BollingerBand(OHLCT):

    WINDOW:int = 20
    FACTOR:int = 2

    def __init__(self, ohlcv:DataFrame):
        super().__init__(ohlcv)
        self._construct()

        __slot__:Dict[str, Any] = {
            'trace': {
                'bb_middle': {
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["bb_middle"], 1),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": False,
                    "line": {
                        "dash": "dot"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".1f",
                    "hovertemplate": f"{self.WINDOW}일: %{{y}}원<extra></extra>"
                },
                'bb_upperband': {
                    "name": "x2 Band",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["bb_upperband"], 1),
                    "mode": "lines",
                    "line": {
                        "dash": "dash",
                        "color": "maroon"
                    },
                    "showlegend": True,
                    "legendgroup": "x2",
                    "yhoverformat": ".1f",
                    "hovertemplate": "x2 상단: %{y}원<extra></extra>"
                },
                'bb_uppertrend': {
                    "name": "x1 Band",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["bb_uppertrend"], 1),
                    "mode": "lines",
                    "line": {
                        "dash": "dash",
                        "color": "green"
                    },
                    "showlegend": True,
                    "legendgroup": "x1",
                    "yhoverformat": ".1f",
                    "hovertemplate": "x1 상단: %{y}원<extra></extra>"
                }
            }
        }
        __slot__['trace']['bb_lowerband'] = __slot__['trace']['bb_upperband'].copy()
        __slot__['trace']['bb_lowerband'].update({
            "y": round(self["bb_lowerband"], 1),
            "showlegend": False,
            "hovertemplate": "x2 하단: %{y}원<extra></extra>"
        })
        __slot__['trace']['bb_lowertrend'] = __slot__['trace']['bb_uppertrend'].copy()
        __slot__['trace']['bb_lowertrend'].update({
            "y": round(self["bb_lowertrend"], 1),
            "showlegend": False,
            "hovertemplate": "x1 하단: %{y}원<extra></extra>"
        })

        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        basePrice = self[BASE_PRICE]
        self['bb_middle'] = middle = basePrice.rolling(self.WINDOW).mean()
        self['bb_stddev'] = stddev = basePrice.rolling(self.WINDOW).std()
        self['bb_upperband'] = upperband = middle + self.FACTOR * stddev
        self['bb_lowerband'] = lowerband = middle - self.FACTOR * stddev
        self['bb_uppertrend'] = uppertrend = middle + (self.FACTOR / 2) * stddev
        self['bb_lowertrend'] = lowertrend = middle - (self.FACTOR / 2) * stddev
        self['bb_width'] = 100 * (2 * self.FACTOR * stddev) / middle
        self['bb_pctb'] = ((basePrice - lowerband) / (upperband - lowerband)).where(upperband != lowerband, nan)
        self['bb_pctt'] = ((basePrice - lowertrend) / (uppertrend - lowertrend)).where(uppertrend != lowertrend, nan)
        return


class PSAR(OHLCT):

    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        self._construct()

        __slot__ = {
            'trace': {
                f'psar_{col}': {
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self[col], 1),
                    "mode": "markers",
                    "visible": True,
                    "showlegend": False,
                    "marker": {
                        "symbol": "circle",
                        "color": "green",
                        "size": 4
                    },
                    "yhoverformat": ".1f",
                    "hovertemplate": f"SAR: %{{y}}원<extra></extra>"
                } for col in ['up', 'down']
            }
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        fromTa = PSARIndicator(self['High'], self['Low'], self['Close'])
        self['up'] = fromTa.psar_up()
        self['down'] = fromTa.psar_down()
        self['psar'] = self.apply(lambda x: x['up'] if pd.isna(x['down']) else x['down'], axis=1)
        self['pct'] = 100 * (self['Typical'] / self['psar'] - 1)
        return


class MACD(OHLCT):

    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        self._construct()

        __slot__: Dict[str, Any] = {
            'trace': {
                'macd': {
                    "name": "MACD",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["macd"], 2),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": False,
                    "line": {
                        "color": "royalblue"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".2f",
                    "hovertemplate": "MACD: %{y}<extra></extra>",
                    "yaxis": "y3",
                },
                'macd_sig': {
                    "name": "Signal",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["signal"], 2),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": False,
                    "line": {
                        "color": "red"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".2f",
                    "hovertemplate": "Signal: %{y}<extra></extra>",
                    "yaxis": "y3",
                },
                'macd_diff': {
                    "name": "Diff",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["diff"], 2),
                    "type":"bar",
                    "marker":{
                        "color": self["diff"].diff().apply(lambda x: 'red' if x > 0 else 'royalblue').tolist()
                    },
                    "visible": True,
                    "showlegend": False,
                    "yhoverformat": ".2f",
                    "hovertemplate": "Diff: %{y}<extra></extra>",
                    "yaxis": "y3",
                }
            }
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        macd = taMACD(close=self[BASE_PRICE])
        self['macd'] = macd.macd()
        self['signal'] = macd.macd_signal()
        self['diff'] = macd.macd_diff()
        return


class RSI(OHLCT):

    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        self._construct()

        __slot__: Dict[str, Any] = {
            'trace': {
                'rsi': {
                    "name": "RSI",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["RSI"], 2),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": False,
                    "line": {
                        "color": "royalblue"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".2f",
                    "hovertemplate": "RSI: %{y}%<extra></extra>",
                    "yaxis": "y3",
                },
            }
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        rsi = RSIIndicator(self[BASE_PRICE])
        self['RSI'] = rsi.rsi()
        return


class StochasticOscillator(OHLCT):

    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        self._construct()

        __slot__: Dict[str, Any] = {
            'trace': {
                'osc': {
                    "name": "오실레이터",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["oscillator"], 2),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": False,
                    "line": {
                        "color": "royalblue"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".2f",
                    "hovertemplate": ": %{y}%<extra></extra>",
                    "yaxis": "y3",
                },
                'osc_sig': {
                    "name": "오실레이터신호",
                    "x": "ohlc.x" if PRINT_MODE.startswith("js") else self["Date"],
                    "y": round(self["oscillator_signal"], 2),
                    "mode": "lines",
                    "visible": True,
                    "showlegend": False,
                    "line": {
                        "dash": "dash",
                        "color": "red"
                    },
                    "connectgaps": True,
                    "yhoverformat": ".2f",
                    "hovertemplate": ": %{y}%<extra></extra>",
                    "yaxis": "y3",
                },
            }
        }
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _construct(self):
        osc = stochOsc(high=self["High"], low=self["Low"], close=self["Close"])
        self["oscillator"] = osc.stoch()
        self["oscillator_signal"] = osc.stoch_signal()
        return

class Deviation(Trend):

    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        self._re_construct()
        enum = [col for col in self if col.endswith('편차')]
        __slot__: Dict[str, Any] = {
            'trace': {
                f'dv{col.replace("편차", "").replace("전구간", "All")}': {
                    'x':self[col].dropna().index.tolist(),
                    'y':self[col].dropna().tolist(),
                    'type':'bar',
                    'visible': True,
                    'marker': {
                        'color':self[col].dropna().apply(lambda x: "red" if x >= 0 else "royalblue").tolist()
                    },
                    "showlegend": False,
                    "xaxis": f"x{n + 1}",
                    "yaxis": f"y{n + 1}",
                    "yhoverformat": ".2f",
                    "hovertemplate": ": %{y}%<extra></extra>"
                } for n, col in enumerate(enum) if not self[col].empty
            }
        }
        __slot__['trace'].update({
            f'dv{col.replace("편차", "")}': {
                'x': [10],
                'y': [10],
                'mode': 'text',
                'visible': True,
                'text': ['데이터 없음'],
                'textposition': 'top center',
                "xaxis": f"x{n + 1}",
                "yaxis": f"y{n + 1}",
            } for n, col in enumerate(enum) if self[col].empty
        })
        __slot__['label'] = list(__slot__['trace'].keys())
        __slot__['const'] = "\n".join([
            f"const {label} = {self.dump(attr)};" for label, attr in __slot__['trace'].items()
        ])
        if PRINT_MODE.startswith('js'):
            __slot__['mapvar'] = str(__slot__['label']).replace("'", "").replace('"', '')
            self.__slot__ = __slot__
        else:
            self.__slot__['trace'].update(__slot__['trace'])
            self.__slot__['label'] += __slot__['label']
            self.__slot__['const'] += __slot__['const']
        return

    def _re_construct(self):
        cols = [col for col in self if col.endswith('추세')]
        for col in cols:
            name = col.replace("추세", "편차")
            unit = self[[BASE_PRICE, col]].dropna()
            if unit.empty:
                self[name] = Series(name=col, dtype=float)
            else:
                self[name] = round((unit[BASE_PRICE] / unit[col] - 1) / (abs(unit[BASE_PRICE] / unit[col] - 1).sum() / len(unit)), 2)
        self.set_index(keys="Date", inplace=True)
        return


if __name__ == "__main__":
    data = pd.read_csv(
        "https://raw.githubusercontent.com/kairess/stock_crypto_price_prediction/master/dataset/005930.KS_5y.csv") \
        .set_index(keys="Date") \
        .drop(columns=["Adj Close"])
    data.index = pd.to_datetime(data.index)

    # PRINT_MODE = 'python'

    # ohlcv_t = OHLCT(data)
    # # print(ohlcv_t.trace)
    # print(ohlcv_t.label)
    # print(ohlcv_t.const)
    #
    # ma = MovingAverage(data)
    # # print(ma.trace)
    # print(ma.label)
    # print(ma.const)

    tr = Trend(data)
    # print(tr)
    # print(ma.trace)
    # print(tr.label)
    # print(tr.const)

    # dv = Deviation(data)
    # print(dv)
    # print(dv.trace)
    # print(dv.const)
