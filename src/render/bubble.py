try:
    from ..common.path import PATH
    from .config import Kwargs
except ImportError:
    from src.common.path import PATH
    from src.render.config import Kwargs
from jinja2 import Environment, FileSystemLoader
import os


defaultBubbleAttribute = {
    "title": "\uc885\ubaa9\u0020\ubd84\ud3ec BUBBLES",
    "link": [{"rel": "stylesheet", "href": f"/src/css/bubble.min.css"}],
    "script": [{"src": f"/src/js/bubble.min.js", "pos": "bottom"}],
    "service_opt_l": ('\n' + '\t' * 5).join([
        '',
        '\t<select name="x" class="bubble-select bubble-x"></select>',
        '\t<select name="y" class="bubble-select bubble-y"></select>',
        '\t<div class="bubble-button bubble-edit"><i class="fa fa-edit"></i></div>',
        '\t<div class="bubble-button bubble-sizing"><i class="fa fa-compress"></i></div>',
        ''
    ]),
    "service_opt_r": ('\n' + '\t' * 5).join([
        '',
        '\t<select name="classifier" class="bubble-select bubble-classify"></select>',
        '\t<select name="tickers" class="bubble-select bubble-searchbar"><option></option></select>',
        ''
    ]),
    # "service_items": '<span class="bubble-legend"></span>' * 7,
    "service_notice": (
            '\ubaa8\ub4e0\u0020\ud22c\uc790\uc758\u0020\ucc45\uc784\uc740\u0020\ub2f9\uc0ac\uc790\uc5d0\uac8c\u0020\uc788\uc2b5\ub2c8\ub2e4\u002e\u0020'
            '\u002a\ud45c\uc2dc\ub294\u0020\ucf54\uc2a4\ub2e5\u0020\uc885\ubaa9\uc785\ub2c8\ub2e4\u002e'
            '\ucf54\uc2a4\ud53c\u0032\u0030\u0030\u002c\u0020\ucf54\uc2a4\ub2e5\u0031\u0035\u0030\u0020\ud3b8\uc131\u0020\uc885\ubaa9\uc73c\ub85c\u0020\uad6c\uc131\ub418\uc5c8\uc2b5\ub2c8\ub2e4\u002e '
            '\u0050\u0043\u0020\ud658\uacbd\uc5d0\uc11c\u0020\ub9c8\uc6b0\uc2a4\u0020\ucee4\uc11c\ub97c\u0020\uc62c\ub9ac\uac70\ub098\u0020\ubaa8\ubc14\uc77c\u0020\uae30\uae30\uc5d0\uc11c\u0020\uae38\uac8c\u0020\ub204\ub974\uba74\u0020\uc138\ubd80\u0020\uc815\ubcf4\uac00\u0020\ub098\ud0c0\ub0a9\ub2c8\ub2e4\u002e '
            '\uc885\ubaa9\uc774\ub098\u0020\uc139\ud130\ub97c\u0020\ud074\ub9ad\u0028\ud0ed\u0029\ud558\uba74\u0020\ud655\ub300\u002f\uc7ac\ud3b8\ub429\ub2c8\ub2e4\u002e '
            '\uc7ac\ud3b8\ub41c\u0020\uc9c0\ub3c4\uc5d0\uc11c\u0020\uc0c1\ub2e8\u0020\ubd84\ub958\uba85\uc744\u0020\ud074\ub9ad\u0028\ud0ed\u0029\ud558\uba74\u0020\uc0c1\uc704\u0020\ubd84\ub958\u0020\uae30\uc900\uc73c\ub85c\u0020\uc7ac\ud3b8\uc774\u0020\ub429\ub2c8\ub2e4\u002e'
    ),
    "faq": [
        {'q': '실시간 업데이트는 안 되나요?', 'a': '안타깝지만 제공되지 않습니다.<i class="fa fa-frown-o"></i>'},
        {'q': '제가 찾는 종목이 없어요.', 'a': '가독성을 위해 대형주는 코스피200 지수와 코스닥150 지수 종목으로 구성하였으며 이외 종목은 제외됩니다.'},
        {'q': '언제 업데이트 되나요?', 'a': '정규장 시간 마감(15:30) 이후 15분~30분 내로 업데이트 됩니다. 휴장일에는 마지막 개장일 데이터가 유지됩니다.'},
        {'q': '자료 출처가 어디인가요?',
         'a': '섹터/업종 분류는 GICS 산업 분류 및 WISE INDEX를 참고하여 재구성하였습니다. 수익률은 한국거래소(KRX) 데이터를 참고하였으며 기타 지표는 네이버 및 에프앤가이드를 참고하였습니다.'},
        {'q': '정보 수정이 필요해요.',
         'a': '고장 신고, 정보 정정 및 기타 문의는 snob.labwons@gmail.com 으로 연락주세요!<i class="fa fa-smile-o"></i>'},
    ]
}

class html:

    def __init__(self, **kwargs):
        self.src = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                   .get_template('service_v2.html') \
                   .render(**kwargs)
        return

    def save(self, path:str):
        file = os.path.join(path, 'index.html')
        with open(file, mode='w', encoding='utf-8') as index:
            index.write(self.src)
        return


class javascript:

    def __init__(self, **kwargs):
        self.src = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
                   .get_template('bubble.js') \
                   .render(**kwargs) \
                   .replace("nan", "null").replace("NaN", "null")
        return

    def save(self, path:str):
        file = os.path.join(path, 'marketmap.js')
        with open(file, mode='w', encoding='utf-8') as js:
            js.write(self.src)
        return

