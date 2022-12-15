import os
import platform
import ctypes

class ft1040_t3():

    def __init__(self):
        wd = os.path.abspath(os.path.dirname(__file__))
        arch = platform.architecture()[0]
        dll_path = ""
        if arch == '64bit':
            dll_path = os.path.join(wd, 'ft1040_dll\smncsftmt_x64.dll')
            
            print("smncsftmt_x64.dll dynamically loaded")
        else:
            dll_path = os.path.join(wd, 'ft1040_dll\smncsftmt_x86.dll')
            print("smncsftmt_x86.dll dynamically loaded")

        if os.path.isfile(dll_path):
            self.__dll = ctypes.CDLL(dll_path)
        else:
            raise Exception("Can not found dll")
        
        '''Define argtypes and restypes'''
        
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

        self.__dll.EnableTTTR.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__dll.EnableTTTR.restype = ctypes.c_int

        self.__dll.SetStatisticsTime.argtypes = [ctypes.c_int, ctypes.c_float]
        self.__dll.SetStatisticsTime.restype = ctypes.c_int

        self.__dll.SetFilePath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        self.__dll.SetFilePath.restype = ctypes.c_int

        self.__dll.SetFileMode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.__dll.SetFileMode.restype = ctypes.c_int

        self.__dll.SetMaxFileSize.argtypes = [ctypes.c_int]
        self.__dll.SetMaxFileSize.restype = ctypes.c_int

        self.__dll.SetTTTREndMode.argtypes = [ctypes.c_int]
        self.__dll.SetTTTREndMode.restype = ctypes.c_int

        self.__dll.StartTask.argtypes = [ctypes.c_int]
        self.__dll.StartTask.restype = ctypes.c_int

        self.__dll.StopTask.argtypes = [ctypes.c_int]
        self.__dll.StopTask.restype = ctypes.c_int

        self.__dll.IsTaskCompleted.restype = ctypes.c_bool

        def USBConnected(self):
            '''Check USB connection'''
            return self.__dll.USBConnected()

        def SetTimeWindowRes(self):
            '''Set time window resolution (best 64ps for T3)'''
            return self.__dll.SetTimeWindowRes()

        def SetStartFreqDiv(self):
            '''Set division frequency'''
            return self.__dll.SetStartFreqDiv()

        def SetGateHLWidth(self):
            '''Set gate width'''
            return self.__dll.SetGateHLWidth

        def SetStartEdge(self):
            '''Set Start Edge'''
            return self.__dll.SetStartEdge

        def SetStartImpedence(self):
            '''Set start impedence''' # impedence of the sync signal which ASG8100 is used
            return self.__dll.SetStartImpedence

        def SetStopEdge(self):
            '''Set stop edge''' 
            return self.__dll.SetStopEdge

        def SetStopImpedence(self):
            '''Set stop impedence'''
            return self.__dll.SetStopImpedence

        def SetGateDelay(self):
            '''Set the gate delay (from the sync signal)'''
            return self.__dll.SetGateDelay

        def EnableTTTR(self):
            '''Enable TTTR mode''' # 0001二进制数据打开CH1 0010打开CH2...; 0011打开CH1 CH2; 0101打开CH1 CH3...以此类推
            return self.__dll.EnableTTTR()

        def SetStatisticsTime(self):
            '''Set statistics timespan'''
            return self.__dll.SetStatisticsTime

        def SetFilePath(self):
            '''Set file storation path'''
            return self.__dll.SetFilePath()

        def SetFileMode(self):
            '''Set file mode (.txt or binary) '''
            return self.__dll.SetFileMode()

        def SetMaxFileSize(self):
            '''Set Max File storage Size, i.e. splitted file sizes'''
            return self.__dll.SetMaxFileSize()

        def SetTTTREndMode(self):
            '''Set event end mode time or counts'''
            return self.__dll.SetTTTREndMode()

        def StartTask(self):
            '''Define start task function'''
            return self.__dll.StartTask()

        def StopTask(self):
            '''Define stop task function'''
            return self.__dll.StopTask()

        def IsTaskCompleted(self):
            '''Check if task is completed'''
            return self.__dll.IsTaskCompleted()
