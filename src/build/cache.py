"""
TITLE   : BASELINE
AUTHOR  : SNOB
CONTACT : snob.labwons@gmail.com
ROUTINE : 21:00+09:00UTC on weekday
"""
if __name__ == "__main__":
    try:
        from ..common.path import PATH
        from ..common.report import eMail
        from ..fetch.market.group import MarketGroup
        from ..fetch.market.index import MarketIndex
        from ..fetch.market.spec import MarketSpec
    except ImportError:
        from src.common.path import PATH
        from src.common.report import eMail
        from src.fetch.market.group import MarketGroup
        from src.fetch.market.index import MarketIndex
        from src.fetch.market.spec import MarketSpec
    from datetime import datetime
    TODAY = datetime.today().strftime("%Y-%m-%d")[2:]


    group = MarketGroup(update=True)
    if not PATH.GROUP.startswith('http'):
        with open(PATH.GROUP, 'w') as f:
            f.write(group.to_json(orient='index').replace("nan", ""))

    spec = MarketSpec(update=True)
    if not PATH.SPEC.startswith('http'):
        with open(PATH.SPEC, 'w') as f:
            f.write(spec.to_json(orient='index').replace("nan", ""))

    index = MarketIndex(update=True)
    if not PATH.INDEX.startswith('http'):
        with open(PATH.INDEX, 'w') as f:
            f.write(index.to_json(orient='index').replace("nan", ""))

    try:
        mail = eMail()
        mail.subject = f'UPDATE BASELINE CACHE on {TODAY}'
        mail.context = f"""
OVERVIEW: 
- FAIL COUNT: 
  1) MARKET GROUP: {group.log.count("Fail")}
  2) MARKET INDEX: {index.log.count("Fail")}
  3) STOCK SPEC: {spec.log.count("Fail")}

DETAILS:
- MARKET GROUP:
{group.log}

- MARKET INDEX:
{index.log}

- STOCK SPEC:
{spec.log}
"""
        mail.send()
    except Exception:
        pass