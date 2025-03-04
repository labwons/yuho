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
        from ..render.config import minify
        from ..render import (
            bubble,
            macro,
            marketmap
        )
        from .service.baseline import MarketBaseline
        from .service.marketmap import MarketMap
    except ImportError:
        from src.common.path import PATH
        from src.common.report import eMail
        from src.render.config import minify
        from src.render import (
            bubble,
            macro,
            marketmap
        )
        from src.build.service.baseline import MarketBaseline
        from src.build.service.marketmap import MarketMap
    from datetime import datetime
    from jinja2 import Environment, FileSystemLoader
    from json import dumps
    from pykrx.stock import get_nearest_business_day_in_a_week


    TESTMODE = True
    TODAY = datetime.today().strftime("%Y/%m/%d")
    try:
        TRADING_DATE = datetime.strptime(get_nearest_business_day_in_a_week(), "%Y%m%d") \
                  .strftime("%Y/%m/%d") + ' 종가 기준'
    except IndexError:
        TRADING_DATE = TODAY + ' 종가 기준'

    mail = eMail()
    try:
        baseline = MarketBaseline(update=True)
        if not PATH.BASE.startswith('http'):
            with open(PATH.BASE, 'w') as f:
                f.write(baseline.to_json(orient='index').replace("nan", "null"))
        context = f'[{"Warning" if baseline.log.count("Fail") else "Success"}] BUILD Baseline\n{baseline.log}\n\n'
    except Exception as error:
        baseline = MarketBaseline(update=False)
        context = f'[Fail] BUILD Baseline: Fail-Safe to use previous data\n\tERROR: {error}\n\n'


    marketMap = MarketMap(baseline)
    # TODO
    # metadata clear (불필요 key 값 삭제하기)
    try:
        if not PATH.MAP.startswith('http'):
            mapT = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                   .get_template('marketmap.js')
            mapJs = mapT.render(
                tradingDate=TRADING_DATE,
                srcIndicatorOpt=dumps(marketMap.meta),
                srcTicker=marketMap.to_json(orient='index'),
                srcColors=marketMap.colors.to_json(orient='index')
            ).replace("nan", "null").replace("NaN", "null")
            with open(PATH.JS.MAP, 'w', encoding='utf-8') as file:
                file.write(mapJs)
        context += f'[Success] BUILD Market-Map\n{marketMap.log}\n\n'
    except Exception as error:
        context += f'[Fail] BUILD Market-Map\n\tERROR: {error}\n\n'


    minify.css()
    minify.js()

    service = marketmap.render(
        localhost=TESTMODE,
        title="시장지도 MARKET MAP",
        trading_date=TRADING_DATE
    )
    with open(PATH.HTML.MAP, 'w', encoding='utf-8') as file:
        file.write(service)

    mail.context = context
    mail.subject = f'[{"SUCCESS" if not context.count("Fail") else "WARNING"}]BUILD BASELINE on {TODAY}'
    print(mail.subject)
    print(mail.context)
    # mail.send()
