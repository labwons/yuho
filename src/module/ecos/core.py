try:
    from ...common.web import Web
except ImportError:
    from dev.common.web import Web
from pandas import DataFrame
from xml.etree.ElementTree import  ElementTree, fromstring


__all__ = ["METADATA", "xml2df"]

ECOSMETA = {
    '기준금리': {
        'symbol': '722Y001',
        'code': '0101000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    'KORIBOR(3개월)': {
        'symbol': '817Y002',
        'code': '010150000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    'KORIBOR(6개월)': {
        'symbol': '817Y002',
        'code': '010151000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '국고채1년': {
        'symbol': '817Y002',
        'code': '010190000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '국고채2년': {
        'symbol': '817Y002',
        'code': '010195000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '국고채5년': {
        'symbol': '817Y002',
        'code': '010200001',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '국고채10년': {
        'symbol': '817Y002',
        'code': '010210000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '회사채3년(AA-)': {
        'symbol': '817Y002',
        'code': '010300000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '회사채3년(BBB-)': {
        'symbol': '817Y002',
        'code': '010320000',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '은행수신금리(신규)': {
        'symbol': '121Y002',
        'code': 'BEABAA2',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '은행수신금리(잔액)': {
        'symbol': '121Y013',
        'code': 'BEABAB2',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '은행대출금리(신규)': {
        'symbol': '121Y006',
        'code': 'BECBLA01',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },
    '은행대출금리(잔액)': {
        'symbol': '121Y015',
        'code': 'BECBLB01',
        'unit': '%',
        'category': '금리지표',
        'YoY': False,
        'MoM': False
    },


    '원/달러환율': {
        'symbol': '731Y003',
        'code': '0000003',
        'unit': '원',
        'category': '통화/유동성지표',
        'YoY': False,
        'MoM': False
    },
    'M2(평잔, 원계열)': {
        'symbol': '101Y004',
        'code': 'BBHA00',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    'M2(평잔, 계절조정)': {
        'symbol': '101Y003',
        'code': 'BBHS00',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '은행수신(말잔)': {
        'symbol': '104Y013',
        'code': 'BCB8',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '은행수신(평잔)': {
        'symbol': '104Y014',
        'code': 'BCA8',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '비은행수신(말잔)': {
        'symbol': '111Y007',
        'code': '1000000',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '비은행수신(평잔)': {
        'symbol': '111Y008',
        'code': '1000000',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '은행여신(말잔)': {
        'symbol': '104Y016',
        'code': 'BDCA1',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '비은행여신(말잔)': {
        'symbol': '111Y009',
        'code': '1000000',
        'unit': '십억원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': True
    },
    '증시예탁금': {
        'symbol': '901Y056',
        'code': 'S23A',
        'unit': '백만원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '신용융자잔고': {
        'symbol': '901Y056',
        'code': 'S23E',
        'unit': '백만원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },
    '신용대주잔고': {
        'symbol': '901Y056',
        'code': 'S23F',
        'unit': '백만원',
        'category': '통화/유동성지표',
        'YoY': True,
        'MoM': False
    },


    '수출지수': {
        'symbol': '403Y001',
        'code': '*AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '반도체수출': {
        'symbol': '403Y001',
        'code': '3091AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '반도체/디스플레이장비수출': {
        'symbol': '403Y001',
        'code': '3091AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '스마트폰/무선전화기수출': {
        'symbol': '403Y001',
        'code': '309512AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '자동차수출': {
        'symbol': '403Y001',
        'code': '3121AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '자동차부품수출': {
        'symbol': '403Y001',
        'code': '31213AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '음식료품수출': {
        'symbol': '403Y001',
        'code': '301AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '석탄및석유제품수출': {
        'symbol': '403Y001',
        'code': '304AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '철강수출': {
        'symbol': '403Y001',
        'code': '3071AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '전지수출': {
        'symbol': '403Y001',
        'code': '31013AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },
    '가전수출': {
        'symbol': '403Y001',
        'code': '31015AA',
        'unit': '-',
        'category': '수출지표',
        'YoY': True,
        'MoM': False
    },


    '소비자물가지수': {
        'symbol': '901Y009',
        'code': '0',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': False
    },
    '소비자물가지수(식료품 및 에너지 제외)': {
        'symbol': '901Y010',
        'code': 'DB',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': False
    },
    '소비자물가지수(서비스)': {
        'symbol': '901Y010',
        'code': '22',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': False
    },
    '생산자물가지수': {
        'symbol': '404Y014',
        'code': '*AA',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': False
    },
    '생산자물가지수(식료품 및 에너지 제외)': {
        'symbol': '404Y015',
        'code': 'S620AA',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': False
    },
    '생산자물가지수(서비스)': {
        'symbol': '404Y014',
        'code': '5AA',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': False
    },


    'KB부동산매매지수(아파트, 전국)': {
        'symbol': '901Y062',
        'code': 'P63AC',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    'KB부동산매매지수(아파트, 서울)': {
        'symbol': '901Y062',
        'code': 'P63ACA',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    'KB부동산전세지수(아파트, 전국)': {
        'symbol': '901Y063',
        'code': 'P64AC',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    'KB부동산전세지수(아파트, 서울)': {
        'symbol': '901Y063',
        'code': 'P64ACA',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    '아파트실거래지수(전국)': {
        'symbol': '901Y089',
        'code': '100',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    '아파트실거래지수(서울)': {
        'symbol': '901Y089',
        'code': '200',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    '아파트실거래지수(수도권)': {
        'symbol': '901Y089',
        'code': '300',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    '아파트실거래지수(경기)': {
        'symbol': '901Y089',
        'code': 'C00',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },
    '아파트실거래지수(지방광역시)': {
        'symbol': '901Y089',
        'code': 'M00',
        'unit': '-',
        'category': '물가/부동산지표',
        'YoY': True,
        'MoM': True
    },

    '경기선행지수순환변동': {
        'symbol': '901Y067',
        'code': 'I16E',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': False,
        'MoM': False
    },
    '경기동행지수순환변동': {
        'symbol': '901Y067',
        'code': 'I16D',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': False,
        'MoM': False
    },
    '제조업업황전망': {
        'symbol': '512Y014',
        'code': 'C0000/BA',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': True,
        'MoM': True
    },
    '제조업신규수주전망': {
        'symbol': '512Y014',
        'code': 'C0000/BD',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': True,
        'MoM': True
    },
    '제조업수출전망': {
        'symbol': '512Y014',
        'code': 'C0000/BM',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': True,
        'MoM': True
    },
    '제조업심리지수': {
        'symbol': '512Y014',
        'code': 'C0000/BY',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': True,
        'MoM': True
    },
    '소비자심리지수': {
        'symbol': '511Y002',
        'code': 'FME/99988',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': True,
        'MoM': True
    },
    '뉴스심리지수(실험통계)': {
        'symbol': '521Y001',
        'code': 'A001',
        'unit': '-',
        'category': '경제/심리지표',
        'YoY': False,
        'MoM': False
    },
    '실업률(원계열)': {
        'symbol': '901Y027',
        'code': 'I61BC/I28A',
        'unit': '%',
        'category': '경제/심리지표',
        'YoY': False,
        'MoM': False
    },
    '실업률(계절조정)': {
        'symbol': '901Y027',
        'code': 'I61BC/I28B',
        'unit': '%',
        'category': '경제/심리지표',
        'YoY': False,
        'MoM': False
    },
}


def xml2df(url: str, parser:str="") -> DataFrame:
    """
    정보-100 : 인증키가 유효하지 않습니다.
               인증키를 확인하십시오! 인증키가 없는 경우 인증키를 신청하십시오!
    정보-200 : 해당하는 데이터가 없습니다.
    에러-100 : 필수 값이 누락되어 있습니다.
               필수 값을 확인하십시오! 필수 값이 누락되어 있으면 오류를 발생합니다.
               요청 변수를 참고 하십시오!
    에러-101 : 주기와 다른 형식의 날짜 형식입니다.
    에러-200 : 파일타입 값이 누락 혹은 유효하지 않습니다.
               파일타입 값을 확인하십시오!
               파일타입 값이 누락 혹은 유효하지 않으면 오류를 발생합니다.
               요청 변수를 참고 하십시오!
    에러-300 : 조회건수 값이 누락되어 있습니다.
               조회시작건수/조회종료건수 값을 확인하십시오!
               조회시작건수/조회종료건수 값이 누락되어 있으면 오류를 발생합니다.
    에러-301 : 조회건수 값의 타입이 유효하지 않습니다.
               조회건수 값을 확인하십시오!
               조회건수 값의 타입이 유효하지 않으면 오류를 발생합니다.
               정수를 입력하세요.
    에러-400 : 검색범위가 적정범위를 초과하여 60초 TIMEOUT이 발생하였습니다.
               요청조건 조정하여 다시 요청하시기 바랍니다.
    에러-500 : 서버 오류입니다.
               OpenAPI 호출시 서버에서 오류가 발생하였습니다.
               해당 서비스를 찾을 수 없습니다.
    에러-600 : DB Connection 오류입니다.
               OpenAPI 호출시 서버에서 DB접속 오류가 발생했습니다.
    에러-601 : SQL 오류입니다.
               OpenAPI 호출시 서버에서 SQL 오류가 발생했습니다.
    에러-602 : 과도한 OpenAPI호출로 이용이 제한되었습니다.
               잠시후 이용해주시기 바랍니다.
    """
    exclude = ['row', 'P_STAT_CODE']
    resp = Web.text(url, parser=parser)
    root = ElementTree(fromstring(str(resp))).getroot()
    if root.find('CODE'):
        raise ConnectionError(f'{root.find("CODE").text} / {root.find("MESSAGE").text}')

    data = list()
    for tag in root.findall('row'):
        getter = dict()
        for n, t in enumerate([inner for inner in tag.iter()]):
            if t.tag in exclude:
                continue
            getter.update({t.tag: t.text})
        data.append(getter)
    return DataFrame(data=data) if data else DataFrame()