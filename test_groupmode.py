import sys
import platform
import time
import struct
from awg4100 import AwgDevice



local_ip = "192.168.8.5"
out_ch = 2

#定义波形代码
wave_code = """                                                      
GAmp = 200

w1 = Sin(Freq = 200, Amp = 200, Len = 3600)
w2 = Sin(Freq = 10, Amp = 10, Len = 3600)
w3 = Square_p(200, Amp=200, Loop=2, Dutycycle=0.2)
w4 = Triangle_p(200, Mode=DOWN, Amp=200, Loop=2)
s1 = SQN([w1(1)]) 
s2 = SQN([w2(1)]) 
s3 = SQN([w3(1)]) 
s4 = SQN([w4(1)]) 
OUT1 = s1 
OUT2 = s2 
OUT3 = s3 
OUT4 = s4 

"""

dev = AwgDevice()

result = dev.init_network(local_ip)
if result == 0:
    print("Init network failed.")
    sys.exit()

dev_info = dev.find_device()
dev_num = len(dev_info)
if dev_num == 0:
    print("Cannot found device")
    sys.exit()

for idx in range(dev_num):
    print("[{}] IP={}, MAC={}, Name={}".format(idx, \
                                               dev_info[idx][0], dev_info[idx][1], dev_info[idx][2]))

trgt = int(input("choice: "))

ip = dev_info[trgt][0]
mac = dev_info[trgt][1]

result = dev.connect(ip, mac)
if result != 1:
    print("Connect failed.")
    sys.exit()

def check_ret(rtn, msg=None):
    if rtn == 0:
        print(msg)
        sys.exit()

rtn, msg = dev.system_init()
check_ret(rtn, "System Reset failed.")

rtn, msg = dev.channel_mode(1)  # 组合模式
check_ret(rtn, "set mode failed: {}".format(msg))

rtn, msg = dev.awg_cast_mode(0)  # 连续模式
check_ret(rtn, "set awg cast mode failed: {}".format(msg))

rtn, msg = dev.clock_mode(0)  
check_ret(rtn, "set clock failed: {}".format(msg))

rtn, msg = dev.channel_switch(1, 1) # OUT1 AWG
check_ret(rtn, "set out channel 1 failed: {}".format(msg))

rtn, msg = dev.channel_switch(2, 1) # OUT2 AWG
check_ret(rtn, "set out channel 2  failed: {}".format(msg))

rtn, msg = dev.channel_switch(3, 1) # OUT3 AWG
check_ret(rtn, "set out channel 3  failed: {}".format(msg))

rtn, msg = dev.channel_switch(4, 1) # OUT4 AWG
check_ret(rtn, "set out channel 4  failed: {}".format(msg))

result = dev.load_wave_data(1, wave_code)
print(result)
if result == 0:
    print("wave download failed: {}".format(result))
    sys.exit()
result = dev.load_wave_data(2, wave_code)
if result == 0:
    print("wave download failed: {}".format(result))
    sys.exit()
result = dev.load_wave_data(3, wave_code)
if result == 0:
    print("wave download failed: {}".format(result))
    sys.exit()
result = dev.load_wave_data(4, wave_code)
if result == 0:
    print("wave download failed: {}".format(result))
    sys.exit()

#infinite loop
rtn, info = dev.awg_cast_number(0) 
check_ret(rtn, "set awg cast number failed: {}".format(info))

print(dev.awg_PlayStatus(1))
time.sleep(5)

rtn, info = dev.awg_broadcast(5, 1)
check_ret(rtn, "start failed: {}".format(info))
time.sleep(5)
print(dev.awg_PlayStatus(1))

input("enter any to stop")

rtn, info = dev.awg_broadcast(5, 0)
check_ret(rtn, "stop failed: {}".format(info))

result = dev.close_device()
if not result:
    sys.exit()