# 导入可直接访问的类
from .awglib import WAVE, SQN, SEQ, ADVS, Marker, Wind

# 导入可直接访问的全局变量
#from .awglib import WorkDir, SampleRate
from .awglib import WD, SR
from .awglib import GAmp, UP, DOWN
from .awglib import MODE_T, MODE_C, T, C
from .awglib import PI

# 导入可直接访问的函数
from .awglib import Sin, SinC, Gauss, Square_p, Square, Triangle_p, Triangle, Delay
from .awglib import Combine, Shift
from .awglib import Sweep

from .preprocessor import preprocessor