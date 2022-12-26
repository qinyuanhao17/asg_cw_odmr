import os
import platform
import ctypes

DEV_ID_0 = ctypes.c_int(0)                                     # Device ID
FTMT_TASK_RUN_MODE_T3 = ctypes.c_int(0x03)                     # T3 Mode
FilePath = ctypes.c_char_p(b"D:\ODMRequipment\File")           # File path
sTime = ctypes.c_float(1) # in second unit                    # Collecting time 
FTMT_START_FREQ_DIV_1 = ctypes.c_int(1)                        # Frequency division time
FTMT_FILE_SAVE_MODE_BIN = ctypes.c_int(1)                      # Binary file type
FTMT_FILE_SAVE_MODE_TEXT = ctypes.c_int(2)                     # Text file type
FTMT_FILE_SERIES_MODE_EACH = ctypes.c_int(0)                   # T1 Mode parameters(useless here)

FTMT_TTTR_END_MODE_TIME = ctypes.c_int(0)                      # Time tagger mode end mode: collecting time
FTMT_TTTR_END_MODE_EVENT = ctypes.c_int(1)

FTMT_WIN_RES_PS_64 = ctypes.c_int(6)                           # Time resolution 64ps (best for T3 mode)
GateWidth = ctypes.c_int(1000) #In unit ns                      # Gate width: 300ns
GateDelay = ctypes.c_int(0) #In unit ns                        # Gate delay: no delay
FTMT_BOARD_A = ctypes.c_int(0)                                 # brd: 0 

CH_MASK_0001 = ctypes.c_uint8(0b0001)                             # CH1 mask number
CH_MASK_0010 = ctypes.c_uint8(0b0010) 
CH_MASK_0100 = ctypes.c_uint8(0b0100) 
CH_MASK_1000 = ctypes.c_uint8(0b1000) 
CH_MASK_0011 = ctypes.c_uint8(0b0011) 
CH_MASK_0101 = ctypes.c_uint8(0b0101) 
CH_MASK_1001 = ctypes.c_uint8(0b1001) 
CH_MASK_0110 = ctypes.c_uint8(0b0110) 
CH_MASK_1010 = ctypes.c_uint8(0b1010) 
CH_MASK_1100 = ctypes.c_uint8(0b1100) 
CH_MASK_0111 = ctypes.c_uint8(0b0111) 
CH_MASK_1011 = ctypes.c_uint8(0b1011) 
CH_MASK_1101 = ctypes.c_uint8(0b1101) 
CH_MASK_1110 = ctypes.c_uint8(0b1110)
CH_MASK_1111 = ctypes.c_uint8(0b1111)  

FT10X0_INPUT_EDGE_RISE = ctypes.c_int(0)                       # Positive trig slope
FT10X0_INPUT_EDGE_FALL = ctypes.c_int(1)                       # Negative trig slope

FTMT_CHANNEL_0 = ctypes.c_int(0)                               # CH1
FTMT_CHANNEL_1 = ctypes.c_int(1)                               # CH2
FTMT_CHANNEL_2 = ctypes.c_int(2)                               # CH3
FTMT_CHANNEL_3 = ctypes.c_int(3)                               # CH4

FT10X0_INPUT_IMPEDENCE_HIGH = ctypes.c_int(0)                  # 1M Ohm impedence
FT10X0_INPUT_IMPEDENCE_50 = ctypes.c_int(1)                    # 50 Ohm impedence
FileSize = ctypes.c_int(100)              # In unit M Bytes                   # Max file size 500 M Bytes

