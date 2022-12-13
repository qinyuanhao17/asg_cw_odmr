import ctypes
lib = ctypes.CDLL('D:\ODMRequipment\dll_versatile\env_bit64\smncsftmt.dll')

# c programming language 宏
DEV_ID_0 = ctypes.c_int(0)
FTMT_START_FREQ_DIV_1 = ctypes.c_int(1)
FTMT_START_FREQ_DIV_2 = ctypes.c_int(2)
FTMT_START_FREQ_DIV_3 = ctypes.c_int(3)
FTMT_START_FREQ_DIV_4 = ctypes.c_int(4)


GetDevType = lib.GetDevType

GetDevType.argtypes = [ctypes.c_int]
GetDevType.restype = ctypes.c_int
rtn = hex(GetDevType(DEV_ID_0))
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