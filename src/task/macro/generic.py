try:
    from ...common.path import PATH
    from ...fetch.ecos.generic import Ecos
    from ...fetch.wise.core import CDSEC
    from ...fetch.wise.generic import Indices
except ImportError:
    from dev.common.path import PATH
    from dev.module.ecos.generic import Ecos
    from dev.module.wise.core import CDSEC
    from dev.module.wise.generic import Indices
import pandas as pd
import json

class Macro:
    objs = {
        "META": {
            "KOSPI": {
                "name": "코스피", 
                "category": "업종지수",
            },
            "KOSDAQ": {
                "name": "코스닥",
                "category": "업종지수"
            }
        },
        "WISE": {},
        "ECOS": {}
    }
    objs["META"].update({
        code: {
            "name": name,
            "category": "업종지수"
        } for code, name in CDSEC.items()
    })
    def __init__(self):
        
        index = Indices(offline=False)
        index.dump()

        index.index.name = "date"
        index.index = pd.to_datetime(index.index).strftime("%Y-%m-%d")
        index.reset_index(level=0, inplace=True)
        for col in index:
            self.objs["WISE"][col] = index[col].tolist()

        Ecos.api = "CEW3KQU603E6GA8VX0O9"
        ecos = Ecos.userDefine.copy()
        self.objs["META"].update(Ecos.META)
        for col in ecos:
            series = ecos[col].dropna()
            self.objs['ECOS'][col] = {
                'date': series.index.strftime("%Y-%m-%d").tolist(),
                'data': series.tolist()
            }
        return

    def dump(self):
        string = json.dumps(self.objs, separators=(",", ":")).replace("NaN", "null")
        if not PATH.MACRO.startswith('http'):
            with open(PATH.MACRO, 'w') as f:
                f.write(string)
        return string
    