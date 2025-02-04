import os


class PATH:

    try:
        ROOT = os.path.dirname(__file__)
        while not ROOT.endswith('yuho'):
            ROOT = os.path.dirname(ROOT)
    except NameError:
        ROOT = 'https://raw.githubusercontent.com/labwons/yuho/main/'

    GROUP  = os.path.join(ROOT, r'docs/json/marketmap/marketmap.json')
    STATE  = os.path.join(ROOT, r'docs/json/marketmap/state.json')
    PRICE  = os.path.join(ROOT, r'docs/json/marketmap/price.json')
    SPECS  = os.path.join(ROOT, r'docs/json/marketmap/specs.json')
    INDEX  = os.path.join(ROOT, r'docs/json/macro/index.json')
    BUBBLE = os.path.join(ROOT, r'docs/json/service/bubble.json')
    TRMAP  = os.path.join(ROOT, r'docs/json/service/treemap.json')
    MACRO  = os.path.join(ROOT, r'docs/json/service/macro.json')
    try:
        DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        DOWNLOADS = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
    except KeyError:
        DESKTOP = DOWNLOADS = ROOT
    


if __name__ == "__main__":
    print(PATH.ROOT)
    print(PATH.GROUP)
    print(PATH.STATE)
    print(PATH.PRICE)
    print(PATH.SPECS)
    print(PATH.INDEX)
    print(PATH.TRMAP)