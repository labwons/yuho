from pandas import Series
import os


class PATH:
    try:
        ROOT = os.path.dirname(__file__)
        while not ROOT.endswith('yuho'):
            ROOT = os.path.dirname(ROOT)
    except NameError:
        ROOT = 'https://raw.githubusercontent.com/labwons/yuho/main/'

    try:
        DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        DOWNLOADS = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads')
    except KeyError:
        DESKTOP = DOWNLOADS = ROOT

    BASE   = os.path.join(ROOT, r'src/fetch/market/json/baseline.json')
    GROUP  = os.path.join(ROOT, r'src/fetch/market/json/group.json')
    INDEX  = os.path.join(ROOT, r'src/fetch/market/json/index.json')
    SPEC   = os.path.join(ROOT, r'src/fetch/market/json/spec.json')
    STATE  = os.path.join(ROOT, r'src/fetch/market/json/state.json')

    DOCS   = os.path.join(ROOT, r'docs')
    BUBBLE = os.path.join(ROOT, r'docs/src/json/bubble.json')
    MAP    = os.path.join(ROOT, r'docs/src/json/treemap.json')
    MACRO  = os.path.join(ROOT, r'docs/src/json/macro.json')

    # HTML = html(ROOT)
    HTML = Series()
    HTML.MAP = os.path.join(ROOT, r'docs/index.html')
    HTML.BUBBLE = os.path.join(ROOT, r'docs/bubble/index.html')
    HTML.MACRO = os.path.join(ROOT, r'docs/macro/index.html')
    HTML.TEMPLATES = os.path.join(ROOT, r'src/render/templates')

    JS = Series()
    JS.MAP = os.path.join(ROOT, r'docs/src/js/marketmap.js')





if __name__ == "__main__":
    # print(PATH.ROOT)
    # print(PATH.GROUP)
    # print(PATH.STATE)
    # print(PATH.SPEC)
    # print(PATH.INDEX)
    # print(PATH.MAP)
    print(PATH.HTML.MAP)
