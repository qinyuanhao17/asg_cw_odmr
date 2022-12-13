import os
import sys
import time
from copy import deepcopy
import traceback
from struct import *
import py_compile

MODE_T = 0x00 # tirgger mode
MODE_C = 0x01 # continue mode
T = MODE_T
C = MODE_C
_MODE_CLASS = [MODE_T, MODE_C]
_WAVE_ALLOWED_TYPE = ['sin', 'sinc', 'gauss', 'square', 'triangle', 'mul', 'add', 'zero']
_OUT_DATA_ = False
_OUT_SEG_ = False

WD = ''
SR = 1.2

OUT_PATH = os.path.dirname(__file__)
# global OUT_FILE
OUT_FILE = ""

def log_and_exit(msg):
    if OUT_FILE is None or OUT_FILE == '':
        file = 'awg-wave.log'
    else:
        file = OUT_FILE
    msg = "!" + msg
    tdir = os.environ['TEMP']
    with open(os.path.join(tdir, file), 'w') as f:
        f.writelines(msg)
        f.close()
        print(msg)
    sys.exit(0)

def _Encode(val):
    if val < -250:
        cd = 0
    elif val > 250:
        cd = 0xffff
    else:
        cd = (val / 250 * 32768 + 32768)
    return int(cd)

def _Decode(cd):
    val = (cd / 32768. - 1.) * 250.
    return val


def str_time():
    return str(int(time.time()*1000000))

#CACHE_NUMBER = 0
def cache_wave_file(data, mode='volt'):
    # global CACHE_NUMBER
    tdir = os.environ['TEMP']
    filepath = os.path.join(tdir, 'wave-cache-{}'.format(str_time()))
    # CACHE_NUMBER += 1
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

