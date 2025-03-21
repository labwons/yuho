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
        from ..render import (
            config,
            bubble,
            marketmap
        )
        from .service.baseline import MarketBaseline
        from .service.bubble import MarketBubble
        from .service.marketmap import MarketMap
        from .maintenance.sitemap import sitemap
    except ImportError:
        from src.common.path import PATH
        from src.common.report import eMail
        from src.render import (
            config,
            bubble,
            marketmap
        )
        from src.build.service.baseline import MarketBaseline
        from src.build.service.bubble import MarketBubble
        from src.build.service.marketmap import MarketMap
        from src.build.maintenance.sitemap import sitemap
    from datetime import datetime, timezone, timedelta
    from json import dumps
    from pandas import set_option as PRINT_DATA
    from pykrx.stock import get_nearest_business_day_in_a_week
    from numpy import datetime_as_string
    from time import sleep
    import os


    # ---------------------------------------------------------------------------------------
    # GOOGLE ADSENSE CONFIGURATION
    # ---------------------------------------------------------------------------------------
    ADSENSE_PROPERTY = {
        "meta": [{"name": "google-adsense-account", "content": config.ADSENSE_ID}],
        "script": [{
            "data-ad-client": config.ADSENSE_ID,
            "async src": "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
            "pos": "top"
        }],
        "ad_title": [{
            "class": "adsbygoogle",
            "style": "display:block",
            "data-ad-client": config.ADSENSE_ID,
            "data-ad-slot": "9705057757",
            "data-ad-format": "auto",
            "data-full-width-responsive": "true",
        }]
    }


    # ---------------------------------------------------------------------------------------
    # ENVIRONMENT SETTINGS
    # ---------------------------------------------------------------------------------------
    PRINT_DATA('display.expand_frame_repr', False)

    ADSENSE    = False
    BASE_DIR   = PATH.DOCS
    CLOCK      = lambda zone: datetime.now(zone)
    LOCAL_HOST = os.getenv('LOCAL_HOST') is None
    LOCAL_ZONE = timezone(timedelta(hours=9))
    ROUTER     = '/yuho'

    if LOCAL_HOST:
        # FOR LOCAL HOST TESTING, EXTERNAL DIRECTORY IS RECOMMENDED AND USED. USING THE SAME
        # LOCAL HOSTING DIRECTORY WITH DEPLOYMENT DIRECTORY, DEPLOYMENT MIGHT BE CORRUPTED.
        # IF YOU WANT TO USE DIFFERENT PATH FOR LOCAL HOST TESTING, BELOW {ROOT} VARIABLE ARE
        # TO BE CHANGED.
        BASE_DIR = os.path.join(PATH.DOWNLOADS, 'labwons')
        PATH.copytree(PATH.DOCS, BASE_DIR)

    if not LOCAL_HOST:
        # ON GITHUB ACTIONS, SYSTEM EXITS WHEN THE LATEST TRADING DATE AND CURRENT DATETIME
        # IS NOT MATCHED. THIS CODE IS IMPLEMENTED IN ORDER TO AVOID RUNNING ON WEEKDAY WHILE
        # HOLIDAYS OF THE MARKET.
        if get_nearest_business_day_in_a_week() != datetime.today().strftime("%Y%m%d"):
            raise SystemExit

        # ON GITHUB ACTIONS, IF SCHEDULED CRON TIME IS ACTIVATED BEFORE THE MARKET IS CLOSED,
        # WHICH ALMOST NEVER HAPPENS, BUILD AND DEPLOY WILL HOLD UNTIL THE MARKET IS CLOSED.
        now = CLOCK(LOCAL_ZONE)
        while now.hour == 3 and now.minute < 31:
            sleep(30)
            now = CLOCK(LOCAL_ZONE)

    # ---------------------------------------------------------------------------------------
    # UPDATE PORTFOLIO
    # ---------------------------------------------------------------------------------------


    # ---------------------------------------------------------------------------------------
    # UPDATE BASELINE
    # ---------------------------------------------------------------------------------------
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


    # ---------------------------------------------------------------------------------------
    # BUILD MARKET MAP
    # ---------------------------------------------------------------------------------------
    marketMap = MarketMap(baseline)
    # TODO
    # metadata clear (불필요 key 값 삭제하기)
    try:
        mapJsKeys = {
            "srcIndicatorOpt" : dumps(marketMap.meta),
            "srcTicker" : marketMap.to_json(orient='index'),
            "srcColors" : marketMap.colors.to_json(orient='index')
        }
        marketmap.javascript(**mapJsKeys).save(os.path.join(BASE_DIR, r'src/js/'))

        mapKeys = config.templateKeys()
        mapKeys.merge(**marketmap.defaultMarketMapAttribute)
        mapKeys["trading_date"] = f'{TRADING_DATE}\u0020\uc885\uac00\u0020\uae30\uc900'

        if LOCAL_HOST:
            # IF YOU ARE DEBUGGING IN LOCAL HOST, MINIFIED RESOURCES IS NOT USED AND WILL BE EXPANDED TO
            # FULL TEXT RESOURCES. THE FULL TEXTED RESOURCES ARE ONLY AFFECT TO THE DEBUGGING ENVIRONMENT,
            # IF YOU WANT TO CHANGE THE SOURCE, YOU NEED TO CHANGE THE TEMPLATE.
            mapKeys.fulltext()
        if not LOCAL_HOST:
            mapKeys.route(ROUTER)
        if ADSENSE:
            mapKeys.merge(**ADSENSE_PROPERTY)
        marketmap.html(**mapKeys).save(BASE_DIR)

        context += [f'- [SUCCESS] Deploy Market-Map', marketMap.log, '']
    except Exception as error:
        context += [f'- [FAILED] Deploy Market-Map', f'  : {error}', '']


    # ---------------------------------------------------------------------------------------
    # BUILD BUBBLE
    # ---------------------------------------------------------------------------------------
    marketBubble = MarketBubble(baseline)
    try:
        bubbleJsKeys = {
            "srcIndicatorOpt": dumps(marketBubble.meta),
            "srcTickers": marketBubble.to_json(orient='index'),
            "srcSectors": dumps(marketBubble.sector)
        }
        bubble.javascript(**bubbleJsKeys).save(os.path.join(BASE_DIR, r'src/js/'))

        bubbleKeys = config.templateKeys()
        bubbleKeys.merge(**bubble.defaultBubbleAttribute)
        bubbleKeys["trading_date"] = f'{TRADING_DATE}\u0020\uc885\uac00\u0020\uae30\uc900'

        if LOCAL_HOST:
            bubbleKeys.fulltext()
        if not LOCAL_HOST:
            bubbleKeys.route(ROUTER)
        if ADSENSE:
            bubbleKeys.merge(**ADSENSE_PROPERTY)
        bubble.html(**bubbleKeys).save(os.path.join(BASE_DIR, 'bubble'))

        context += [f'- [SUCCESS] Deploy Market-Bubble', marketBubble.log, '']
    except Exception as error:
        context += [f'- [FAILED] Deploy Market-Bubble', f'  : {error}', '']


    # ---------------------------------------------------------------------------------------
    # BUILD RESOURCES
    # ---------------------------------------------------------------------------------------
    try:
        resources = config.deploymentResource()
        resources.LOCAL_HOST = LOCAL_HOST
        resources.BASE_DIR = BASE_DIR
        if not LOCAL_HOST:
            resources.router = ROUTER
        resources.render_css()
        resources.minify()
        context += [f'- [SUCCESS] CSS Deployment and Minify Resources', '']
    except Exception as error:
        context += [f'- [FAILED] CSS Deployment and Minify Resources', f'  : {error}', '']

    sitemap(BASE_DIR, "https://labwons.com", os.path.join(BASE_DIR, "sitemap.xml"))


    # ---------------------------------------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------------------------------------
    mail = eMail()
    mail.context = "\n".join(context)
    prefix = "SUCCESS"
    if "FAILED" in mail.context:
        prefix = "FAILED"
    mail.subject = f'[{prefix}] BUILD BASELINE on {TRADING_DATE} {datetime.now(LOCAL_ZONE).strftime("%H:%M")}'

    if LOCAL_HOST:
        print(f'{mail.subject}\n{mail.context}\n')
        # print(f'{baseline}\n{"-" * 50}\n{marketMap}')
    else:
        mail.send()