class ft1040():

    def __init__(self):

        '''Dynamically loading dll library'''   #This part can be replaced by __dll = ctypes.CDLL("absolute or relative location of the .dll file")
        wd = os.path.abspath(os.path.dirname(__file__))
        arch = platform.architecture()[0]
        dll_path = ""
        if arch == '64bit':
            dll_path = os.path.join(wd, 'dll_ft1040\dll_x64\smncsftmt.dll')
            
            print("64 bit smncsftmt.dll is dynamically loaded")
        else:
            dll_path = os.path.join(wd, 'dll_ft1040\dll_x86\smncsftmt.dll')
            print("32 bit smncsftmt.dll is dynamically loaded")

        if os.path.isfile(dll_path):
            self.__dll = ctypes.CDLL(dll_path)
        else:
            raise Exception("Can not found dll")
        
        '''Define argtypes and restypes'''
        
        self.__dll.GetDevType.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.__dll.GetDevType.restype = ctypes.c_int

        self.__dll.USBConnected.argtypes = [ctypes.c_int]
        self.__dll.USBConnected.restype = ctypes.c_bool

        self.__dll.SetTimeWindowRes.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetTimeWindowRes.restype = ctypes.c_int

        self.__dll.SetStartFreqDiv.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetStartFreqDiv.restype = ctypes.c_int

        self.__dll.SetGateHLWidth.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetGateHLWidth.restype = ctypes.c_int

        self.__dll.SetStartEdge.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetStartEdge.restype = ctypes.c_int

        self.__dll.SetStartImpedence.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetStartImpedence.restype = ctypes.c_int

        self.__dll.SetStopEdge.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__dll.SetStopEdge.restype = ctypes.c_int

        self.__dll.SetStopImpedence.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__dll.SetStopImpedence.restype = ctypes.c_int

        self.__dll.SetGateDelay.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetGateDelay.restype = ctypes.c_int

        self.__dll.EnableTTTR.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint8]
        self.__dll.EnableTTTR.restype = ctypes.c_int

        self.__dll.SetStatisticsTime.argtypes = [ctypes.c_int, ctypes.c_float]
        self.__dll.SetStatisticsTime.restype = ctypes.c_int

        self.__dll.SetFilePath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        self.__dll.SetFilePath.restype = ctypes.c_int

        self.__dll.SetFileMode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__dll.SetFileMode.restype = ctypes.c_int

        self.__dll.SetMaxFileSize.argtypes = [ctypes.c_int, ctypes.c_int]
        self.__dll.SetMaxFileSize.restype = ctypes.c_int

        self.__dll.GetFilePath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        self.__dll.GetFilePath.restype = ctypes.c_int


        self.__dll.SetTTTREndMode.argtypes = [ctypes.c_int]
        self.__dll.SetTTTREndMode.restype = ctypes.c_int

        self.__dll.StartTask.argtypes = [ctypes.c_int]
        self.__dll.StartTask.restype = ctypes.c_int

        self.__dll.StopTask.argtypes = [ctypes.c_int]
        self.__dll.StopTask.restype = ctypes.c_int

        self.__dll.IsTaskCompleted.restype = ctypes.c_bool

    def GetDevType(self, devId = ctypes.c_int(), d_str = ctypes.c_char_p()):
        '''Check if the device is FT1040'''
        return hex(self.__dll.GetDevType(devId, d_str))

    def USBConnected(self, devId = ctypes.c_int()):
        '''Check USB connection'''
        return self.__dll.USBConnected(devId)

    def SetTimeWindowRes(self, devId = ctypes.c_int(), winRes = ctypes.c_int()):
        '''Set time window resolution (best 64ps for T3)'''
        return self.__dll.SetTimeWindowRes(devId, winRes)

    def SetStartFreqDiv(self, devId = ctypes.c_int(), freqDiv = ctypes.c_int()):
        '''Set division frequency'''
        return self.__dll.SetStartFreqDiv(devId, freqDiv)

    def SetGateHLWidth(self, devId = ctypes.c_int(), width = ctypes.c_int()):
        '''Set gate width'''
        return self.__dll.SetGateHLWidth(devId, width)

    def SetStartEdge(self, devId = ctypes.c_int(), edge = ctypes.c_int()):
        '''Set Start Edge'''
        return self.__dll.SetStartEdge(devId, edge)

    def SetStartImpedence(self, devId = ctypes.c_int(), impedence = ctypes.c_int()):
        '''Set start impedence''' # impedence of the sync signal which ASG8100 is used
        return self.__dll.SetStartImpedence(devId, impedence)

    def SetStopEdge(self, devId = ctypes.c_int(), brd = ctypes.c_int(), chl = ctypes.c_int(), edge = ctypes.c_int()):
        '''Set stop edge''' 
        return self.__dll.SetStopEdge(devId, brd, chl, edge)

    def SetStopImpedence(self, devId = ctypes.c_int(), brd = ctypes.c_int(), chl = ctypes.c_int(), impedence = ctypes.c_int()):
        '''Set stop impedence'''
        return self.__dll.SetStopImpedence(devId, brd, chl, impedence)

    def SetGateDelay(self, devId = ctypes.c_int(), delay = ctypes.c_int()):
        '''Set the gate delay (from the sync signal)'''
        return self.__dll.SetGateDelay(devId, delay)

    def EnableTTTR(self, devId = ctypes.c_int(), brd = ctypes.c_int(), mask8 = ctypes.c_uint8()):
        '''Enable TTTR mode''' # 0001二进制数据打开CH1 0010打开CH2...; 0011打开CH1 CH2; 0101打开CH1 CH3...以此类推
        return self.__dll.EnableTTTR(devId, brd, mask8)

    def SetStatisticsTime(self, rMode = ctypes.c_int(), sTime = ctypes.c_float()):
        '''Set statistics timespan'''
        return self.__dll.SetStatisticsTime(rMode, sTime)

    def SetFilePath(self, devId = ctypes.c_int(), rMode = ctypes.c_int(), path = ctypes.c_char_p()):
        '''Set file storation path'''
        return self.__dll.SetFilePath(devId, rMode, path)

    def SetFileMode(self, rMode = ctypes.c_int(), sMode = ctypes.c_int(), fMode = ctypes.c_int()):
        '''Set file mode (.txt or binary) '''
        return self.__dll.SetFileMode(rMode, sMode, fMode)

    def SetMaxFileSize(self,devId = ctypes.c_int(), size = ctypes.c_int()):
        '''Set Max File storage Size, i.e. splitted file sizes''' # Size has unit Mega Bytes
        return self.__dll.SetMaxFileSize(devId, size)
    
    def GetFilePath(self, devId = ctypes.c_int(), rMode = ctypes.c_int(), path = ctypes.c_char_p()):
        return self.__dll.GetFilePath(devId, rMode, path)

    def SetTTTREndMode(self, eMode = ctypes.c_int(), eCounts = int()):
        '''Set event end mode time or counts''' # Only time end mode is considered here, which is eMode = 0
        if eCounts == 0:
            return self.__dll.SetTTTREndMode(eMode)
        else:
            eCounts = ctypes.c_uint64(eCounts)
            self.__dll.SetTTTREndMode.argtypes = [ctypes.c_int, ctypes.c_uint64]
            self.__dll.SetTTTREndMode.restype = ctypes.c_int
            return self.__dll.SetTTTREndMode(eMode, eCounts)

    def StartTask(self, rMode = ctypes.c_int()):
        '''Define start task function'''
        return self.__dll.StartTask(rMode)

    def StopTask(self, rMode = ctypes.c_int()):
        '''Define stop task function'''
        return self.__dll.StopTask(rMode)

    def IsTaskCompleted(self):
        '''Check if task is completed'''
        return self.__dll.IsTaskCompleted()

    '''
    Functions that are not defined here:
    SetBlockedWindow
    SetStartThreshold
    SetStopThreshold
    SetStopDelay
    SetPulseCycle
    GetRunMode
    GetSignalStatus
    GetDllVersion
    GetFilePath
    SetMaxBarValue
    SetT1Interval
    EnableT1
    EnableT3T1
    GetT1Data
    GetT1Status
    GetElapsedTime
    EnableITTR
    SetITTRInterval
    SetITTREndMode
    GetActualEvents
    SetMemoryDataMode
    MemoryDataModeEnabled
    GetMemoryData
    ReleaseMemoryData
    dmtch_Initialize
    dmtch_AddStrategy
    dmtch_GetStratgyCount
    dmtch_GetChlCount
    dmtch_GetChlData
    MarkMainDevice
    EnableConcurrentMode
    '''

