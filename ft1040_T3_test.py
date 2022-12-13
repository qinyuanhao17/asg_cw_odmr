import ctypes
lib = ctypes.CDLL('D:\ODMRequipment\dll_versatile\env_bit64\smncsftmt.dll')

'''Define macro instruction'''
DEV_ID_0 = ctypes.c_int(0)                                     # Device ID
FTMT_TASK_RUN_MODE_T3 = ctypes.c_int(0x03)                     # T3 Mode
FilePath = ctypes.c_char_p(b"D:\ODMRequipment\File")           # File path
sTime = ctypes.c_float(10) # in second unit                    # Collecting time 
FTMT_START_FREQ_DIV_1 = ctypes.c_int(1)                        # Frequency division time
FTMT_FILE_SAVE_MODE_BIN = ctypes.c_int(1)                      # Binary file type
FTMT_FILE_SAVE_MODE_TEXT = ctypes.c_int(2)                     # Text file type
FTMT_FILE_SERIES_MODE_EACH = ctypes.c_int(0)                   # T1 Mode parameters(useless here)
FTMT_TTTR_END_MODE_TIME = ctypes.c_int(0)                      # Time tagger mode end mode: collecting time
FTMT_WIN_RES_PS_64 = ctypes.c_int(6)                           # Time resolution 64ps (best for T3 mode)
GateWidth = ctypes.c_int(300) #In unit ns                      # Gate width: 300ns
GateDelay = ctypes.c_int(0) #In unit ns                        # Gate delay: no delay
FTMT_BOARD_A = ctypes.c_int(0)                                 # brd: 0 
CH_MASK_0 = ctypes.c_int(0b0001)                               # CH1 mask number
FT10X0_INPUT_EDGE_RISE = ctypes.c_int(0)                       # Positive trig slope
FTMT_CHANNEL_0 = ctypes.c_int(0)                               # CH1
FT10X0_INPUT_IMPEDENCE_HIGH = ctypes.c_int(0)                  # 1M Ohm impedence
FT10X0_INPUT_IMPEDENCE_50 = ctypes.c_int(1)                    # 50 Ohm impedence
FileSize = ctypes.c_int(500) # In unit M Bytes                 # Max file size 500 M Bytes

print(FTMT_TASK_RUN_MODE_T3.value)
print(FilePath.value)

'''Check USB connection'''
USBConnected = lib.USBConnected
USBConnected.argtypes = [ctypes.c_int]
USBConnected.restype = ctypes.c_bool
rtn = USBConnected(DEV_ID_0)
print(rtn)

'''Set time window resolution (best 64ps for T3)'''
SetTimeWindowRes = lib.SetTimeWindowRes
SetTimeWindowRes.argtypes = [ctypes.c_int, ctypes.c_int]
SetTimeWindowRes.restype = ctypes.c_int
rtn = SetTimeWindowRes(DEV_ID_0, FTMT_WIN_RES_PS_64)
print(rtn)

'''Set division frequency'''
SetStartFreqDiv = lib.SetStartFreqDiv
SetStartFreqDiv.argtypes = [ctypes.c_int, ctypes.c_int]
SetStartFreqDiv.restype = ctypes.c_int
rtn = SetStartFreqDiv(DEV_ID_0, FTMT_START_FREQ_DIV_1)
print(rtn)

'''Set gate width'''
SetGateHLWidth = lib.SetGateHLWidth
SetGateHLWidth.argtypes = [ctypes.c_int, ctypes.c_int]
SetGateHLWidth.restype = ctypes.c_int
rtn = SetGateHLWidth(DEV_ID_0, GateWidth)
print(rtn)

'''Set Start Edge'''
SetStartEdge = lib.SetStartEdge
SetStartEdge.argtypes = [ctypes.c_int, ctypes.c_int]
SetStartEdge.restype = ctypes.c_int
rtn = SetStartEdge(DEV_ID_0, FT10X0_INPUT_EDGE_RISE)
print(rtn)

