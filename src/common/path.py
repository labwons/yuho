from pandas import Series
import os, shutil


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

    # HTML = html(ROOT)
    HTML = Series()
    HTML.MAP = os.path.join(ROOT, r'docs/index.html')
    HTML.BUBBLE = os.path.join(ROOT, r'docs/bubble/index.html')
    HTML.MACRO = os.path.join(ROOT, r'docs/macro/index.html')
    HTML.TEMPLATES = os.path.join(ROOT, r'src/render/templates')

    JS = Series()
    JS.MAP = os.path.join(ROOT, r'docs/src/js/marketmap.js')

    @classmethod
    def copy(cls, src:str, dst:str, rename:str=""):
        if not os.path.exists(src):
            raise FileNotFoundError(f"원본 파일이 존재하지 않습니다: {src}")

        ext = f".{src.split('.')[-1]}"
        new = os.path.basename(src) if not rename else f"{rename}{ext}"
        dst = os.path.join(dst, new)
        if not os.path.isfile(dst):
            shutil.copy2(src=src, dst=dst)
        return dst

    @classmethod
    def copytree(cls, src:str, dst:str):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return





if __name__ == "__main__":
    # print(PATH.ROOT)
    # print(PATH.GROUP)
    # print(PATH.STATE)
    # print(PATH.SPEC)
    # print(PATH.INDEX)
    # print(PATH.MAP)
    print(PATH.HTML.MAP)