if __name__ == "__main__":
    dev = ft1040()
    type = type(dev.GetDevType(0, ctypes.c_char_p(b"my dev")))
    print(type)

    '''Check USB connection'''
    rtn = dev.USBConnected(0)
    print(rtn)

    '''Set time window resolution (best 64ps for T3)'''
    rtn = dev.SetTimeWindowRes(DEV_ID_0, FTMT_WIN_RES_PS_64)
    print(rtn)

    '''Set division frequency'''
    rtn = dev.SetStartFreqDiv(DEV_ID_0, FTMT_START_FREQ_DIV_1)
    print(rtn)

    '''Set gate width'''
    rtn = dev.SetGateHLWidth(DEV_ID_0, GateWidth)
    print(rtn)

    '''Set Start Edge'''
    rtn = dev.SetStartEdge(DEV_ID_0, FT10X0_INPUT_EDGE_RISE)
    print(rtn)

    '''Set start impedence''' # impedence of the sync signal which AWG4100 is used    
    rtn = dev.SetStartImpedence(DEV_ID_0, FT10X0_INPUT_IMPEDENCE_50)
    print(rtn)

    '''Set stop edge''' # CH1 defined only
    rtn = dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_EDGE_RISE)
    print(rtn)

    '''Set stop impedence''' # CH1 defined only
    rtn = dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_IMPEDENCE_50)
    print(rtn)

    '''Set the gate delay (from the sync signal)'''
    rtn = dev.SetGateDelay(DEV_ID_0, GateDelay)
    print(rtn)

    '''Enable TTTR mode''' 
    rtn = dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0001)
    print(rtn)

    '''Set statistics timespan'''
    rtn = dev.SetStatisticsTime(FTMT_TASK_RUN_MODE_T3, sTime)
    print(rtn)

    '''Set file storation path'''
    rtn = dev.SetFilePath(DEV_ID_0, FTMT_TASK_RUN_MODE_T3, FilePath)
    print(rtn)

    '''Set file mode (.txt or binary) '''
    rtn = dev.SetFileMode(FTMT_TASK_RUN_MODE_T3, FTMT_FILE_SAVE_MODE_TEXT, FTMT_FILE_SERIES_MODE_EACH)
    print(rtn)

    '''设置SetMaxFileSize'''
    rtn = dev.SetMaxFileSize(DEV_ID_0, FileSize)
    print(rtn)

    '''Set event end mode time or counts'''
    rtn = dev.SetTTTREndMode(FTMT_TTTR_END_MODE_TIME)
    print(rtn)

    '''Define start task function'''
    rtn = dev.StartTask(FTMT_TASK_RUN_MODE_T3)
    print(rtn)

    while True:
        if dev.IsTaskCompleted() ==True:
            rtn = dev.StopTask(FTMT_TASK_RUN_MODE_T3)
            print('Task completed: {}'.format(rtn))
            break
