import ctypes
import os
import platform
lib = ctypes.CDLL(".\dll_ft1040\dll_x64\smncsftmt.dll")

# c programming language 宏
DEV_ID_0 = ctypes.c_int(0)
FTMT_START_FREQ_DIV_1 = ctypes.c_int(1)
FTMT_START_FREQ_DIV_2 = ctypes.c_int(2)
FTMT_START_FREQ_DIV_3 = ctypes.c_int(3)
FTMT_START_FREQ_DIV_4 = ctypes.c_int(4)
FTMT_TTTR_END_MODE_TIME = ctypes.c_int(0) 
FTMT_TASK_RUN_MODE_T3 = ctypes.c_int(0x03)  
FilePath = ctypes.c_char_p(b"D:\ODMRequipment\File")
# dll_path = ""
# wd = os.path.abspath(os.path.dirname(__file__))
# arch = platform.architecture()[0]
# if arch == '64bit':
#     dll_path = os.path.join(wd, 'dll_ft1040\dll_x64\smncsftmt.dll')
    
#     print("64 bit smncsftmt.dll is dynamically loaded")
# else:
#     dll_path = os.path.join(wd, 'dll_ft1040\dll_x86\smncsftmt.dll')
#     print("32 bit smncsftmt.dll is dynamically loaded")
# print(dll_path)
# if os.path.isfile(dll_path):
#     lib = ctypes.CDLL(dll_path)
# GetDevType = lib.GetDevType
# GetDevType.argtypes = [ctypes.c_int, ctypes.c_char_p]
# GetDevType.restype = ctypes.c_int

# print(GetDevType(ctypes.c_int(0), ctypes.c_char_p(b"my dev")))
SetTTTREndMode = lib.SetTTTREndMode
SetTTTREndMode.argtypes = [ctypes.c_int]
SetTTTREndMode.restype = ctypes.c_int
rtn = SetTTTREndMode(FTMT_TTTR_END_MODE_TIME)
print(rtn)


GetDevType = lib.GetDevType

GetDevType.argtypes = [ctypes.c_int, ctypes.c_char_p]
GetDevType.restype = ctypes.c_int
rtn = hex(GetDevType(DEV_ID_0,ctypes.c_char_p(b"my dev")))
print(rtn)

# GetSerialNumber = lib.GetSerialNumber
# # GetSerialNumber.restype = ctypes.c_uint32

# print(type(GetSerialNumber(0)))
# print(lib.GetPartNumber(0))

SetStartFreqDiv = lib.SetStartFreqDiv
SetStartFreqDiv.argtypes = [ctypes.c_int, ctypes.c_int]
SetStartFreqDiv.restype = ctypes.c_int
rtn = SetStartFreqDiv(DEV_ID_0,FTMT_START_FREQ_DIV_1)
print(rtn)

GetFilePath = lib.GetFilePath
GetFilePath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
GetFilePath.restype = ctypes.c_int
rtn = GetFilePath(DEV_ID_0, FTMT_TASK_RUN_MODE_T3, FilePath)
print(rtn)