try:
    from ..common.path import PATH
    from .config import DefaultKwargs
except ImportError:
    from src.common.path import PATH
    from src.render.config import DefaultKwargs
from jinja2 import Environment, FileSystemLoader



def render(test_mode:bool=False):
    template = Environment(loader=FileSystemLoader(PATH.HTML.TEMPLATES)) \
               .get_template('service_v2.html')
    kwargs = DefaultKwargs()
    kwargs.ADSENSE = True
    kwargs.TESTMODE = test_mode
    kwargs['title'] = 'TESTING'
    kwargs['trading_date'] = '2025/02/20'
    kwargs['link'] = {"rel": "stylesheet", "href": f"{kwargs.ROOT}/src/css/marketmap.min.css"}
    kwargs['service_opt_l'] = '''
                        <select name="type" class="map-select map-type"></select>
                        <select name="option" class="map-select map-option"></select>
                        <div class="map-button map-reset"><i class="fa fa-refresh"></i></div>
                        <div class="map-button map-switch"><i class="fa fa-signal"></i></div>
                    '''
    kwargs['service_opt_r'] = '''
                         <select class="map-select map-searchbar"><option></option></select>
                    '''
    kwargs['app_icon'] = '<i class="map-rewind fa fa-undo"></i>'
    kwargs['service_items'] = f'''{'<span class="map-legend"></span>' * 7}'''
    kwargs['service_notice'] = ('\ubaa8\ub4e0\u0020\ud22c\uc790\uc758\u0020\ucc45\uc784\uc740\u0020\ub2f9\uc0ac\uc790\uc5d0\uac8c\u0020\uc788\uc2b5\ub2c8\ub2e4\u002e\u0020'
                                '\u002a\ud45c\uc2dc\ub294\u0020\ucf54\uc2a4\ub2e5\u0020\uc885\ubaa9\uc785\ub2c8\ub2e4\u002e'
                                '\ucf54\uc2a4\ud53c\u0032\u0030\u0030\u002c\u0020\ucf54\uc2a4\ub2e5\u0031\u0035\u0030\u0020\ud3b8\uc131\u0020\uc885\ubaa9\uc73c\ub85c\u0020\uad6c\uc131\ub418\uc5c8\uc2b5\ub2c8\ub2e4\u002e '
                                '\u0050\u0043\u0020\ud658\uacbd\uc5d0\uc11c\u0020\ub9c8\uc6b0\uc2a4\u0020\ucee4\uc11c\ub97c\u0020\uc62c\ub9ac\uac70\ub098\u0020\ubaa8\ubc14\uc77c\u0020\uae30\uae30\uc5d0\uc11c\u0020\uae38\uac8c\u0020\ub204\ub974\uba74\u0020\uc138\ubd80\u0020\uc815\ubcf4\uac00\u0020\ub098\ud0c0\ub0a9\ub2c8\ub2e4\u002e '
                                '\uc885\ubaa9\uc774\ub098\u0020\uc139\ud130\ub97c\u0020\ud074\ub9ad\u0028\ud0ed\u0029\ud558\uba74\u0020\ud655\ub300\u002f\uc7ac\ud3b8\ub429\ub2c8\ub2e4\u002e '
                                '\uc7ac\ud3b8\ub41c\u0020\uc9c0\ub3c4\uc5d0\uc11c\u0020\uc0c1\ub2e8\u0020\ubd84\ub958\uba85\uc744\u0020\ud074\ub9ad\u0028\ud0ed\u0029\ud558\uba74\u0020\uc0c1\uc704\u0020\ubd84\ub958\u0020\uae30\uc900\uc73c\ub85c\u0020\uc7ac\ud3b8\uc774\u0020\ub429\ub2c8\ub2e4\u002e')
    kwargs['faq'] = [
        {'q': 'Testing Question 1', 'a': 'Testing Answer 1'},
        {'q': 'Testing Question 2', 'a': 'Testing Answer 2'},
        {'q': 'Testing Question 3', 'a': 'Testing Answer 3'},
        {'q': 'Testing Question 4', 'a': 'Testing Answer 4'},
        {'q': 'Testing Question 5', 'a': 'Testing Answer 5'},
        {'q': 'Testing Question 6', 'a': 'Testing Answer 6'},
        {'q': 'Testing Question 7', 'a': 'Testing Answer 7'},
    ]

    service = template.render(**kwargs)
    with open(PATH.HTML.MAP, 'w', encoding='utf-8') as file:
        file.write(service)
    return


if __name__ == "__main__":
    render(test_mode=False)