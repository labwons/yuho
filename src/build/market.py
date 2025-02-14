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
    except ImportError:
        from src.common.path import PATH
        from src.common.report import eMail
        from src.build.service.baseline import MarketBaseline
    from datetime import datetime

    TODAY = datetime.today().strftime("%Y-%m-%d")[2:]

    mail = eMail()
    mail.subject = f'BUILD BASELINE on {TODAY}'
    try:
        baseline = MarketBaseline(update=True)
        if not PATH.BASE.startswith('http'):
            with open(PATH.BASE, 'w') as f:
                f.write(baseline.to_json(orient='index').replace("nan", ""))


    except Exception as report:
        mail.context = f"{report}"
    finally:
        mail.send()


