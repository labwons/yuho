from pandas import Series
from typing import Union


BLUE2RED = [
    '#1861A8', # R24 G97 B168
    '#228BE6', # R34 G139 B230
    '#74C0FC', # R116 G192 B252
    '#A6A6A6', # R168 G168 B168
    '#FF8787', # R255 G135 B135
    '#F03E3E', # R240 G62 B62
    '#C92A2A'  # R201 G42 B42
]

RED2GREEN = [
    '#F63538', # R246 G53 B56
    '#BF4045', # R191 G64 B69
    '#8B444E', # R139 G68 B78
    '#414554', # R65 G69 B84
    '#35764E', # R53 G118 B78
    '#2F9E4F', # R47 G158 B79
    '#30CC5A'  # R48 G204 B90
]

HEX2RGB = lambda x: (int(x[1:3], 16), int(x[3:5], 16), int(x[5:], 16))
CONNECT = lambda x, x1, y1, x2, y2: ( (y2 - y1) / (x2 - x1) ) * (x - x1) + y1

def paint(data:Series, tag:dict, replace_last:bool=True) -> Series:
    scale = tag['scale']
    scaleNa = tag['scaleNa']
    bound = tag['bound'].copy()
    for n, b in enumerate(bound):
        if not b:
            bound[n] = 0
    def _paint(val:Union[int, float, str]) -> str:
        if val == tag['na']:
            return scale[scaleNa]
        val = float(val)
        if val <= bound[0]:
            return scale[0]
        elif val > bound[-1]:
            return scale[-1]
        n = 0
        while n < len(bound) - 1:
            if bound[n] < val <= bound[n + 1]:
                break
            n += 1
        r1, g1, b1 = HEX2RGB(scale[n])
        r2, g2, b2 = HEX2RGB(scale[n + 1])
        r = CONNECT(val, bound[n], r1, bound[n + 1], r2)
        g = CONNECT(val, bound[n], g1, bound[n + 1], g2)
        b = CONNECT(val, bound[n], b1, bound[n + 1], b2)
        return f'#{hex(int(r))[2:]}{hex(int(g))[2:]}{hex(int(b))[2:]}'.upper()
    color = data.apply(_paint)
    if replace_last:
        color.iloc[-1] = '#C8C8C8'
    return color