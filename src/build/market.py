"""
TITLE   : BUILD MARKET BASELINE
AUTHOR  : SNOB
CONTACT : snob.labwons@gmail.com
ROUTINE : 15:40+09:00UTC on weekday
"""
if __name__ == "__main__":
    from pandas import set_option as PRINT_DATA
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
    from datetime import datetime, timezone, timedelta
    from jinja2 import Environment, FileSystemLoader
    from json import dumps
    from numpy import datetime_as_string
    from time import sleep
    import os


    PRINT_DATA('display.expand_frame_repr', False)
    LOCAL_HOST = True if not os.getenv('LOCAL_HOST') else False
    # -------------------------------------------------------------------------------
    # INCASE YOU WANT TO BUILD, DEPLOY AND COMMIT ON LOCAL,
    # SWITCH {LOCAL_HOST} TO False, AS BELOW
    # -------------------------------------------------------------------------------
    # LOCAL_HOST = False

    if not LOCAL_HOST:
        from pykrx.stock import get_nearest_business_day_in_a_week
        if get_nearest_business_day_in_a_week() != datetime.today().strftime("%Y%m%d"):
            raise SystemExit

    KST = timezone(timedelta(hours=9))
    clk = datetime.now(KST)
    while clk.minute < 31:
        sleep(30)
        clk = datetime.now(KST)


    mail = eMail()
    context = ["DETAILS"]

    try:
        baseline = MarketBaseline(update=True)
        if not PATH.BASE.startswith('http'):
            with open(PATH.BASE, 'w') as f:
                f.write(baseline.to_json(orient='index').replace("nan", "null"))
        prefix_baseline = "PARTIALLY FAILED" if baseline.log.count("FAIL") else "SUCCESS"
        context += [f'- [{prefix_baseline}] BUILD Baseline', baseline.log, '']
    except Exception as error:
        baseline = MarketBaseline(update=False)
        prefix_baseline = "FAILED"
        context += [f'- [{prefix_baseline}] BUILD Baseline', f'  : {error}', '* Using latest baseline', '']
    TRADING_DATE = baseline['date'].values[0]
    if not isinstance(TRADING_DATE, str):
        TRADING_DATE = f"{datetime_as_string(TRADING_DATE, unit='D').replace('-', '/')}"


    marketMap = MarketMap(baseline, TRADING_DATE)
    # TODO
    # metadata clear (불필요 key 값 삭제하기)
    try:
        if not PATH.MAP.startswith('http'):
            mapT = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                   .get_template('marketmap.js')
            mapJs = mapT.render(
                srcIndicatorOpt=dumps(marketMap.meta),
                srcTicker=marketMap.to_json(orient='index'),
                srcColors=marketMap.colors.to_json(orient='index')
            ).replace("nan", "null").replace("NaN", "null")
            with open(PATH.JS.MAP, 'w', encoding='utf-8') as file:
                file.write(mapJs)
        context += [f'- [SUCCESS] BUILD Market-Map', marketMap.log, '']
    except Exception as error:
        context += [f'- [FAILED] BUILD Market-Map', f'  : {error}', '']

    minify.css()
    minify.js()

    service = marketmap.render(
        localhost=LOCAL_HOST,
        title="\uc2dc\uc7a5\uc9c0\ub3c4 MARKET MAP",
        trading_date=f'{TRADING_DATE}\u0020\uc885\uac00\u0020\uae30\uc900'
    )
    with open(PATH.HTML.MAP, 'w', encoding='utf-8') as file:
        file.write(service)

    mail.context = "\n".join(context)
    if "PARTIALLY FAILED" in mail.context:
        prefix = "PARTIALLY FAILED"
    elif "FAILED" in mail.context:
        prefix = "FAILED"
    else:
        prefix = "SUCCESS"
    mail.subject = f'[{prefix}] BUILD BASELINE on {TRADING_DATE}'

    if LOCAL_HOST:
        print(mail.subject)
        print(mail.context)
        print(baseline)
        print("-" * 50)
        print(marketMap)
    else:
        mail.send()

