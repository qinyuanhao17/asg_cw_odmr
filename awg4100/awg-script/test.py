import sys
import traceback
import asyncio
import websockets
from copy import deepcopy

class A:
    ID = 0
    def __init__(self):
        self.id = A.ID
        A.ID += 1
        self.__name__ = 'A'

class ParameterError(Exception):
    def __init__(self, msg):
        super(Exception, self).__init__(msg)

class People(A):
    __name__ = 'People'

    def __init__(self, name, age=1):
        super(People, self).__init__()
        self.name = name
        self.age = age
    
    def __repr__(self):
        return '{}:{}'.format(self.id, self.name)
    
    def __add__(self, a):
        if isinstance(a, (int, float)):
            if a > 0:
                self.age += a
            else:
                raise ValueError('age shoule > 0')
        else:
            raise TypeError('can\'t add B by non-number type of <{}>'.format(type(a).__name__))
        return self

try:
    p1 = People('Alice', 17)
    p2  = People('Bob')
    People('Cathy')
    p3 = People("Davie")

    print(p1)
    print(p2)
    print(p3)

    print(type(p1).__name__)

    age = 12
    p3 + age
    # p3 + 'hh'
    # async def _test():
    #     async with websockets.connect('ws://127.0.0.1:12345') as websocket:
    #         msg = 'hello'
    #         await websocket.send(msg)
    # asyncio.get_event_loop().run_until_complete(_test())

    l1 = (0, [100, 200])
    l2 = (1, [300, 100, 100, 100])
    flag, ll = l2
    for i in range(len(ll)):
        print((i + flag)%2, end=',')
    print()
except:
    print('-'*60)
    trcbk = traceback.format_exc(limit=1)
    print(trcbk, end='')
    print('-'*60)


def mearge_two_wind(wnd1, wnd2, flag=False):
    """
    """
    vals = []
    idx1, idx2 = 0, 0
    pos1, pos2 = 0, 0
    while idx1 != len(wnd1) and idx2 != len(wnd2):
        vlen = min(wnd1[idx1][0] - pos1, wnd2[idx2][0] - pos2)
        _v = wnd1[idx1][1] * wnd2[idx2][1]
        if len(vals) == 0 or _v != vals[-1][1]:
            vals.append((vlen, _v))
        else:
            vals[-1] = (vals[-1][0]+vlen, vals[-1][1])

        pos1 += vlen
        if pos1 == wnd1[idx1][0]:
            idx1 += 1
            pos1 = 0
        pos2 += vlen
        if pos2 == wnd2[idx2][0]:
            idx2 += 1
            pos2 = 0
    
    if idx1 != len(wnd1) and pos1 != wnd1[-1][0]:
        rmLen = wnd1[idx1][0] - pos1
        for it in wnd1[idx1+1:]:
            rmLen += it[0]
        if vals[-1][1] == 0:
            vals[-1] += rmLen
        else:
            vals.append((rmLen, 0))
    
    if idx2 != len(wnd2) and pos2 != wnd2[-1][0]:
        rmLen = wnd2[idx2][0] - pos2
        for it in wnd2[idx2+1:]:
            rmLen += it[0]
        if vals[-1][1] == 0:
            vals[-1] += rmLen
        else:
            vals.append((rmLen, 0))
    return vals

wnd1 = [(1000, 1)]
wnd2 = [(100, 1), (100, 0), (100, 1)]
print(mearge_two_wind(wnd1, wnd2))