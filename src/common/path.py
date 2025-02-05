class PATH:
    import os

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

    GROUP  = os.path.join(ROOT, r'src/fetch/market/json/group.json')
    STATE  = os.path.join(ROOT, r'src/fetch/market/json/state.json')
    SPECS  = os.path.join(ROOT, r'src/fetch/market/json/specs.json')
    INDEX  = os.path.join(ROOT, r'src/fetch/market/json/index.json')

    BUBBLE = os.path.join(ROOT, r'docs/src/json/bubble.json')
    MAP    = os.path.join(ROOT, r'docs/src/json/treemap.json')
    MACRO  = os.path.join(ROOT, r'docs/src/json/macro.json')



if __name__ == "__main__":
    print(PATH.ROOT)
    print(PATH.GROUP)
    print(PATH.STATE)
    print(PATH.SPECS)
    print(PATH.INDEX)
    print(PATH.MAP)