class WAVE:
    wid = 0
    def __init__(self, wave, mode='volt'):
        self.id = WAVE.wid
        WAVE.wid += 1
        self.type = ''
        self.params = []  # params: [f, A, T, ph0, bias]
        self.data = None
        self.corr_wave = []
        self.data_mode = ''
        self.filepath = None
        self.amplitude = 0
        self.length = 0

        if isinstance(wave, list) and isinstance(wave[0], (int, float)):
            self.length = len(wave)
            if len(wave) < 100:
                self.type = 'data'
                self.data_mode = mode
                if mode == 'volt':
                    self.data = wave
                elif mode == 'code':
                    self.data = [_Decode(v) for v in wave]
                else:
                    log_and_exit("Wrong list wave data")
            else:
                self.type = 'cache'
                self.length = len(wave)
                self.filepath = cache_wave_file(wave, mode)
        elif isinstance(wave, str):
            if len(wave) > 5 and wave[-5:] == '.wave':
                right_path = False
                if os.path.isfile(wave):
                    self.filepath = wave
                    right_path = True
                elif os.path.isfile(os.path.join(WD, wave)):
                    self.filepath = os.path.join(WD, wave)
                    right_path = True

                if right_path:
                    self.type = 'file'
                    file_info = os.stat(self.filepath)
                    file_data_sz = (file_info.st_size - 16)
                    if file_data_sz <= 0:
                        log_and_exit('{} is not a .wave file.'.format(wave))
                    with open(self.filepath, 'rb') as f:
                        header = unpack('4s4sI', f.read(12))
                        if header[0] != b'AWGw':
                            log_and_exit('file {} is not a .wave file.'.format(wave))
                        self.length = header[2]
                        if header[1] == b'\x00u16':
                            if self.length != (file_data_sz // 2):
                                log_and_exit('file {} data length error'.format(wave))
                        elif header[1] == b'\x00f32':
                            if self.length != (file_data_sz // 4):
                                log_and_exit('file {} data length error'.format(wave))
                        elif header[1] == b'\x00f64':
                            if self.length != (file_data_sz // 8):
                                log_and_exit('file {} data length error'.format(wave))
                        else:
                            log_and_exit('file {} unknown data format'.format(wave))
                else:
                    log_and_exit('file not found')
            elif wave in _WAVE_ALLOWED_TYPE:
                self.type = wave
            else:
                log_and_exit("unknow WAVE type name")
        elif isinstance(wave, WAVE):
            self.type = deepcopy(wave.type)
            self.params = deepcopy(wave.params)
            self.data = deepcopy(wave.data)
            self.corr_wave = deepcopy(wave.corr_wave)
            self.data_mode = deepcopy(wave.data_mode)
            self.filepath = deepcopy(wave.filepath)
            self.amplitude = wave.amplitude
            self.length = wave.length
        else:
            log_and_exit("unknow WAVE type")

    def __call__(self, loop, mode):
        return SubSegment(self, loop, mode)

    def __mul__(self, obj):
        if isinstance(obj, WAVE) and self.length == obj.length:
            if self.type == 'data' and obj.type == 'data':
                new_wave_data = []
                for i in range(self.length):
                    new_wave_data.append(self.data[i] * obj.data[i])
                return WAVE(new_wave_data)
            else:
                ret = WAVE('mul')
                ret.length = self.length
                ret.corr_wave = [self, obj]
                return ret
        elif isinstance(obj, float) or isinstance(obj, int):
            if self.type in ['sin', 'sinc', 'gauss', 'triangle', 'square']:
                ret = WAVE(self)
                ret.params[1] *= float(obj)
                return ret
            else:
                ret = WAVE('mul')
                ret.corr_wave = [self, float(obj)]
                return ret
        else:
            log_and_exit("mul error")
            return

    def __rmul__(self, gain):
        # gain must not WAVE
        ret = None
        if isinstance(gain, float) or isinstance(gain, int):
            ret = self.__mul__(gain)
        else:
            log_and_exit("unsport type")
        return ret

    def __add__(self, obj):
        ret = None
        if isinstance(obj, WAVE) and self.length == obj.length:
            if self.type == 'data' and obj.type == 'data':
                new_wave_data = []
                for i in range(self.length):
                    new_wave_data.append(self.data[i] + obj.data[i])
                ret = WAVE(new_wave_data)
            else:
                ret = WAVE('add')
                ret.corr_wave = [self, obj]
                ret.length = self.length
        else:
            log_and_exit("add error")
        return ret

    def __repr__(self):
        """sin [f, A, ph0, bias]
        [f, A, t0, bias]
        [var, A, b]
        """
        ret = None
        if self.length > 536_870_912:
            log_and_exit("WAVE to long")

        if self.type in ['sin', 'sinc', 'gauss', 'square', 'triangle']:
            params_str = ''
            for p in self.params:
                params_str += ',' + str(p)
            ret = 'W{},{},{}{}'.format(self.id, self.type, self.length, params_str)
        elif self.type == 'mul':
            if isinstance(self.corr_wave[1], float):
                ret = 'W{},mul,{},W{},{}'.format(self.id, self.length,\
                    self.corr_wave[0].id, self.corr_wave[1])
            else:
                ret = 'W{},mul,{},W{},W{}'.format(self.id, self.length,\
                    self.corr_wave[0].id, self.corr_wave[1].id)
        elif self.type == 'add':
            ret = 'W{},add,{},W{},W{}'.format(self.id, self.length,\
                self.corr_wave[0].id, self.corr_wave[1].id)
        elif self.type == 'file':
            ret = 'W{},file,{},{}'.format(self.id, self.length, self.filepath)
        elif self.type == 'cache':
            ret = 'W{},cache,{},{}'.format(self.id, self.length, self.filepath)
        elif self.type == 'data':
            ret = 'W{},data,{},{}'.format(self.id, len(self.data), str(self.data)[1:-1])
        elif self.type == 'zero':
            ret = 'W{},zero,{}'.format(self.id, self.length)
        else:
            log_and_exit('unknow WAVE <{}>'.format(self.type))
        return ret


class SubSegment:
    def __init__(self, obj, loop=1, mode=C):
        if isinstance(obj, WAVE) and isinstance(loop, int) and mode in _MODE_CLASS:
            if loop > 0:
                self.w = obj
                self.l = loop
                self.m = mode
            else:
                log_and_exit('Error: WAVE loop is 0')
        else:
            log_and_exit('Error: paramer type error, when WAVE.__call__')


class Segment:
    sgId = 0
    def __init__(self, sslist, dtime):
        self.id = Segment.sgId
        Segment.sgId += 1
        self.wss_list = [] # [(wave, loop), ...]
        self.length = 0
        self.delay_time = dtime
        if isinstance(sslist, list) and isinstance(sslist[0], SubSegment):
            try:
                for it in sslist:
                    self.wss_list.append((it.w, it.l))
                    self.length += it.w.length * it.l
            except TypeError:
                log_and_exit("Type error! 0x1001")
        else:
            log_and_exit("Error: Type error! 0x1000")

    def __repr__(self):
        ret = ''
        for w, l in self.wss_list:
            ret += "W{},{}; ".format(w.id, l)
        ret = ret[0:-2]
        return ret


class SEQ:
    sid = 0
    def __init__(self, obj=None):
        self.id = SEQ.sid
        SEQ.sid += 1
        self.seg_list = []
        self.seg_length_list = []
        if obj is None:
            pass
        elif isinstance(obj, list):
            self._appseg(obj)
        else:
            raise Exception('Error: wrong type when construct a SEQ Object')

    def _appseg(self, obj):
        if isinstance(obj, list):
            seg = None
            for sseg in obj:
                if isinstance(sseg, SubSegment):
                    if sseg.m == T:
                        if seg is not None:
                            self.seg_list.append(Segment(seg, 28))
                        seg = []
                        seg.append(sseg)
                    else:
                        seg.append(sseg)
                else:
                    raise Exception('Error: wrong type {} it should a WAVE'.format(type(sseg)))
            self.seg_list.append(Segment(seg, 28))
        else:
            log_and_exit('Error: paramers is not enough')

    def __add__(self, obj):
        ret = None
        if isinstance(obj, list):
            if obj[0].m != T:
                log_and_exit('Segment should start with MODE_T')
            ret = SEQ()
            ret.seg_list = deepcopy(self.seg_list)
            ret._appseg(obj)
        elif isinstance(obj, SEQ):
            ret = SEQ()
            ret.seg_list = self.seg_list + obj.seg_list
        else:
            log_and_exit('Object is not SEQ or list')
        return ret

    def __iadd__(self, obj):
        if isinstance(obj, list):
            if obj[0].m != T:
                log_and_exit('Segment should start with MODE_T')
            self._appseg(obj)
        elif isinstance(obj, SEQ):
            self.seg_list += obj.seg_list
        else:
            log_and_exit('Object is not SEQ or list')
        return self

    def __call__(self, repeat):
        return ADVS(self, repeat)

    def __repr__(self):
        """
        describation of SEG by Segment
        """
        desc = ''
        for seg in self.seg_list:
            desc += "S{},{}; ".format(seg.id, 1)
        desc = desc[0:-2]
        return desc

    def detect(self):
        wave_d = {}
        seg_d = {}
        seg_ll = []
        for seg in self.seg_list:
            for wave_pack in seg.wss_list:
                stack = [wave_pack[0]]
                while len(stack) != 0:
                    curr_w = stack.pop()
                    wave_d[curr_w.id] = curr_w
                    if len(curr_w.corr_wave) != 0:
                        stack.append(curr_w.corr_wave[0])
                        if isinstance(curr_w.corr_wave[1], WAVE):
                            stack.append(curr_w.corr_wave[1])
            seg_d[seg.id] = seg
            seg_ll.append(seg.length + seg.delay_time)
        return wave_d, seg_d, seg_ll


class ADVS:
    aid = 0
    def __init__(self, obj=None, repeat=1):
        self.id = ADVS.aid
        ADVS.aid += 1
        if obj is None:
            self.seq_list = []
        elif isinstance(obj, SEQ) and isinstance(repeat, int) and repeat > 0:
            self.seq_list = [(obj, repeat)]
        elif isinstance(obj, ADVS):
            self.seq_list = deepcopy(obj.seq_list)
        else:
            log_and_exit('Error: wrong type, when construct a ADVS object.')

    def __add__(self, nadvs):
        ret = None
        if isinstance(nadvs, ADVS):
            ret = ADVS()
            ret.seq_list = self.seq_list + nadvs.seq_list
        else:
            log_and_exit('Error: wrong type, when a ADVS add to')
        return ret

    def __iadd__(self, nadvs):
        if isinstance(nadvs, ADVS):
            self.seq_list += nadvs.seq_list
        else:
            log_and_exit('Error: wrong type, when a ADVS add to')
        return self

    def __repr__(self):
        desc = ''
        for sp in self.seq_list:
            s, l = sp
            if isinstance(s, SEQ):
                if len(s.seg_list) == 1:
                    desc += "S{},{}; ".format(s.seg_list[0].id, l)
                else:
                    desc += (str(s) + "; ") * l
            else:
                log_and_exit("ADVS Type error")
        desc = desc[0:-2]
        return desc

    def detect(self):
        """
        only detect wave and segment
        """
        wave_d = {}
        seg_d = {}
        seg_ll = []
        for seq in self.seq_list:
            _wd, _sd, _sll = seq[0].detect()
            for wid in _wd:
                wave_d[wid] = _wd[wid]
            for sid in _sd:
                seg_d[sid] = _sd[sid]
            seg_ll += _sll
        return wave_d, seg_d, seg_ll

GAmp = 300

def Sin(f, A=None, L=None, ph0=0, b=0):
    """
    f : 频率, MHz
    T : 持续时长，整数 ns
    """
    if A is None:
        A = GAmp

    if L is None or L <= 0:
        L = 1000 / f * SR
    L = int(L)

    ret = WAVE('sin')
    ret.params = [f, A, ph0, b]
    ret.length = L

    return ret


def SinC(f, A=None, L=None, ph0=0, b=0):
    if A is None:
        A = GAmp

    if L is None or L <= 0:
        L = 1000 / f * SR
    L = int(L)

    ret = WAVE('sinc')
    ret.params = [f, A, ph0, b]
    ret.length = L

    return ret


def Gauss(var, A=None, L=None, b=0):
    if A is None:
        A = GAmp

    if L is None:
        L = 5 * var # sqrt(ln(32767 * A / 500))
    L = int(L)

    ret = WAVE('gauss')
    ret.params = [var, A, b]
    ret.length = L

    return ret

UP = 0xA0
DOWN = 0xA1

def Square(period, mode=UP, A=None, N=1):
    if A is None:
        A = GAmp

    ret = WAVE('square')
    nL = int(period * SR)
    ret.params = [nL, A, N, mode]
    ret.length = nL * N

    return ret

def Triangle(period, mode=UP, A=None, N=1):
    if A is None:
        A = GAmp

    ret = WAVE('triangle')
    nL = int(period * SR)
    ret.params = [nL, A, N, mode]
    ret.length = nL * N

    return ret


def Zero(L):
    L = int(L)
    
    ret = WAVE("zero")
    ret.params = []
    ret.length = L

    return ret

def _save_in_file(out=None, filename=None):
    channel_num = len(out)

    for i in range(channel_num):
        if not (out[i] is None or isinstance(out[i], (SEQ, ADVS))):
            print(type(out[i]))
            log_and_exit('OUT{} type error'.format(i+1))
            return

    if filename is None:
        file = 'odmr-wave-data'
    else:
        file = filename

    out_txt = []
    wd, sd, sll = {}, {}, []
    for i in range(channel_num):
        if out[i] is not None:
            out_txt.append('OUT{}=[{}]\n'.format(i+1, str(out[i])))
            _wd, _sd, _sll = out[i].detect()
            for wid in _wd:
                wd[wid] = _wd[wid]
            for sid in _sd:
                sd[sid] = _sd[sid]

    txt_lines = ['R={}\n'.format(SR)]
    for wid in sorted(wd):
        txt_lines.append("{}\n".format(wd[wid]))
    for sid in sorted(sd):
        txt_lines.append("S{}=[{}]\n".format(sid, sd[sid]))
    for l in out_txt:
        txt_lines.append(l)

    for l in txt_lines:
        print(l, end='')

    tdir = os.environ['TEMP']
    with open(os.path.join(tdir, file), 'w') as f:
        f.writelines(txt_lines)
        f.close()


#=======================================
if __name__ == "__main__":
    # global OUT_FILE
    OUT1 = None
    OUT2 = None
    OUT3 = None
    OUT4 = None
    OUTs = [OUT1, OUT2, OUT3, OUT4]
    PI = 3.141592653589793
    
    try:
        if len(sys.argv) >= 3:
            OUT_FILE = sys.argv[2]
        else:
            OUT_FILE = "awg-outfile"
        
        if os.path.isfile(sys.argv[1]):
            with open(sys.argv[1], encoding='utf-8') as code_file:
                user_script = code_file.read()
        else:
            user_script = sys.argv[1].replace(';', '')

        user_code_exec = compile(user_script, '', 'exec')
        exec(user_code_exec)
        
        # _save_in_file([OUT1, OUT2, OUT3, OUT4], OUT_FILE)
        _save_in_file(OUTs, OUT_FILE)
    except Exception as err:
        err_msg = str(err)
        trcbk = traceback.format_exc().split('\n')
        for l in trcbk[3:]:
            err_msg += '\n!' + l
        log_and_exit(err_msg)
    # except SyntaxError as serr:
    #     log_and_exit(str(serr.lineno))
