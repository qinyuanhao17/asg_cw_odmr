import os
from ctypes import *
import platform

class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]

                                                                                                                                
RECV_SIZE = 128
BUFFER = c_char * RECV_SIZE

@Singleton
class AwgDevice:
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        wd = os.path.abspath(os.path.dirname(__file__))
        arch = platform.architecture()[0]
        
        dll_path = os.path.join(wd, 'AWGDLL.dll')

        os.chdir(wd)
        if os.path.isfile(dll_path):
            self._dll = CDLL(dll_path)
        else:
            raise Exception("can not found dll")
    
    # //初始化网络             
	# AWG_API int InitMyNetwork(char * localIp);
    def init_network(self, localIp):
        localIp = c_char_p(localIp.encode("utf-8"))
        return self._dll.InitMyNetwork(localIp)

	# //连接
	# AWG_API int ConnectDevice(char *pDestinationIP, char *pDestinationMAC);
    def connect(self, ip, mac):
        ip = c_char_p(ip.encode("utf-8"))
        mac = c_char_p(mac.encode("utf-8"))
        return self._dll.ConnectDevice(ip, mac)

    # 3.1 int FindDevice(char * DestIpString, char **rsvIp, char **rsvMac);
    def find_device(self):
        """ 搜索设备 """
        rsvIp = (c_char*4096)()
        rsvMac = (c_char*4096)()
        rsvName = (c_char*4096)()
        res = self._dll.FindDevice_Str(rsvIp, rsvMac, rsvName)
        
        ret = []
        ip_str = str(rsvIp.value, encoding='utf-8')
        if ip_str != '':
            ip_list = ip_str.split("|")
            mac_list = str(rsvMac.value, encoding='utf-8').split("|")
            name_list = str(rsvName.value, encoding='utf-8').split("|")
            #print(ip_list, mac_list, name_list)
            size = min(len(ip_list), len(mac_list), len(name_list))
            for i in range(size):
                ret.append((ip_list[i], mac_list[i], name_list[i]))
        return ret

	# # 3.2 bool InitDevice(char * serAddr, int serPort, char * localAddr);
    # def init_device(self, serAddr:str, serPort:int, localAddr:str):
    #     """ 连接设备 """
    #     serAddr = c_char_p(serAddr.encode("utf-8"))
    #     serPort = c_int(serPort)
    #     localAddr = c_char_p(localAddr.encode("utf-8"))
    #     return bool(self._dll.InitDevice(serAddr, serPort, localAddr))

	# 3.3 bool CloseDevice();
    def close_device(self):
        """ 断开设备 """
        return bool(self._dll.CloseDevice())

    # 3.4 bool LoadWave(int channelNumber, const char* code);
    def load_wave_data(self, channel:int, code:str):
        """ 按照通道号下载数据 """
        channel = c_int(channel)
        code = c_char_p(code.encode('utf-8'))
        return int(self._dll.LoadWaveData(channel, code))

   # 3.5 int LoadData(int channelNumber, const char* code, char * s, char * err);
    def load_wave(self, channel:int, code:str, s:str, err:str):
        """ 按照通道号下载数据 """
        channel = c_int(channel)
        code = c_char_p(code.encode('utf-8'))
        s = c_char_p(s.encode('utf-8'))
        err = c_char_p(err.encode('utf-8'))
        return int(self._dll.LoadData(channel, code, s, err))
        
    # 3.6 int LoadAddr(int channelNumber, const char* code, char * s,char *err);
    def load_wave_addr(self, channel:int, code:str, s:str, err:str):
        """ 下载数据地址 """
        channel = c_int(channel)
        code = c_char_p(code.encode('utf-8'))
        s = c_char_p(s.encode('utf-8'))
        err = c_char_p(err.encode('utf-8'))
        return int(self._dll.LoadAddr(channel, code, s, err))
        
	# int GetDeviceName(char * recvbuf);
    def get_device_name(self):
        """ 产品名称 """
        recvbuf = BUFFER()
        res = self._dll.GetDeviceName(recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

    # int GetDeviceVersion(char * recvbuf);
    def get_device_version(self):
        """ 硬件固件版本 """
        recvbuf = BUFFER()
        res = self._dll.GetDeviceVersion(recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

    # int GetLocked(char * recvbuf);
    def get_locked(self):
        """ 时钟locked同步 """
        recvbuf = BUFFER()
        res = self._dll.GetLocked(recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

    # AWG_API int SystemInit(char * recvbuf);
    def system_init(self):
        """ 系统复位 """
        resvbuf = BUFFER()
        res = self._dll.SystemInit(resvbuf)
        return res, str(resvbuf.value, encoding='utf-8')

    # 3.5 int AwgBroadcast(int channelNumber, int mode, char * recvbuf);
    def awg_broadcast(self, channel:int, mode:int):
        """ 按照通道号播放波形 """
        channel = c_int(channel)
        mode = c_int(mode)
        recvbuf = BUFFER()
        res = self._dll.AwgBroadcast(channel, mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

	# 3.6 int AwgCastNumber(int mode, char * recvbuf);
    def awg_cast_number(self, repeat:int):
        """ AWG播放次数 """
        repeat = c_int(repeat)
        recvbuf = BUFFER()
        res = self._dll.AwgCastNumber(repeat, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

	# 3.7 int AwgCastMode(int mode, char * recvbuf);
    def awg_cast_mode(self, mode:int):
        """ AWG播放模式 """
        mode = c_int(mode)
        recvbuf = BUFFER()
        res =  self._dll.AwgCastMode(mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

	# 3.8 int AwgOffset(int channelNumber, char * Offset, char * recvbuf);
    def awg_offset(self, channel:int, offset:str):
        """ AWG通道偏置 """
        channel = c_int(channel)
        offset = c_char_p(offset.encode('utf-8'))
        recvbuf = BUFFER()
        res =  self._dll.AwgOffset(channel, offset, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

	# 3.9 int ClockMode(int mode, char * recvbuf);
    def clock_mode(self, mode:int):
        """ 时钟模式 """
        mode = c_int(mode)
        recvbuf = BUFFER()
        res = self._dll.ClockMode(mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

    # 3.10 int SamplingRate(int mode, char * recvbuf);
    # def sampling_rate(self, mode:int):
    #     """ 采样率 """
    #     mode = c_int(mode)
    #     recvbuf = BUFFER()
    #     res = self._dll.SamplingRate(mode, recvbuf)
    #     return res, str(recvbuf.value, encoding='utf-8')

    # 3.11 int ChannelMode(int mode, char * recvbuf);
    def channel_mode(self, mode:int):
        """ 独立、组合模式 """
        mode = c_int(mode)
        recvbuf = BUFFER()
        res = self._dll.ChannelMode(mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

    # AWG_API int ExperimentMode(int channelNumber, int mode, char * recvbuf);

	# # 3.12 int TrggerOutMode(int mode, char * recvbuf);
    # def trigger_out_mode(self, mode:int):
    #     """ trgger输出模式 """
    #     mode = c_int(mode)
    #     recvbuf = BUFFER()
    #     res = self._dll.TriggerOutMode(mode, recvbuf)
    #     return res, str(recvbuf)
    
	# 3.13 int ChannelONOFF(int channelNumber, int mode, char * recvbuf);
    def channel_switch(self, channel:int, mode:int):
        """ 组合通道开关 """
        channel = c_int(channel)
        mode = c_int(mode)
        recvbuf = BUFFER()
        res = self._dll.ChannelONOFF(channel, mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

	# 3.14 int MarkerONOFF(int channelNumber, int mode, char * recvbuf);
    def marker_switch(self, channel:int, mode:int):
        """ Marker开关 """
        channel = c_int(channel)
        mode = c_int(mode)
        recvbuf = BUFFER()
        res = self._dll.MarkerONOFF(channel, mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')

	# 3.15 int DDSCast(int channelNumber, int mode, char * recvbuf);
    def DDS_cast(self, channel:int, mode:int):
        """ DDS播放 """
        channel = c_int(channel)
        mode = c_int(mode)
        recvbuf = BUFFER()
        res = self._dll.DDSCast(channel, mode, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
    
    # 3.16 int RateControl(int channelNumber, char * frequencyChannel, char * recvbuf);
    def rate_control(self, channel: int, freq: str):
        """ 频率控制字 """
        channel = c_int(channel)
        freq = c_char_p(freq.encode('utf-8'))
        recvbuf = BUFFER()
        res = self._dll.RateControl(channel, freq, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
	
	# 3.17 int PhaseControl(int channelNumber, char * phaseChannel, char * recvbuf);
    def phase_control(self, channel:int, phase:str):
        """ 相位控制字 """
        channel = c_int(channel)
        phase = c_char_p(phase.encode('utf-8'))
        recvbuf = BUFFER()
        res = self._dll.PhaseControl(channel, phase, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
	
	# 3.18 int RangeControl(int channelNumber, char * amplitudeValue, char * recvbuf);
    def range_control(self, channel:int, ampl:str):
        """ 幅度控制字 """
        channel = c_int(channel)
        ampl = c_char_p(ampl.encode('utf-8'))
        recvbuf = BUFFER()
        res = self._dll.RangeControl(channel, ampl, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
	
	#  3.19 int OffsetControl(int channelNumber, char * offsetChannel, char * recvbuf);
    def offset_control(self, channel:int, offset:str):
        """ 偏置控制字 """
        channel = c_int(channel)
        offset = c_char_p(offset.encode('utf-8'))
        recvbuf = BUFFER()
        res = self._dll.OffsetControl(channel, offset, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
        
        
    # AWG_API int PlayStatus(int channelNumber, char * playMode, char * expermentMode);
    def awg_PlayStatus(self, channel:int): 
        channel = c_int(channel)
        playMode = BUFFER()
        expermentMode = BUFFER()
        res = self._dll.PlayStatus(channel, playMode, expermentMode)
        return res, str(playMode.value, encoding='utf-8'), str(expermentMode.value, encoding='utf-8')
  
        
	# # 3.20 int DDSSetMode(int channelNumber, double frequencyChannel, double phaseChannel, unsigned short amplitudeValue, short biasChannel);
    # def set_DDS_mode(self, channel:int, freq:float, phase:float, ampl:float, bias:float):
    #     """ DDS模式下载 """
    #     channel = c_int(channel)
    #     freq = c_double(freq)
    #     phase = c_double(phase)
    #     ampl = c_ushort(ampl)
    #     bias = c_short(bias)
    #     return self._dll.DDSSetMode(channel, freq, phase, ampl, bias)

	# 3.21 int LoadPara(char * filename, char * recvbuf);
    def load_params(self, filename:str):
        """ 加载参数 """
	    #filename = c_char_p(filename.encode('utf-8'))
        filename = c_char_p(filename.encode('utf-8'))
        recvbuf = BUFFER()
        res = self._dll.LoadPara(filename, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
    
	# 3.22 int SavePara(char * filename, char * recvbuf);
    def save_params(self, filename:str):
        """ 保存参数 """
        filename = c_char_p(filename.encode('utf-8'))
        recvbuf = BUFFER()
        res = self._dll.SavePara(filename, recvbuf)
        return res, str(recvbuf.value, encoding='utf-8')
       