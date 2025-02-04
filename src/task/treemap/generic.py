try:
    from ...common.calendar import Calendar
    from ...common.path import PATH
    from .color import paint
    from .core import KEYS, ceiling, bounds, grouping
except ImportError:
    from dev.task.treemap.color import paint
    from dev.task.treemap.core import KEYS, ceiling, bounds, grouping
    from dev.common.calendar import Calendar
    from dev.common.path import PATH
from pandas import DataFrame, Series
import pandas as pd
import json


class MarketMap(DataFrame):

    src = ''
    def __init__(self, basis:DataFrame=DataFrame()):
        if basis.empty:
            basis = pd.read_json(PATH.SPECS, orient='index')
            basis.index = basis.index.astype(str).str.zfill(6)
        basis.loc[basis['size'] > 10000, 'stockSize'] = 'large'
        basis = basis[basis['volume'] > 0]
        basis = pd.concat([df for _, df in basis.groupby(by='industryCode')])

        large_ws = basis[basis['stockSize'] == 'large']
        large_ws['ceiling'] = large_ws['industryName']

        section = '대형주'
        ii, si = large_ws.groupby(by=['industryName']), large_ws.groupby(by=['sectorName'])
        ind_ws, sec_ws = grouping(*ii), grouping(*si)
        ind_ws = ind_ws[ind_ws['name'] != ind_ws['ceiling']]
        sec_ws['ceiling'] = section
        ind_i_ws = [f'{i}WS' for i in ind_ws.index]
        sec_i_ws = [f'{sec.iloc[0]["sectorCode"]}WS' for (_, ), sec in si]
        ind_ws.index, sec_ws.index = ind_i_ws, sec_i_ws
        top_ws = ceiling(large_ws, section, 'TOPWS', '')
        top_ws['ceiling'] = ''
        top_ws = DataFrame(index=['TOPWS'], data=top_ws)

        section = '대형주(삼성전자 제외)'
        large_ns = large_ws[large_ws.index != '005930']
        ii, si = large_ns.groupby(by=['industryName']), large_ns.groupby(by=['sectorName'])
        ind_ns, sec_ns = grouping(*ii), grouping(*si)
        ind_ns = ind_ns[ind_ns['name'] != ind_ns['ceiling']]
        sec_ns['ceiling'] = section
        ind_i_ns = [f'{i}NS' for i in ind_ns.index]
        sec_i_ns = [f'{sec.iloc[0]["sectorCode"]}NS' for (_, ), sec in si]
        ind_ns.index, sec_ns.index = ind_i_ns, sec_i_ns
        top_ns = ceiling(large_ns, section, 'TOPNS', '')
        top_ns['ceiling'] = ''
        top_ns = DataFrame(index=['TOPNS'], data=top_ns)

        super().__init__(
            pd.concat(
                [large_ws, ind_ws, sec_ws, top_ws, ind_ns, sec_ns, top_ns]
            )[['name', 'size', 'ceiling', 'meta'] + list(KEYS.keys())]
        )

        META = KEYS.copy()
        for key, val in META.items():
            if not val['bound']:
                META[key]['bound'] = bounds(self[key])
            v = self[key].fillna(val['na'])
            c = paint(v, val)
            v = v.apply(lambda x: x if x == val['na'] else f"{x:.2f}{val['unit']}")
            self[key] = Series(list(zip(v, c)), index=v.index)
        META['DATE'] = str(Calendar)
        META['DUPLICATEDGROUP'] = (large_ws[
            large_ws['industryName'] == large_ws['sectorName']
        ]['sectorCode'].drop_duplicates() + 'WS').to_list()

        self.src = {
            'TICKERS': self[self.index.isin(large_ws.index)] \
                       .sort_values(by='size', ascending=False) \
                       .to_dict(orient='index'),
            'WS': {
                'industry': self[self.index.isin(ind_ws.index)].to_dict(orient='index'),
                'sector': self[self.index.isin(sec_ws.index)].to_dict(orient='index'),
                'top': self[self.index.isin(top_ws.index)].to_dict(orient='index')
            },
            'NS': {
                'industry': self[self.index.isin(ind_ns.index)].to_dict(orient='index'),
                'sector': self[self.index.isin(sec_ns.index)].to_dict(orient='index'),
                'top': self[self.index.isin(top_ns.index)].to_dict(orient='index')
            },
            'METADATA': META
        }
        return

    def dump(self) -> str:
        string = json.dumps(self.src)
        if not PATH.TRMAP.startswith('http'):
            with open(PATH.TRMAP, 'w') as f:
                f.write(string)
        return string


if __name__ == "__main__":


    marketMap = MarketMap(specs)
    marketMap.dump()

    # marketMap.to_excel('datasample.xlsx', index=True)
    # files.download('datasample.xlsx')