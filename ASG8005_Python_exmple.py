import sys
from ASG8005_PythonSDK import *
from ctypes import *
import threading
import time

m_CountCount = 1

@CFUNCTYPE(None, c_int, c_char_p)  # 设置字符串回调函数，要返回固件信息和提示
def status_callback(type, c_char_buff):
    print(type)
    print(c_char_buff)
    return

@CFUNCTYPE(None, c_int, c_int, POINTER(c_uint32))  # 设置count回调函数，dll有数据时调用python处理
def count_callback(type, len, c_int_buff):
    datList = []
    for i in range(len):
        datList.append(c_int_buff[i])
    typestr:str
    if type == 0:
        if m_CountCount != len:
            print("数据错误")
        typestr = 'count计数：'
    elif type == 3:
        typestr = '连续计数 ：'
    print(typestr,"datList :",datList)
    return

#实例化asg对象
asg = ASG8005()

#设置回调函数
asg.set_callback(status_callback)
asg.set_callback_count(count_callback)

#连接
print("asg.connect() " , asg.connect())


#ASG
asg_data1=[
    [10,10],
    [10,10,10,10],
    [10,10,10,10,10,10,10,10],
    [0,10,10,10,10,10,10,10],
    [10,10,10,10,10,10,10,0],
    [0,10],
    [10,0],
    [0,0]
]
length1=[len(seq) for seq in asg_data1]

#input("press Enter to download_ASG_pulse_data")
print("asg.download_ASG_pulse_data: ",asg.download_ASG_pulse_data(asg_data1, length1))

#COUNT
count_data=[20,20,20,20,20,20,20,10000]
length_count=len(count_data)
m_CountCount = length_count/2

#下载count数据
print("asg.ASG_counter_download : ",asg.ASG_counter_download(count_data,length_count))



#配置循环次数
counter_repeat = 0# 1x2 = 4
print("asg.ASG_set_counter_repeat ：",asg.ASG_set_counter_repeat(counter_repeat))

#配置连续采集时间间隔
count_timeStep = 50000000 # 50000000 x 20 = 1000000000ns = 1s
print("asg.ASG_countTimeStep() ：",asg.ASG_countTimeStep(count_timeStep))

#开启连续计数功能
print("asg.ASG_isCountContinu：",asg.ASG_isCountContinu(1))

#配置asg和count功能 有两个参数第一个是开启count功能，第二个是开启asg功能，第二个默认asg全开
print("asg.ASG_countConfig：",asg.ASG_countConfig(1))

#开始播放
#input("press Enter to start")
print("asg.start(): ",asg.start())


#停止播放
input("press Enter to stop")
print("asg.stop(): ",asg.stop())

#关闭连接
print("asg.close_device(): ",asg.close_device())


'''
        调用顺序说明

一、设备：
1.连接

二、公共设置：
1.设置字符串回调函数，要返回固件信息和提示
2.设置count回调函数，dll有数据时调用python处理

三、ASG：
1.下载asg波形

四、count：
1.下载count数据
2.配置循环次数
3.配置连续采集时间间隔
4.开启连续计数功能

五、公共函数：
1.开始播放
2.停止播放
3.关闭连接
'''





























