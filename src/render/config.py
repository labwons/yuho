try:
    from ..common.path import PATH
    from ..build.service.portfolio import ONSITE
except ImportError:
    from src.common.path import PATH
    from src.build.service.portfolio import ONSITE
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Union
import csscompressor, jsmin, os


ADSENSE_ID: str = "ca-pub-7507574593260609"
class deploymentResource:

    _root:str = ''
    def __init__(self, router:str=''):
        self.router = router
        return

    @property
    def BASE_DIR(self) -> str:
        if not self._root:
            raise AttributeError('ROOT MUST BE SET')
        return self._root

    @BASE_DIR.setter
    def BASE_DIR(self, root:str):
        self._root = root

    def render_css(self):
        style = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                .get_template('style.css') \
                .render(router=self.router)
        with open(os.path.join(self.BASE_DIR, "src/css/style.css"), "w", encoding="utf-8") as css:
            css.write(style)
        return

    def minify(self):
        for _dir, _folder, _files in os.walk(self.BASE_DIR):
            for _file in _files:
                if _file.endswith('js') and not _file.endswith('.min.js'):
                    js = os.path.join(_dir, _file)
                    with open(js, 'r', encoding='utf-8') as file:
                        src = file.read()
                    with open(js.replace(".js", ".min.js"), "w", encoding='utf-8') as file:
                        file.write(jsmin.jsmin(src))
                elif _file.endswith('css') and not _file.endswith('.min.css'):
                    css = os.path.join(_dir, _file)
                    with open(css, 'r', encoding='utf-8') as file:
                        src = file.read()
                    with open(css.replace(".css", ".min.css"), "w", encoding='utf-8') as file:
                        file.write(csscompressor.compress(src))
                else:
                    continue
        return


class templateKeys(dict):

    NAMING_KEY: Dict[str, str] = {'bubble': '종목 분포', 'macro': '경제 지표', 'portfolio': '투자 기록'}
    def __init__(self):
        super().__init__(
            meta=[
                {"charset": "UTF-8"},
                {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
            ],
            link=[
                {"rel": "icon", "href": f"/src/img/favicon.ico", "type": "image/x-icon"},
                {"rel": "stylesheet", "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"},
                {"rel": "stylesheet", "href": f"/src/css/select2.min.css"},
                {"rel": "stylesheet", "href": f"/src/css/style.min.css"},
            ],
            script=[
                {"src": f"/src/js/jquery-3.6.1.min.js", "pos": "top"},
                {"src": f"/src/js/plotly-2.35.2-r0.1.min.js", "pos": "top"},
                {"src": f"/src/js/select2.min.js", "pos": "top"},
                {"src": f"/src/js/common.min.js", "pos": "bottom"},
            ],
            logo_header=f"/src/img/logo-text.png",
            logo_footer=f"/src/img/logo-footer.png",
            notice="본 홈페이지는 <b>개인 블로그</b>이며 여기서 취득한 어떤 정보도 법적인 효력을 갖지 못합니다. 모든 투자의 책임은 당사자에게 있습니다. 참고한 정보의 출처는 신뢰할 만하나, 열람 시점이나 제공처의 사정 따라 정보의 정확성이 달라질 수 있습니다.",
            contact="snob.labwons@gmail.com",
            nav=self.navigate()

        )
        return

    def __format__(self, format_spec):
        from pprint import pformat
        return pformat(self)

    def merge(self, **kwargs):
        for key, items in kwargs.items():
            if not key in self:
                self[key] = items
                continue
            if isinstance(self[key], (str, int, float)):
                self[key] = items
            elif isinstance(self[key], list):
                self[key] += items
            elif isinstance(self[key], dict):
                self[key].update(items)
            else:
                raise AttributeError(f'Unknown Attribute Type for key: {key}, item: {items}')

    @classmethod
    def navigate(cls) -> List[Dict[str, Union[str, dict]]]:
        nav:List[Dict] = [{"href": f"/", "content": "시장 지도"}]
        for content in os.listdir(PATH.DOCS):
            if '.' in content or content == 'src':
                continue
            nav.append({'href': f'/{content}', 'content': cls.NAMING_KEY[content]})
            sub = []
            for sub_content in os.listdir(os.path.join(PATH.DOCS, content)):
                if not '.' in sub_content and sub_content != "src":
                    name = sub_content
                    if name in ONSITE:
                        name = ONSITE[name]["name"]
                    sub.append({'href': f'/{content}/{sub_content}', 'content': name})
            nav[-1].update({'sub': sub})
        return nav

    def route(self, root:str):
        _route = lambda path: path if path.startswith(root) else f'{root}{path}'

        copy = self.copy()
        for key, item in copy.items():
            if isinstance(item, list):
                for n, subitem in enumerate(item):
                    if "href" in subitem and subitem["href"].startswith("/"):
                        self[key][n]["href"] = _route(f'{root}{self[key][n]["href"]}')
                    elif "src" in subitem and subitem["src"].startswith("/"):
                        self[key][n]["src"] = _route(f'{root}{self[key][n]["src"]}')
                    else:
                        continue
            elif isinstance(item, str) and item.startswith("/"):
                self[key] = _route(item)
            else:
                continue

    def fulltext(self):
        copy = self.copy()
        for key, item in copy.items():
            if isinstance(item, list):
                for n, subitem in enumerate(item):
                    if "href" in subitem:
                        subkey = "href"
                    elif "src" in subitem:
                        subkey = "src"
                    else:
                        continue
                    if any([package in subitem[subkey] for package in ["select2", "jquery", "plotly"]]):
                        continue
                    if ".min" in subitem[subkey]:
                        self[key][n][subkey] = subitem[subkey].replace(".min", "")
            elif isinstance(item, str) and ".min" in item:
                self[key] = item.replace(".min", "")
            else:
                continue


def siteMap(site:List=None):
    if not site:
        site = templateKeys.navigate()
    print(site)


if __name__ == "__main__":
    # keys = templateKeys()
    # print(f"{keys}")
    # print("-" * 100)
    # keys.route('/yuho')
    # print(f"{keys}")


    siteMap()