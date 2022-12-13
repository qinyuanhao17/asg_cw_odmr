import ctypes
from ctypes import *

# lib = ctypes.cdll.LoadLibrary("C://Users//xmgd//Desktop//MT16//11_15_DLL_64//smncsftmt.dll")
lib = ctypes.cdll.LoadLibrary(r"D:\MT16\11_9_DLL\smncsftmt.dll")

# 初始化
dll_init = lib.InitDll
dll_init()

dll_usbconnect = lib.USBConnected
dll_usbconnect.argtypes = [c_int]
dll_usbconnect.restypes = c_int
print("USB连接测试：", dll_usbconnect(0))

# 设置数据采集时间
dll_setstatisticstime = lib.SetStatisticsTime
dll_setstatisticstime.argtypes = [c_int, c_float]
dll_setstatisticstime.restypes = c_int
# dll_setstatisticstime(6, 3.0)
print("设置数据采集时间：", dll_setstatisticstime(6, 1.0))

# 设置文件保存方式
dll_setfilemode = lib.SetFileMode
dll_setfilemode.argtypes = [c_int, c_int, c_int]
dll_setfilemode.restypes = c_int
# dll_setfilemode(6, 1, 1)
print("设置文件保存方式：", dll_setfilemode(6, 1, 1))

# 设置统计周期
dll_setittrinterval = lib.SetITTRInterval
dll_setittrinterval.argtypes = [c_int, c_int, c_int]
print("设置统计周期:", dll_setittrinterval(0, 0, 1000))

# 设置采集数据文件保存路径
dll_setfilepath = lib.SetFilePath
dll_setfilepath.argtypes = [c_int, c_int, POINTER(c_char)]
dll_setfilepath.restypes = c_int
path_char = (c_char*64)(*bytes("D:\MT16_PATH", "utf-8"))
print("设置采集数据文件保存路径:", dll_setfilepath(0, 6, path_char))

# 使能ITTR模式
dll_enableittr = lib.EnableITTR
dll_enableittr.argtypes = [c_int, c_int, c_int]
print("使能ITTR模式:", dll_enableittr(0, 0, 1))


#设置停止方式
dll_setittrendmode = lib.SetITTREndMode
dll_setittrendmode.argtypes = [c_int, c_int]
print("设置停止方式:", dll_setittrendmode(1, 100))

# 开始任务
dll_starttask = lib.StartTask
dll_starttask.argtypes = [c_int]
dll_starttask.restypes = c_int
# dll_starttask(6)
print("开始任务:", dll_starttask(6))
# # 判断任务是否执行完成
dll_istaskcompleted = lib.IsTaskCompleted
dll_istaskcompleted.restypes = c_int
while True:
    if  dll_istaskcompleted() == 0:
        break
# 反初始化
dll_uninitdll = lib.UnInitDll
# dll_uninitdll()
print("反初始化:", dll_uninitdll())

