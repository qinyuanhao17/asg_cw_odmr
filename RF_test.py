import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())
my_instrument = rm.open_resource('USB0::0x1AB1::0x099C::DSG8M213400002::INSTR')

#check connection 1
print(my_instrument.query('*IDN?'))

#check connection 2
my_instrument.write('*IDN?')
print(my_instrument.read())

#read available file information under path
my_instrument.write(':MMEMory:CATalog? E:\RFList')
#Load file (have to chose load-file-type first)
my_instrument.write(':MMEMory:LOAD RFTEST1.CSV')
'''
Programming logic sample
使用 SCPI 命令实现如下功能： 配置连续的线性步进扫描，从[RF OUTPUT 50Ω]连接器输出一个 RF 扫描信号：频率范围为 1GHz 至 2GHz， 电平范围为-20dBm 至 0dBm，扫描点数为 10，驻留时间为 500ms。
1. *IDN? /*查询射频信号源 ID 字符串以检测远程通信是否正常*/
2. :SYST:PRES:TYPE FAC /*选择预置类型为“出厂设置”*/
3. :SYST:PRES /*将仪器恢复至出厂设置（扫描模式默认为连续，扫描方式默认为步进，扫描间隔默认为线性）*/
4. :SWE:STEP:STAR:FREQ 1GHz /*设置步进扫描的起始频率为 1GHz*/
5. :SWE:STEP:STOP:FREQ 2GHz /*设置步进扫描的终止频率为 2GHz*/
6. :SWE:STEP:STAR:LEV -20 /*设置步进扫描的起始电平为-20dBm*/
7. :SWE:STEP:STOP:LEV 0 /*设置步进扫描的终止电平为 0dBm*/
8. :SWE:STEP:POIN 10 /*设置步进扫描的扫描点数为 10*/
9. :SWE:STEP:DWEL 500ms /*设置步进扫描的驻留时间为 500ms*/
10. :SWE:STAT LEV,FREQ /*同时启用频率和电平扫描功能*/ 
11. :OUTP ON /*打开 RF 输出开关*/
'''






