
"""
AWG 波形生成
运行环境：python3.7.6
"""

import os
import sys
import time
from copy import deepcopy
from struct import *

# 未知波形由 C++ 部分判断, 减少修改不同步的问题
#_ALLOWED_WAVE_TYPE = ['sin', 'sinc', 'gauss', 'square', 'triangle', 'mul', 'add', 'zero']

WD = ''
SR = 1.2

GAmp = 100

UP = 0xA0
DOWN = 0xA1

# 电压编码范围
_VOLTE_RANGE = 500.

# 输出的中间临时文件
_OUT_FILE = ""

# 调试用, 实时打印生成的波形
_SHOW_DATA_ = False


def log_and_exit(msg):
    """
    将错误信息写入临时文件并推出程序
    """
    global _OUT_FILE
    if _OUT_FILE is None or _OUT_FILE == '':
        file = 'awg-temp-file'
    else:
        file = _OUT_FILE
    msg = "!" + msg
    tdir = os.environ['TEMP']
    with open(os.path.join(tdir, file), 'w') as f:
        f.writelines(msg)
        f.close()
        print(msg)
    sys.exit(0)

#-----------------------------------------------------------------------------
"""
波形相关辅助函数
"""

def _encode(val):
    """
    将电压(mV)值映射到 0~65535
    """
    if val < -_VOLTE_RANGE:
        cd = 0
    elif val > _VOLTE_RANGE:
        cd = 0xffff
    else:
        cd = (val / _VOLTE_RANGE * 32767 + 32768)
    return int(cd)


def _decode(cd):
    """
    将 0~65535 映射到电压值(mV)
    """
    return (cd - 32768) / 32767. * _VOLTE_RANGE


def str_time():
    """
    精确到微妙时间戳用于标记缓存文件
    """
    return str(int(time.time()*1000000))


def cache_wave_file(data, mode='volt'):
    """
    创建二进制缓存文件, 格式如下
        0H00 - 0H03     'AWGw' 波形文件标识
        0H04 - 0H07     '\0u16' 或 '\0f32' 或 '\0f64'
        0H08 - 0H0B     uint32, 波形长度，点数
        0H0B - 0H0F     (空字段, 占位， 无用)
        0H10 - ...      数据块,
                            u16 表示数据块为编码的, 16位无符号整型
                            f32 表示mV为单位的电压值, 32位浮点
                            f64 表示mV为单位的电压值, 64位浮点
    """
    tdir = os.environ['TEMP']
    filepath = os.path.join(tdir, 'wave-cache-{}'.format(str_time()))
    if mode == 'code':
        dtype = b'\x00u16'
    else:
        dtype = b'\x00f64'
    with open(filepath, 'bw') as wf:
        wf.write(b'AWGw')
        wf.write(dtype)
        wf.write(pack('I', len(data)))
        wf.write(b'\x00\x00\x00\x00')
        if mode == 'code':
            wf.write(pack('{}H'.format(len(data)), *data))
        else:
            wf.write(pack('{}d'.format(len(data)), *data))
    return filepath


