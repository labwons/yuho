"""
TITLE   : BUILD MARKET BASELINE
AUTHOR  : SNOB
CONTACT : snob.labwons@gmail.com
ROUTINE : 15:40+09:00UTC on weekday
"""
if __name__ == "__main__":
    try:
        from ..common.path import PATH
        from ..common.report import eMail
        from .service.baseline import MarketBaseline
        from .service.marketmap import MarketMap
    except ImportError:
        from src.common.path import PATH
        from src.common.report import eMail
        from src.build.service.baseline import MarketBaseline
        from src.build.service.marketmap import MarketMap
    from datetime import datetime
    from json import dumps

    TODAY = datetime.today().strftime("%Y-%m-%d")[2:]

    mail = eMail()

    try:
        baseline = MarketBaseline(update=False)
        if not PATH.BASE.startswith('http'):
            with open(PATH.BASE, 'w') as f:
                f.write(baseline.to_json(orient='index').replace("nan", ""))
        context = f'[{"Fail" if baseline.log.count("Fail") else "Success"}] BUILD Baseline\n{baseline.log}\n\n'

        marketmap = MarketMap(baseline)
        if not PATH.MAP.startswith('http'):
            service = {
                'meta': marketmap.meta,
                'base': marketmap.to_dict(orient='index'),
                'colors': marketmap.colors.to_dict(orient='index'),
                'all': marketmap[marketmap.index.str.isdigit() | marketmap.index.str.startswith('W')].index.tolist(),
                'woS': marketmap[marketmap.index.str.isdigit() | marketmap.index.str.startswith('N')].index.tolist()
            }
            with open(PATH.MAP, 'w') as f:
                f.write(dumps(service))
        context += f'[Success] Build Market-Map\n{marketmap.log}\n\n'

        prefix = "SUCCESS" if not baseline.log.count("Fail") + marketmap.log.count("Fail") else "WARNING"
        mail.subject = f'[{prefix}]BUILD BASELINE on {TODAY}'
        mail.context = context
    except Exception as report:
        mail.context = f"{report}"
    finally:
        mail.send()


