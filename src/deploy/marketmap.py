try:
    from ..common.path import PATH
    from .default import DefaultKwargs
except ImportError:
    from src.common.path import PATH
    from src.deploy.default import DefaultKwargs
from jinja2 import Environment, FileSystemLoader



def render(test_mode:bool=False):
    template = Environment(loader=FileSystemLoader('templates')) \
               .get_template('index.html')
    kwargs = DefaultKwargs()
    kwargs.ADSENSE = True
    kwargs['app_icon'] = '<i class="map-rewind fa fa-undo"></i>'
    kwargs['service_items'] = '<div class="map-legend"><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>'
    kwargs['service_notice'] = ('모든 투자의 책임은 당사자에게 있습니다. '
                                '*표시는 코스닥 종목입니다.'
                                '코스피200, 코스닥150 편성 종목으로 구성되었습니다. '
                                'PC 환경에서 마우스 커서를 올리거나 모바일 기기에서 길게 누르면 세부 정보가 나타납니다. '
                                '종목이나 섹터를 클릭(탭)하면 확대/재편됩니다. ')

    if test_mode:
        del kwargs['logo_img']
        del kwargs['nav']

    service = template.render(**kwargs)
    with open(PATH.HTML.MAP, 'w', encoding='utf-8') as file:
        file.write(service)
    return


if __name__ == "__main__":
    render(test_mode=True)