try:
    from ..common.path import PATH
except ImportError:
    from src.common.path import PATH
from typing import Any, Dict, List, Union
import csscompressor, jsmin, os


class minify:

    @classmethod
    def css(cls):
        for _dir, _folder, _files in os.walk(PATH.DOCS):
            for _file in _files:
                if _file.endswith('css') and not _file.endswith('.min.css'):
                    with open(os.path.join(_dir, _file), 'r', encoding='utf-8') as file:
                        src = file.read()
                    with open(os.path.join(_dir, _file.replace(".css", ".min.css")), "w", encoding='utf-8') as file:
                        file.write(csscompressor.compress(src))
        return

    @classmethod
    def js(cls):
        for _dir, _folder, _files in os.walk(PATH.DOCS):
            for _file in _files:
                if _file.endswith('js') and not _file.endswith('.min.js'):
                    with open(os.path.join(_dir, _file), 'r', encoding='utf-8') as file:
                        src = file.read()
                    with open(os.path.join(_dir, _file.replace(".js", ".min.js")), "w", encoding='utf-8') as file:
                        file.write(jsmin.jsmin(src))
        return


class DefaultKwargs(Dict):

    ADSENSE:bool = True
    TESTMODE:bool = False
    ROOT = '' if TESTMODE else '/docs'
    __ADS__:str = "ca-pub-7507574593260609"
    __nav__:Dict[str, str] = {'bubble': '종목 분포', 'macro': '경제 지표', 'portfolio': '투자 종목'}

    def __getitem__(self, item) -> Union[Dict, List[Dict], str]:
        kwargs = super().__getitem__(item)
        if self.ADSENSE:
            if item == "meta":
                kwargs.append({"name": "google-adsense-account", "content": self.__ADS__})
            if item == 'script-top':
                kwargs.append({"data-ad-client": self.__ADS__,
                               "async src": "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"})
            if item == 'ad1':
                kwargs.update({
                    "class": "adsbygoogle",
                    "style": "display:block",
                    "data-ad-client": self.__ADS__,
                    "data-ad-slot": "9705057757",
                    "data-ad-format": "auto",
                    "data-full-width-responsive": "true",
                })
        if item == 'link':
            kwargs.append({"rel": "icon", "href": f"{self.ROOT}/src/img/favicon.ico", "type": "image/x-icon"})
        return kwargs

    def __init__(self):
        __mem__ = self.__mem__ = {
            "meta": [
                {"charset": "UTF-8"},
                {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
            ],
            "link": [
                {"rel": "stylesheet", "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"},
                {"rel": "stylesheet", "href": f"{self.ROOT}/src/css/select2.min.css"},
                {"rel": "stylesheet", "href": f"{self.ROOT}/src/css/style.min.css"},
            ],
            "tscript": [
                    {"src": f"{self.ROOT}/src/js/jquery-3.6.1.min.js"},
                    {"src": f"{self.ROOT}/src/js/plotly-2.35.2-r0.1.min.js"},
                    {"src": f"{self.ROOT}/src/js/select2.min.js"},
            ],
            "bscript": [

            ],
            "logo_img": f"{self.ROOT}/src/img/logo-text.png" if not self.TESTMODE else "",
            "ad1": {},
            "footer_img": f"{self.ROOT}/src/img/logo-footer.png",
            "footer_notice": "본 홈페이지는 <b>개인 블로그</b>이며 여기서 취득한 어떤 정보도 법적인 효력을 갖지 못합니다. 모든 투자의 책임은 당사자에게 있습니다. 참고한 정보의 출처는 신뢰할 만하나, 열람 시점이나 제공처의 사정 따라 정보의 정확성이 달라질 수 있습니다.",
            "footer_contact": "snob.labwons@gmail.com"
        }
        if not self.TESTMODE:
            __mem__["nav"] = self.navigate()
        super().__init__(__mem__)
        return

    def __iter__(self):
        for key in self:
            if not self.ADSENSE:
                if key in ['ad1']:
                    continue
            yield key

    def __setitem__(self, key:str, value:Union[Dict, List, str]):
        if key in self.__mem__:
            if isinstance(self.__mem__[key], List):
                self.__mem__[key].append(value)
            elif isinstance(self.__mem__[key], Dict):
                self.__mem__[key].update(value)
            else:
                self.__mem__[key] = value
            return
        super().__setitem__(key, value)
        return

    @classmethod
    def navigate(cls) -> List[Dict[str, Union[str, dict]]]:
        nav:List[Dict] = [{"href": "/", "content": "시장 지도"}]
        for content in os.listdir(PATH.DOCS):
            if '.' in content or content == 'src':
                continue
            nav.append({'href': f'/{content}', 'content': cls.__nav__[content]})
            # TODO
            # Portfolio의 경우 Sub Menu를 href: /{종목코드} text: 종목명 으로 변경
            sub = []
            for sub_content in os.listdir(os.path.join(PATH.DOCS, content)):
                if not '.' in sub_content and sub_content != "src":
                    sub.append({'href': f'/{content}/{sub_content}', 'content': sub_content})
            nav[-1].update({'sub': sub})
        return nav
