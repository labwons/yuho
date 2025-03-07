"""
TITLE   : BUILD CACHE
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

    mail = eMail()

    context = ['DETAILS']
    # try:
    group = MarketGroup(update=True)
    if not PATH.GROUP.startswith('http'):
        with open(PATH.GROUP, 'w') as f:
            f.write(group.to_json(orient='index').replace("nan", ""))
    prefix_group = "PARTIALLY FAILED" if "FAIL" in group.log else "SUCCESS"
    context += [f"- [{prefix_group}] MARKET GROUP: ", group.log, ""]
    # except Exception as report:
    #     prefix_group = 'FAILED'
    #     context += [f"- [{prefix_group}] MARKET GROUP: ", f'{report}', ""]
    #
    # try:
    #     index = MarketIndex(update=True)
    #     if not PATH.INDEX.startswith('http'):
    #         with open(PATH.INDEX, 'w') as f:
    #             f.write(index.to_json(orient='index').replace("nan", ""))
    #     prefix_index = "PARTIALLY FAILED" if "FAIL" in index.log else "SUCCESS"
    #     context += [f"- [{prefix_index}] MARKET INDEX: ", index.log, ""]
    # except Exception as report:
    #     prefix_index = "FAILED"
    #     context += [f"- [{prefix_index}] MARKET INDEX: ", f'{report}', ""]
    #
    # try:
    #     spec = MarketSpec(update=True)
    #     if not PATH.SPEC.startswith('http'):
    #         with open(PATH.SPEC, 'w') as f:
    #             f.write(spec.to_json(orient='index').replace("nan", ""))
    #     prefix_spec = "PARTIALLY FAILED" if "FAIL" in spec.log else "SUCCESS"
    #     context += [f"- [{prefix_spec}] MARKET SPECIFICATION: ", spec.log, ""]
    # except Exception as report:
    #     prefix_spec = 'FAILED'
    #     context += [f"- [{prefix_spec}] MARKET SPECIFICATION: ", f'{report}', ""]
    #
    # if "PARTIALLY FAILED" in [prefix_group, prefix_index, prefix_spec]:
    #     prefix = "PARTIALLY FAILED"
    # elif "FAILED" in [prefix_group, prefix_index, prefix_spec]:
    #     prefix = "FAILED"
    # else:
    #     prefix = "SUCCESS"
    #
    #
    # mail.subject = f'[{prefix}] UPDATE BASELINE CACHE on {datetime.today().strftime("%Y/%m/%d")}'
    # mail.context = "\n".join(context)
    # mail.send()