def _get_wave_file_length(filename):
    """
    获取 .wave 波形文件的长度, 并做一些校验
    文件格式见上
    """
    file_info = os.stat(filename)
    file_data_sz = (file_info.st_size - 16)
    err_msg = None
    length = 0

    if file_data_sz <= 0:
        err_msg = '{} is not a .wave file.'.format(wave)
    else:
        with open(filename, 'rb') as f:
            header = unpack('4s4sI', f.read(12))
            if header[0] != b'AWGw':
                err_msg = 'file {} is not a .wave file.'.format(wave)
            else:
                length = header[2]
                if header[1] == b'\x00u16':
                    if length != (file_data_sz // 2):
                        err_msg = 'file {} data length error'.format(wave)
                elif header[1] == b'\x00f32':
                    if length != (file_data_sz // 4):
                        err_msg = 'file {} data length error'.format(wave)
                elif header[1] == b'\x00f64':
                    if length != (file_data_sz // 8):
                        err_msg = 'file {} data length error'.format(wave)
                else:
                    err_msg = 'file {} unknown data format'.format(wave)
    return length, err_msg

#-----------------------------------------------------------------------------
"""
定义基本波形
"""

class Wind:
    """Wind 不会下载

    Wind 在中间文件中的表示:
        M1,0,1000,2000,1000     __----__
        M2,1,1000,2000,1000     --____--
    """
    WindId = 0
    def __init__(self, *data):
        self.id = Wind.WindId
        Wind.WindId += 1
        data = list(data)
        if Wind._data_check(data):
            # 合并数据数据
            self.vals = [(data[0], data[1])]
            for i in range(2, len(data), 2):
                if data[i+1] == self.vals[-1][1]:
                    self.vals[-1] = (self.vals[-1][0] + data[i], self.vals[-1][1])
                else:
                    self.vals.append((data[i], data[i+1]))
            self.length = 0
            for it in self.vals:
                self.length += it[0]
        else:
            raise ValueError('Wind parameters error')
    
    def _set_data(self, data):
        self.vals = data
    
    @staticmethod
    def _data_check(data):
        """
        检查数据是否合法
            [len1, val1, len2, val2, ...]
            其中 lenx > 0, valx 必须是 0 或 1
        """
        sz = len(data)
        
        if sz < 1:
            return False
        else:
            for i in range(0, sz, 2):
                if not(data[i] > 0 and (data[i+1] == 0 or data[i+1] == 1)):
                    return False
        return True

    def __mul__(self, obj):
        if isinstance(obj, WAVE):
            return obj * self
        if isinstance(obj, Wind):
            vals = Wind._merge_two_wind(self, obj, lambda a, b: a&b)
            ret = Wind(100, 1)
            ret._set_data(vals)
            return ret
        
    def __repr__(self):
        ret = 'M{},{}'.format(self.id, self.vals[0][1])
        for it in self.vals:
            ret += ',{}'.format(it[0])
        return ret
    
    @staticmethod
    def _merge_two_wind(wnd1, wnd2, func=None):
        """
        """
        vals = []
        idx1, idx2 = 0, 0
        pos1, pos2 = 0, 0
        while idx1 != len(wnd1.vals) and idx2 != len(wnd2.vals):
            vlen = min(wnd1.vals[idx1][0] - pos1, wnd2.vals[idx2][0] - pos2)
            _v = func(wnd1.vals[idx1][1], wnd2.vals[idx2][1])
            if len(vals) == 0 or _v != vals[-1][1]:
                vals.append((vlen, _v))
            else:
                vals[-1] = (vals[-1][0]+vlen, vals[-1][1])

            pos1 += vlen
            if pos1 == wnd1.vals[idx1][0]:
                idx1 += 1
                pos1 = 0
            pos2 += vlen
            if pos2 == wnd2.vals[idx2][0]:
                idx2 += 1
                pos2 = 0
        
        if idx1 != len(wnd1.vals) and pos1 != wnd2.vals[-1][0]:
            rmlen = wnd1.vals[idx1][0] - pos1
            for it in wnd1.vals[idx1+1:]:
                rmlen += it[0]
            if vals[-1][1] == 0:
                vals[-1] = (vals[-1][0]+rmlen, 0)
            else:
                vals.append((rmlen, 0))
            
        if idx2 != len(wnd2.vals) and pos2 != wnd2.vals[-1][0]:
            rmlen = wnd2.vals[idx2][0] - pos2
            for it in wnd2.vals[idx2+1:]:
                rmlen += it[0]
            if vals[-1][1] == 0:
                vals[-1] = (vals[-1][0]+rmlen, 0)
            else:
                vals.append((rmlen, 0))
        return vals

class WAVE:
    """
    构造一般波形
    WAVE在中间文件中的表示例子:
        W0,<type>,<length>,...|<marker> 
        W1,winded,W<id>,M<id>
    """
    WaveId = 0
    def __init__(self, wave, mode='volt'):
        self.id = WAVE.WaveId
        WAVE.WaveId += 1
        self._type = ''
        self.params = None      # 函数类型波形的参数, 第一个参数必须是长度
        self._data = None       # 值类型的数据, 保存为电压值
        self.corr_obj = None    # 运算相关的对象, 第一个是 WAVE, 第二个元素可以是 WAVE, Wind, int, float
        self._filepath = None   # 文件类型和缓存类型的绝对路径
        self._amplitude = 0     # 振幅，文件和缓存定义为1
        self._length = 0        # 长度，点数
        self.marker = None     # marker 信号: [len1,val1, <len2, val2>]
        
        if isinstance(wave, list) and isinstance(wave[0], (int, float)):
            """
            通过指定每个采样点的值
            长度大于 100 的缓存到文件中, 减少中间文件体积以及格式化文本的耗时
            """
            self._length = len(wave)
            if self._length > 536_870_912:
                raise ValueError('WAVE too long')
            elif self._length < 100:
                self.type = 'data'
                if mode == 'volt':
                    self.data = wave
                elif mode == 'code':
                    self.data = [_decode(v) for v in wave]
                else:
                    raise ValueError("unknown mode={}".format(mode))
            else:
                self.type = 'cache'
                self.filepath = cache_wave_file(wave, mode)
        elif isinstance(wave, str):
            """
            文件和函数类型
            """
            if len(wave) > 5 and wave[-5:] == '.wave':
                # 优先判断是不是文件
                right_path = False
                if os.path.isfile(wave):
                    self.filepath = wave
                    right_path = True
                elif os.path.isfile(os.path.join(WD, wave)):
                    self.filepath = os.path.join(WD, wave)
                    right_path = True

                if right_path:
                    self.type = 'file'
                    self._length, errmsg = _get_wave_file_length(self.filepath)
                    if errmsg != None:
                        raise ValueError(errmsg)
                else:
                    raise FileNotFoundError('{}'.format(wave))
            elif wave.isalpha():
                # 如果全部是字母, 暂时认为是一种函数类型
                # 未函数类型由 C++ 部分处理, 减少修改点, 防止修改时遗漏
                self.type = wave
            else:
                raise TypeError("unknow WAVE type name {}".format(wave))
        elif isinstance(wave, WAVE):
            # 必须要执行深度拷贝
            self._type = deepcopy(wave._type)
            self.params = deepcopy(wave.params)
            self._data = deepcopy(wave._data)
            self.corr_obj = wave.corr_obj
            self._filepath = deepcopy(wave._filepath)
            self._amplitude = wave._amplitude
            self._length = wave._length
            self.marker = deepcopy(wave.marker)
        else:
            raise TypeError("unknow WAVE type")
    
    def set_params(self, params):
        self.params = params
    
    def set_length(self, length):
        if length > 536_870_912:
            raise SystemError('WAVE too long')
        self._length = length

    def get_length(self):
        return self._length

    def __call__(self, loop):
        """ 用元组表示一个波形的循环 """
        return (self, loop)
    
    def _gen_wind_wave(self, wind):
        """ 生成加窗的波形 """
        ret = None 
        if self.corr_obj != None and isinstance(self.corr_obj[1], Wind):
            ret = WAVE('winded')
            ret._length = self._length
            ret.corr_obj = [self, self.corr_obj[1] * wind]
        else:
            ret = WAVE('winded')
            ret._length = self._length
            ret.corr_obj = [self, wind]
        return ret

    def __mul__(self, obj):
        ret = None
        if isinstance(obj, WAVE):
            # 波形相乘短的补0
            #   如果两个都是 'data' 类型直接计算, 也许能减少文件体积
            #   否则, 创建 'mul' 类型
            if self.type == 'data' and obj.type == 'data':
                new_wave_data = [0] * max(len(self.data), len(obj.data))
                sz = min(len(self.data), len(obj.data))
                for i in range(sz):
                    new_wave_data[i] = self.data[i] * obj.data[i]
                ret = WAVE(new_wave_data)
            else:
                ret = WAVE('mul')
                ret._length = max(self._length, obj._length)
                ret.corr_obj = [self, obj]
        elif isinstance(obj, float) or isinstance(obj, int):
            # 波形数乘, 使中间文件保持一致, 不进行优化
            ret = WAVE('mul')
            ret.corr_obj = [self, float(obj)]
        elif isinstance(obj, Wind):
            ret = self._gen_wind_wave(obj)
        else:
            # 其他类型认为错误
            raise TypeError("can\'t multipy WAVE by {}".format(type(obj)))
        return ret
    
    def __rmul__(self, obj):
        """ 左乘 """
        ret = None
        if isinstance(obj, float) or isinstance(obj, int):
            ret = self.__mul__(obj)
        elif isinstance(obj, Wind):
            ret = self._gen_wind_wave(obj)
        else:
            raise TypeError("can\'t multipy WAVE by {}".format(type(obj)))
        return ret

    def __add__(self, obj):
        ret = None
        if isinstance(obj, WAVE):
            if self.type == 'data' and obj.type == 'data':
                if self._length < obj._length:
                    _long_data = deepcopy(obj.data)
                    _short_data = obj.data
                else:
                    _long_data = deepcopy(self.data)
                    _short_data = obj.data
                for i in range(leng(_short_data)):
                    _long_data[i] += _short_data[i]
                ret = WAVE(_long_data)
            else:
                ret = WAVE('add')
                ret.corr_obj = [self, obj]
                ret._length = max(self._length, obj._length)
        elif isinstance(obj, Marker):
            self.marker = obj.params
            ret = self
        else:
            raise TypeError('can\'t add {} to a WAVE'.format(type(obj)))
        return ret

    def __repr__(self):
        """
        格式化字符串 
        """
        ret = 'W{},{},{}'.format(self.id, self.type, self._length)

        if self.type == 'mul':
            if isinstance(self.corr_obj[1], float):
                ret += ',W{},{}'.format(self.corr_obj[0].id, self.corr_obj[1])
            else:
                ret += ',W{},W{}'.format(self.corr_obj[0].id, self.corr_obj[1].id)
        elif self.type == 'add':
            ret += ',W{},W{}'.format(self.corr_obj[0].id, self.corr_obj[1].id)
        elif self.type == 'combine':
            for it in self.params:
                ret += ',W{}'.format(it.id)
        elif self.type == 'shift':
            ret += ',W{},{}'.format(self.corr_obj[0].id, self.corr_obj[1])
        elif self.type == 'file':
            ret += ',{}'.format(self.filepath)
        elif self.type == 'cache':
            ret += ',{}'.format(self.filepath)
        elif self.type == 'data':
            ret += ',{}'.format(str(self.data)[1:-1].replace(' ', ''))
        elif self.type == 'delay':
            pass
        elif self.type == 'winded':
            ret += ',W{},M{}'.format(self.corr_obj[0].id, self.corr_obj[1].id)
        else:
            ret += ',{}'.format(str(self.params)[1:-1].replace(' ', ''))
        
        if self.marker == None: 
            ret += '|{},{}'.format(self._length, 1)
        
        else: 
            if self.marker[0] > self._length:
                self.marker[0] = self._length  
            if self.marker[2] + self.marker[0]  > self._length:
                self.marker[2] = self._length - self.marker[0]  
            if self.marker[1] != 0:
                self.marker[1] = 1 
            if self.marker[3] != 0:
                self.marker[3] = 1 
            ret += '|{}'.format(str(self.marker)[1:-1].replace(' ', ''))
        
        return ret

    def search_corr_obj(self):
        wave_dict, wind_dict = {}, {}
        stack = [self]
        if self.type == 'combine':
            for it in self.params:
                stack.append(it)
        
        while len(stack) != 0:
            curr_w = stack.pop()
            wave_dict[curr_w.id] = curr_w
            if curr_w.corr_obj != None:
                stack.append(curr_w.corr_obj[0])
                if isinstance(curr_w.corr_obj[1], WAVE):
                    stack.append(curr_w.corr_obj[1])
                elif isinstance(curr_w.corr_obj[1], Wind):
                    wind_dict[curr_w.corr_obj[1].id] = curr_w.corr_obj[1]
        return wave_dict, wind_dict
            

class Marker:
    """
    Marker 信号
    """
    def __init__(self, *argv):
        if len(argv) == 4 or len(argv) == 2:
            self.params = list(argv)
        else:
            raise ValueError("Marker parameters error")

    def __add__(self, wave):
        if isinstance(wave, WAVE):
            wave.marker = self.params
            return wave
        else:
            raise ValueError("Marker should bind with WAVE")

    def __radd__(self, wave):
        self.__add__(wave)

# def Delay(cycle):
#     if cycle <=0:
#         raise ValueError('Delay() parameters error')
#     else:
#         ret = WAVE('delay')
#         ret.set_length(cycle * 4)
#         return ret
Delay = WAVE('delay')
Delay.set_length(4)

def Sin(freq, Amp=None, Len=None, Phase=0, Offset=0, Loop=1):
    global GAmp
    if Len != None:
        if Len <= 0:
            Len = -1
    if Amp == None:
        Amp = GAmp
    if Amp > 500:
        Amp = 500
    if Len == None:
        Len = 1000 * SR / freq
    Len = int(Len)
    ret = WAVE('sin')
    ret.params = [Len, freq, Amp, Phase, Offset, Loop]
    ret.set_length(Len * Loop)
    return ret


def Gauss(var, Amp=None, Len=None, Offset=0, Loop=1):
    global GAmp
    if Len != None:
        if Len <= 0:
            Len = -1
    if Amp is None:
        Amp = GAmp
    if Amp > 500:
        Amp = 500

    if Len is None:
        Len = 5 * var # sqrt(ln(32767 * A / 500))
    Len = int(Len)
    ret = WAVE('gauss')
    ret.params = [Len, var, Amp, Offset, Loop]
    ret.set_length(Len * Loop)
    return ret


def Square(Len, Mode=UP, Amp=None, Offset=0, Loop=1):
    global GAmp
    if Len != None:
        if Len <= 0:
            Len = -1
    if Amp == None:
        Amp = GAmp
    if Amp > 500:
        Amp = 500
    if Mode != UP and Mode != DOWN:
        raise ValueError('Square() Mode error')
    ret = WAVE('square')
    ret.params = [Len, Amp, Mode, Offset, Loop]
    ret.set_length(Len * Loop)
    return ret


def Triangle(Len, Mode, Amp=None, Offset=0, Loop=1):
    global GAmp
    if Len != None:
        if Len <= 0:
            Len = -1
    if Amp == None:
        Amp = GAmp
    if Amp > 500:
        Amp = 500
    if Mode != UP and Mode != DOWN:
        raise ValueError('Triangel() Mode parameters error')
    ret = WAVE('triangle')
    ret.params = [Len, Amp, Mode, Offset, Loop]
    ret.set_length(Len * Loop)
    return ret


def Combine(*argv):
    ret = WAVE('combine')
    ret.params = []
    for it in argv:
        if isinstance(it, WAVE):
            ret.params.append(it)
            ret.set_length(ret.get_length() + it.get_length())
        else:
            raise TypeError('Combine: not a WAVE')
    return ret


def Shift(wave, offset):
    ret = WAVE('shift')
    if isinstance(wave, WAVE) and isinstance(offset, int) and offset >= 0:
        ret.corr_obj = [wave, offset]
        ret.set_length(wave.get_length() + offset)
    else:
        raise ValueError('Shift() offset shoulde a <int>')
    return ret

#-----------------------------------------------------------------------------
"""
实现序列，子序列和 ADVS

子序列表示
    S0=w1,10,w2,20|               # 例1，单个子序列
    S1=w1,12;w3,8|w3,2|w4,5|      # 例2
    S2=w3,10|w1,3;w2,3;w52|w7,1|  # 例3
序列表示
    OUT1=S1,1
    OUT2=S1,1;S2,3
"""

class SEQ:
    sid = 0
    def __init__(self, obj=None):
        self.id = SEQ.sid
        SEQ.sid += 1
        self.subseq_list = []
        if obj is None:
            pass
        else:
            errmsg = SEQ._seq_list_check(obj)
            if errmsg == '':
                self._ext_subseq(obj)
            else:
                raise ValueError(errmsg)
    
    @staticmethod
    def _seq_list_check(wll, nest=0):
        errmsg  = ''
        if nest >= 2:
            errmsg = 'too much nest'
        elif isinstance(wll, list):
            # 检查类型是否合法
            for it in wll:
                if isinstance(it, list):
                    errmsg = SEQ._seq_list_check(it, nest+1)
                    if errmsg != '':
                        break
                elif isinstance(it, tuple) and isinstance(it[0], WAVE) and isinstance(it[1], int):
                    if it[1] <= 0:
                        errmsg = 'WAVE loop={} error'.format(it[1])
                        break
                else:
                    errmsg = 'WAVE loop type error {}'.format(type(it))
                    break
        else:
            errmsg = 'Unsupport SEQ type'
        return errmsg
    
    def _ext_subseq(self, wll):
        for it in wll:
            if isinstance(it, list):
                self.subseq_list.append(it)
            else:
                self.subseq_list.append([it])

    def __add__(self, obj):
        errmsg = seq_list_check(obj)
        if errmsg == '':
            self._ext_subseq(obj)
        else:
            raise ValueError(errmsg)
        return self
    
    def __iadd__(self, obj):
        errmsg = seq_list_check(obj)
        if errmsg == '':
            self._ext_subseq(obj)
        else:
            raise ValueError(errmsg)
        return self

    def __call__(self, loop):
        return ADVS(self, loop)

    def __repr__(self):
        desc = 'S{}='.format(self.id)
        for subseq in self.subseq_list:
            _tmp = ''
            for wl in subseq:
                _tmp += 'W{},{};'.format(wl[0].id, wl[1])
            desc += _tmp[0:-1] + '|'
        return desc

    def detect_wave(self):
        """
        找出所有的 WAVE 和 Wind
        """
        wave_dict = {}  # id:obj
        wind_dict = {}  # id:obj
        seq_dict = {self.id: self}
        for subseq in self.subseq_list:
            for wave, loop in subseq:
                wd, md = wave.search_corr_obj()
                for wid in wd:
                    wave_dict[wid] = wd[wid]
                for mid in md:
                    wind_dict[mid] = md[mid]
        return wave_dict, wind_dict, seq_dict
                

class ADVS:
    advsId = 0
    def __init__(self, obj=None, repeat=1):
        self.id = ADVS.advsId
        ADVS.advsId += 1
        if obj is None:
            self.seqloop_list = []
        elif isinstance(obj, SEQ) and isinstance(repeat, int) and repeat > 0:
            self.seqloop_list = [(obj, repeat)]
        elif isinstance(obj, ADVS):
            self.seqloop_list = deepcopy(obj.seqloop_list)
        else:
            raise TypeErroe('can\’t construct a ADVS by {}'.format(type(obj)))
        
    def __add__(self, nadvs):
        ret = None
        if isinstance(nadvs, ADVS):
            ret = ADVS()
            ret.seqloop_list = self.seqloop_list + nadvs.seqloop_list
        else:
            raise TypeError('can\'t add {} object to ADVS'.format(type(nadvs)))
        return ret

    def __iadd__(self, nadvs):
        if isinstance(nadvs, ADVS):
            self.seqloop_list += nadvs.seqloop_list
        else:
            raise TypeError('can\'t add {} object to ADVS'.format(type(nadvs)))
        return self
    
    def __repr__(self):
        desc = ''
        for seq, loop in self.seqloop_list:
            desc += 'S{},{};'.format(seq.id, loop)
        return desc[0:-1]
    
    def detect_wave(self):
        wave_dict = {}
        wind_dict = {}
        seq_dict = {}
        for seq, loop in self.seqloop_list:
            _wd, _md, _sd = seq.detect_wave()
            for wid in _wd:
                wave_dict[wid] = _wd[wid]
            for mid in _md:
                wind_dict[mid] = _md[mid]
            seq_dict[seq.id] = seq
        return wave_dict, wind_dict, seq_dict

#-----------------------------------------------------------------------------
"""
辅助函数
"""
def save_in_file(outs):
    channel_num = len(outs)

    for i in range(channel_num):
        if not (outs[i] == None or isinstance(outs[i], (SEQ, ADVS))):
            raise TypeError('OUT{} type error'.format(i))
    
    out_txt = []
    waves, winds, seqs = {}, {}, {}
    for i in range(channel_num):
        if isinstance(outs[i], SEQ):
            out_txt.append('\nOUT{}=S{},1'.format(i+1, outs[i].id))
        elif isinstance(outs[i], ADVS):
            out_txt.append('\nOUT{}={}'.format(i+1, outs[i]))
        if outs[i] != None:
            _wd, _md, _sd = outs[i].detect_wave()
            for wi in _wd:
                waves[wi] = _wd[wi]
            for mi in _md:
                winds[mi] = _md[mi]
            for si in _sd:
                seqs[si] = _sd[si]
    
    full_txt = 'R={}'.format(SR)
    for mid in sorted(winds):
        full_txt += '\n{}'.format(winds[mid])
    for wid in sorted(waves):
        full_txt += '\n{}'.format(waves[wid])
    for sid in sorted(seqs):
        full_txt += '\n{}'.format(seqs[sid])
    for l in out_txt:
        full_txt += l
    
    print(full_txt)

    global _OUT_FILE
    if _OUT_FILE == '':
        _OUT_FILE = 'awg-temp-file'
    tdir = os.environ['TEMP']
    with open(os.path.join(tdir, _OUT_FILE), 'w') as f:
        f.write(full_txt)


def set_out_filename(filename):
    global _OUT_FILE
    _OUT_FILE = filename