'''Set start impedence''' # impedence of the sync signal which AWG4100 is used
SetStartImpedence = lib.SetStartImpedence
SetStartImpedence.argtypes = [ctypes.c_int, ctypes.c_int]
SetStartImpedence.restype = ctypes.c_int
rtn = SetStartImpedence(DEV_ID_0, FT10X0_INPUT_IMPEDENCE_50)
print(rtn)

'''Set stop edge''' # CH1 defined only
SetStopEdge = lib.SetStopEdge
SetStopEdge.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
SetStopEdge.restype = ctypes.c_int
rtn = SetStartEdge(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_EDGE_RISE)
print(rtn)

'''Set stop impedence''' # CH1 defined only
SetStopImpedence = lib.SetStopImpedence
SetStopImpedence.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
SetStopImpedence.restype = ctypes.c_int
rtn = SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_IMPEDENCE_HIGH)
print(rtn)

'''Set the gate delay (from the sync signal)'''
SetGateDelay = lib.SetGateDelay
SetGateDelay.argtypes = [ctypes.c_int, ctypes.c_int]
SetGateDelay.restype = ctypes.c_int
rtn = SetGateDelay(DEV_ID_0, GateDelay)
print(rtn)

''''''
'''Enable TTTR mode''' # 0001二进制数据打开CH1 0010打开CH2...; 0011打开CH1 CH2; 0101打开CH1 CH3...以此类推
EnableTTTR = lib.EnableTTTR
EnableTTTR.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
EnableTTTR.restype = ctypes.c_int
rtn = EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0)
print(rtn)

'''Set statistics timespan'''
SetStatisticsTime = lib.SetStatisticsTime
SetStatisticsTime.argtypes = [ctypes.c_int, ctypes.c_float]
SetStatisticsTime.restype = ctypes.c_int
rtn = SetStatisticsTime(FTMT_TASK_RUN_MODE_T3, sTime)
print(rtn)

'''Set file storation path'''
SetFilePath = lib.SetFilePath
SetFilePath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
SetFilePath.restype = ctypes.c_int
rtn = SetFilePath(DEV_ID_0, FTMT_TASK_RUN_MODE_T3, FilePath)
print(rtn)

'''Set file mode (.txt or binary) '''
SetFileMode = lib.SetFileMode
SetFileMode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
SetFileMode.restype = ctypes.c_int
rtn = SetFileMode(FTMT_TASK_RUN_MODE_T3, FTMT_FILE_SAVE_MODE_TEXT, FTMT_FILE_SERIES_MODE_EACH)
print(rtn)

'''设置SetMaxFileSize'''
SetMaxFileSize = lib.SetMaxFileSize
SetMaxFileSize.argtypes = [ctypes.c_int]
SetMaxFileSize.restype = ctypes.c_int
rtn = SetMaxFileSize(FileSize)
print(rtn)

'''Set event end mode time or counts'''
SetTTTREndMode = lib.SetTTTREndMode
SetTTTREndMode.argtypes = [ctypes.c_int]
SetTTTREndMode.restype = ctypes.c_int
rtn = SetTTTREndMode(FTMT_TTTR_END_MODE_TIME)
print(rtn)

'''Defien start task function'''
StartTask = lib.StartTask
StartTask.argtypes = [ctypes.c_int]
StartTask.restype = ctypes.c_int
rtn = StartTask(FTMT_TASK_RUN_MODE_T3)
print(rtn)
'''Define stop task function'''
StopTask = lib.StopTask
StopTask.argtypes = [ctypes.c_int]
StopTask.restype = ctypes.c_int


'''Check if task is completed'''
IsTaskCompleted = lib.IsTaskCompleted
IsTaskCompleted.restype = ctypes.c_bool
while True:
    if IsTaskCompleted() ==True:
        rtn = StopTask(FTMT_TASK_RUN_MODE_T3)
        print('Task completed: {}'.format(rtn))
        break
