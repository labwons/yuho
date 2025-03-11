try:
    from ..common.path import PATH
except ImportError:
    from src.common.path import PATH
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Union
import csscompressor, jsmin, os


ROOT = '/yuho'

class Resources:

    def __init__(self, localhost:bool = False):
        __src__ = {'css':[], 'js':[]}
        for _dir, _folder, _files in os.walk(PATH.DOCS):
            for _file in _files:
                if _file.endswith('js') and not _file.endswith('.min.js'):
                    __src__['js'].append(os.path.join(_dir, _file))
                elif _file.endswith('css') and not _file.endswith('.min.css'):
                    __src__['css'].append(os.path.join(_dir, _file))
                else:
                    continue
        self.__src__ = __src__
        self.__loc__ = localhost
        return

    def render_css(self):
        style = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                .get_template('style.css') \
                .render(root='' if self.__loc__ else ROOT)
        with open(os.path.join(PATH.DOCS, "src/css/style.css"), "w", encoding="utf-8") as css:
            css.write(style)

        marketmap = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                    .get_template('marketmap.css') \
                    .render(root='' if self.__loc__ else ROOT)
        with open(os.path.join(PATH.DOCS, "src/css/marketmap.css"), "w", encoding="utf-8") as css:
            css.write(marketmap)
        return

    def minify(self):
        for css in self.__src__['css']:
            with open(css, 'r', encoding='utf-8') as file:
                src = file.read()
            with open(css.replace(".css", ".min.css"), "w", encoding='utf-8') as file:
                file.write(csscompressor.compress(src))

        for js in self.__src__['js']:
            with open(js, 'r', encoding='utf-8') as file:
                src = file.read()
            with open(js.replace(".js", ".min.js"), "w", encoding='utf-8') as file:
                file.write(jsmin.jsmin(src))
        return


class Kwargs:

    __ADS__: str = "ca-pub-7507574593260609"
    __NAV__: Dict[str, str] = {'bubble': '종목 분포', 'macro': '경제 지표', 'portfolio': '투자 종목'}
    def __init__(self, adsense:bool = False, localhost:bool = False):
        self._ad, self._lc = adsense, localhost
        self.__root__ = root = '' if localhost else ROOT
        self.__item__:Dict = {}
        self.__meta__:List[Dict] = [
            {"charset": "UTF-8"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
        ]
        self.__link__:List[Dict] = [
            {"rel": "stylesheet", "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"},
            {"rel": "stylesheet", "href": f"{root}/src/css/select2.min.css"},
            {"rel": "stylesheet", "href": f"{root}/src/css/style{'' if localhost else '.min'}.css"},
        ]
        self.__script__:List[Dict] = [
            {"src": f"{root}/src/js/jquery-3.6.1.min.js", "pos": "top"},
            {"src": f"{root}/src/js/plotly-2.35.2-r0.1.min.js", "pos": "top"},
            {"src": f"{root}/src/js/select2.min.js", "pos": "top"},
        ]
        return

    def __repr__(self) -> str:
        from pprint import pformat
        return pformat(self.encode())

    def __iter__(self):
        yield from self.encode()

    def __setitem__(self, key, value):
        self.__item__[key] = value
        return

    def __nav__(self) -> List[Dict[str, Union[str, dict]]]:
        nav:List[Dict] = [{"href": f"{self.__root__}/", "content": "시장 지도"}]
        for content in os.listdir(PATH.DOCS):
            if '.' in content or content == 'src':
                continue
            nav.append({'href': f'{self.__root__}/{content}', 'content': self.__NAV__[content]})
            # TODO
            # Portfolio의 경우 Sub Menu를 href: /{종목코드} text: 종목명 으로 변경
            sub = []
            for sub_content in os.listdir(os.path.join(PATH.DOCS, content)):
                if not '.' in sub_content and sub_content != "src":
                    sub.append({'href': f'/{content}/{sub_content}', 'content': sub_content})
            nav[-1].update({'sub': sub})
        return nav

    def encode(self) -> Dict[str, Union[List, Dict, str]]:
        self.__item__.update({
            "ad_title": [],
            "root": self.__root__,
            "meta": self.meta,
            "link": self.link,
            "script": self.script,
            "logo_header": self.logo_header,
            "logo_footer": self.logo_footer,
            "notice": self.notice,
            "contact": self.contact,
            "nav": self.__nav__()
        })
        if self._ad:
            self.__item__["ad_title"] = self.ad_title
        return self.__item__

    @property
    def meta(self) -> List[Dict]:
        if self._ad:
            ad_meta = {"name": "google-adsense-account", "content": self.__ADS__}
            if not ad_meta in self.__meta__:
                self.__meta__.append(ad_meta)
        return self.__meta__

    @meta.setter
    def meta(self, *meta:Dict):
        for _meta in meta:
            if not _meta in self.__meta__:
                self.__meta__.append(_meta)
        return

    @property
    def link(self) -> List[Dict]:
        self.__link__.append({"rel": "icon", "href": f"{self.__root__}/src/img/favicon.ico", "type": "image/x-icon"})
        return self.__link__

    @link.setter
    def link(self, *link):
        for _link in link:
            _link["href"] = f'{self.__root__}{_link["href"]}'
            if not _link in self.__link__:
                self.__link__.append(_link)
        return

    @property
    def script(self) -> List[Dict]:
        if self._ad:
            ad = {
                "data-ad-client": self.__ADS__,
                "async src": "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
                "pos":"top"
            }
            if not ad in self.__script__:
                self.__script__.append(ad)
        return self.__script__

    @script.setter
    def script(self, *script):
        for _script in script:
            if not "pos" in _script:
                raise KeyError("Please define the position of the script: 'top', 'mid', 'bottom'")
            _script["src"] = f'{self.__root__}{_script["src"]}'
            if not _script in self.__script__:
                self.__script__.append(_script)
        return

    @property
    def logo_header(self) -> str:
        return f"{self.__root__}/src/img/logo-text.png" if not self._lc else ""

    @property
    def logo_footer(self) -> str:
        return f"{self.__root__}/src/img/logo-footer.png" if not self._lc else ""

    @property
    def notice(self) -> str:
        return "본 홈페이지는 <b>개인 블로그</b>이며 여기서 취득한 어떤 정보도 법적인 효력을 갖지 못합니다. 모든 투자의 책임은 당사자에게 있습니다. 참고한 정보의 출처는 신뢰할 만하나, 열람 시점이나 제공처의 사정 따라 정보의 정확성이 달라질 수 있습니다."

    @property
    def contact(self) -> str:
        return "snob.labwons@gmail.com"

    @property
    def ad_title(self) -> List[Dict[str, str]]:
        return [{
            "class": "adsbygoogle",
            "style": "display:block",
            "data-ad-client": self.__ADS__,
            "data-ad-slot": "9705057757",
            "data-ad-format": "auto",
            "data-full-width-responsive": "true",
        }]


if __name__ == "__main__":
    kwargs = Kwargs(False, False)
    print(kwargs)
