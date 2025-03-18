from pandas import DataFrame
from typing import Any, Dict, List
from time import time


colors = {
  "G10": "rgb(92,168,155)",
  "G15": "rgb(86, 152, 168)",
  "G20": "rgb(96, 103, 184)",
  "G25": "rgb(195, 102, 56)",
  "G30": "rgb(96, 185, 120)",
  "G35": "rgb(94, 156, 59)",
  "G40": "rgb(142, 182, 77)",
  "G45": "rgb(207, 90, 92)",
  "G50": "rgb(210, 145, 65)",
  "G55": "rgb(86, 80, 199)",
  "G99": "rgb(132, 62, 173)"
}

class MarketBubble(DataFrame):

    _log: List[str] = []
    meta: Dict[str, Dict[str, Any]] = {}
    sector: Dict[str, Dict[str, str]] = {"ALL": {"label": "전체", "color": "royalblue"}}
    def __init__(self, baseline:DataFrame):
        normalize = lambda x, mn, mx: mn + (x - x.min()) * (mx - mn) / (x.max() - x.min())
        stime = time()
        self.log = f'RUN [Build Market Bubble]'
        self.meta = baseline.meta

        super().__init__(baseline)
        self['size'] = round(normalize(self['marketCap'], 7, 100), 4)
        self['meta'] = self['name'] + '(' + self.index + ')<br>' \
                     + '시가총액: ' + self['size'].apply(self._format_cap) + '원<br>' \
                     + '종가: ' + self['close'].apply(lambda x: f"{x:,d}원")
        abnormal = self[
            (self[['D-1', 'W-1', 'M-1', 'M-3', 'M-6', 'Y-1']].sum(axis="columns") == 0) |
            (self['volume'] == 0) |
            (self['name'].isna())
        ]

        for code, name in self[["sectorCode", "sectorName"]].drop_duplicates().dropna().itertuples(index=False):
            self.sector[code] = {'label': name, 'color': colors[code]}

        self.drop(inplace=True, index=abnormal.index)
        self.drop(inplace=True, columns=[
            "close", "marketCap", "amount", "market", "date",
            "industryCode", "industryName", "sectorName", "stockSize",
        ])

        meta = {}
        for col in self.meta:
            if col in self:
                meta[col] = self.meta[col]
                if not self.meta[col]['round'] == -1:
                    meta[col]['mean'] = round(self[col].mean(), 2)
        self.meta = meta

        self._round_up()

        self.log = f'END [Build Market Bubble] {len(self)} Items / Elapsed: {time() - stime:.2f}s'
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

    def _round_up(self):
        for col in self:
            if col in self.meta and (not self.meta[col]['round'] == -1):
                self[col] = round(self[col], self.meta[col]['round'])
            # if col in self.meta:
            #     self[col] = self[col].astype(str).fillna(self.meta[col]['na'])
        return

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
    baseline = MarketBaseline(update=False)
    # print(baseline)
    marketBubble = MarketBubble(baseline)
    print(marketBubble)
    print(marketBubble.meta)
    print(marketBubble.sector)