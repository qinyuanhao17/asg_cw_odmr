import sys
import os
import time
import platform
import struct
import socket
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import asg_cw_odmr_ui
from threading import Thread
from ft1040_SDK import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QMouseEvent, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent
from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsDropShadowEffect, QVBoxLayout, QLabel, QFileDialog, QDesktopWidget

class MyWindow(asg_cw_odmr_ui.Ui_Form, QWidget):

    rf_info_msg = pyqtSignal(str)
    ft_info_msg = pyqtSignal(str)
    ft_ply_btn_msg = pyqtSignal(str)
    ft_progressBar_msg = pyqtSignal(int)

    def __init__(self):

        super().__init__()

        # init UI
        self.setupUi(self)
        self.ui_width = int(QDesktopWidget().availableGeometry().size().width()*0.75)
        self.ui_height = int(QDesktopWidget().availableGeometry().size().height()*0.72)
        self.resize(self.ui_width, self.ui_height)
        center_pointer = QDesktopWidget().availableGeometry().center()
        x = center_pointer.x()
        y = center_pointer.y()
        old_x, old_y, width, height = self.frameGeometry().getRect()
        self.move(int(x - width / 2), int(y - height / 2))

        # set flag off and widget translucent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # set window blur
        self.render_shadow()
        
        # init window button signal
        self.window_btn_signal()

        '''
        RF init
        '''
        # Init RF combobox ui
        self.rf_cbx_test()
        
        # Init RF setup info ui
        self.rf_info_ui()

        # Init RF signal
        self.my_rf_signal()

        '''
        FT1040 init
        '''
        self.dev = ft1040()
        
        # Init ui
        self.ft_init_ui()
        self.ft_info_ui()
        
        # Init signal
        self.ft_signal()

        # Check FT1040connection
        self.check_ft_connection()
        
    '''
    FT1040 control
    '''    

    def ft_signal(self):

        # Choose file path
        self.ft_smp_ld_btn.clicked.connect(self.ft_smp_ld)
        # Message signal
        self.ft_info_msg.connect(self.ft_slot)
        self.ft_ply_btn_msg.connect(self.ft_ply_btn_enable)
        self.ft_progressBar_msg.connect(self.progressBar_setvalue)
        # Scroll area setting auto slide
        self.ft_scroll.verticalScrollBar().rangeChanged.connect(
            lambda: self.ft_scroll.verticalScrollBar().setValue(
                self.ft_scroll.verticalScrollBar().maximum()
            )
        )
        # basic setting signal
        self.basic_set_btn.clicked.connect(self.basic_setting)
        # trig setting signal
        self.trig_set_btn.clicked.connect(self.trig_setting)
        # File size setting signal
        self.set_file_size_btn.clicked.connect(self.file_size_setting)
        # File location open button signal
        self.open_folder_btn.clicked.connect(self.open_folder)
        # Enable TTTR mode signal
        self.enable_tttr_btn.clicked.connect(self.enable_tttr_mode)
        # Time or event stop signal
        self.time_stp_set_btn.clicked.connect(self.time_stop_mode)
        self.event_stp_set_btn.clicked.connect(self.event_stop_mode)

        # FT1040 play button signal
        self.ft_ply_btn.clicked.connect(self.ft_ply)

        '''Define reconfirm button signals to set all parameters that is not changed in the last test'''
        self.reconfirm_btn.clicked.connect(self.basic_setting)
        self.reconfirm_btn.clicked.connect(self.trig_setting)
        self.reconfirm_btn.clicked.connect(self.ft_smp_ld)
        self.reconfirm_btn.clicked.connect(self.file_size_setting)
        self.reconfirm_btn.clicked.connect(self.enable_tttr_mode)
        self.reconfirm_btn.clicked.connect(self.time_stop_mode)
        self.reconfirm_btn.clicked.connect(self.event_stop_mode)

    def ft_init_ui(self):
        
        '''Init Resolution combobox ui'''
        t3_res_list = []
        t3_res_str_list = []
        for i in range(6,26):
            t3_res_list.append(2**i)
            t3_res_str_list.append('{}ps'.format(2**i))
        self.t3_res_list = t3_res_list
        self.t3_res_str_list = t3_res_str_list
        self.res_cbx_btn.addItems(t3_res_str_list)

        # Init Frequency Division combobox ui
        self.frq_div_cbx_btn.addItems(['1', '2', '4', '8'])

    def check_ft_connection(self):
        rtn = self.dev.USBConnected(DEV_ID_0)
        dev_type = self.dev.GetDevType(DEV_ID_0, b"my_dev")
        if rtn == True:
            self.ft_info_msg.emit("Connection succeeded: FT{}P".format(dev_type[2:]))
            self.ft_info_msg.emit("-"*60)
        else:
            self.ft_info_msg.emit("Connection failed.")
            self.ft_info_msg.emit("-"*60)

    def basic_setting(self):

        '''Set Window resolution'''
        resolution_str = self.res_cbx_btn.currentText()
        index = self.t3_res_str_list.index(resolution_str)
        # print(index)
        resolution = ctypes.c_int(index+6)
        # print(resolution)
        # print(type(resolution))
        rtn = self.dev.SetTimeWindowRes(DEV_ID_0, resolution)
        if rtn == 0:
            self.ft_info_msg.emit("Time window resolution is setted to: {}".format(resolution_str))
        else:
            self.ft_info_msg.emit("Setting time window resolution failed.")

        '''Set start frequency division'''
        frq_div_str = self.frq_div_cbx_btn.currentText()
        frq_div = ctypes.c_int(int(frq_div_str))
        # print(frq_div)
        # print(type(frq_div))
        # print(frq_div_str)
        rtn = self.dev.SetStartFreqDiv(DEV_ID_0, frq_div)
        if rtn == 0:
            self.ft_info_msg.emit("Start frequency division is setted to: {}".format(frq_div_str))
        else:
            self.ft_info_msg.emit("Setting start frequency division failed.")

        '''Set gate delay'''
        gate_delay_str = self.gate_delay_ledit.text()
        gate_delay = ctypes.c_int(int(gate_delay_str))
        # print(gate_delay)
        rtn = self.dev.SetGateDelay(DEV_ID_0, gate_delay)
        if rtn == 0:
            self.ft_info_msg.emit("Gate delay is setted to: {}".format(gate_delay_str))
        else:
            self.ft_info_msg.emit("Setting gate delay failed.")
        
        '''Set gate width'''
        gate_width_str = self.gate_width_ledit.text()
        gate_width = ctypes.c_int(int(gate_width_str))
        rtn = self.dev.SetGateHLWidth(DEV_ID_0, gate_width)
        if rtn == 0:
            self.ft_info_msg.emit("Gate width is setted to: {}".format(gate_width_str))
            self.ft_info_msg.emit("-"*60)
        else:
            self.ft_info_msg.emit("Setting gate width failed.")
            self.ft_info_msg.emit("-"*60)
    
    def trig_setting(self):

        '''Setting sync input impedence'''
        sync_imp = self.sync_imp_cbx.currentText()
        if sync_imp == "50Ω":
            rtn = self.dev.SetStartImpedence(DEV_ID_0, FT10X0_INPUT_IMPEDENCE_50)
            if rtn == 0:
                self.ft_info_msg.emit("Sync input impedence is setted to: {}".format(sync_imp))
            else:
                self.ft_info_msg.emit("Setting sync input impedence failed.")
        elif sync_imp == "1MΩ":
            rtn = self.dev.SetStartImpedence(DEV_ID_0, FT10X0_INPUT_IMPEDENCE_HIGH)
            if rtn == 0:
                self.ft_info_msg.emit("Sync input impedence is setted to: {}".format(sync_imp))
            else:
                self.ft_info_msg.emit("Setting sync input impedence failed.")

        '''Setting sync input Edge'''
        sync_trig = self.sync_trig_cbx.currentText()
        # print(sync_trig)
        if sync_trig == "Positive":
            rtn = self.dev.SetStartEdge(DEV_ID_0, FT10X0_INPUT_EDGE_RISE)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("Sync input edge is setted to: {}".format(sync_trig))
            else:
                self.ft_info_msg.emit("Setting sync input edge failed.")
        elif sync_trig == "Negative":
            rtn = self.dev.SetStartEdge(DEV_ID_0, FT10X0_INPUT_EDGE_FALL)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("Sync input edge is setted to: {}".format(sync_trig))
            else:
                self.ft_info_msg.emit("Setting sync input edge failed.")

        '''Setting CH1 input impedence'''
        ch1_imp = self.ch1_imp_cbx.currentText()
        if ch1_imp == "50Ω":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_IMPEDENCE_50)
            if rtn == 0:
                self.ft_info_msg.emit("CH1 input impedence is setted to: {}".format(ch1_imp))
            else:
                self.ft_info_msg.emit("Setting CH1 input impedence failed.")
        elif ch1_imp == "1MΩ":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_IMPEDENCE_HIGH)
            if rtn == 0:
                self.ft_info_msg.emit("CH1 input impedence is setted to: {}".format(ch1_imp))
            else:
                self.ft_info_msg.emit("Setting CH1 input impedence failed.")

        '''Setting CH1 input edge'''
        ch1_trig = self.ch1_trig_cbx.currentText()
        # print(ch1_trig)
        if ch1_trig == "Positive":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_EDGE_RISE)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH1 input edge is setted to: {}".format(ch1_trig))
            else:
                self.ft_info_msg.emit("Setting CH1 input edge failed.")
        elif ch1_trig == "Negative":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_0, FT10X0_INPUT_EDGE_FALL)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH1 input edge is setted to: {}".format(ch1_trig))
            else:
                self.ft_info_msg.emit("Setting CH1 input edge failed.")

        '''Setting CH2 input impedence'''
        ch2_imp = self.ch2_imp_cbx.currentText()
        if ch2_imp == "50Ω":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_1, FT10X0_INPUT_IMPEDENCE_50)
            if rtn == 0:
                self.ft_info_msg.emit("CH2 input impedence is setted to: {}".format(ch2_imp))
            else:
                self.ft_info_msg.emit("Setting CH2 input impedence failed.")
        elif ch2_imp == "1MΩ":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_1, FT10X0_INPUT_IMPEDENCE_HIGH)
            if rtn == 0:
                self.ft_info_msg.emit("CH2 input impedence is setted to: {}".format(ch2_imp))
            else:
                self.ft_info_msg.emit("Setting CH2 input impedence failed.")

        '''Setting CH2 input edge'''
        ch2_trig = self.ch2_trig_cbx.currentText()
        # print(ch2_trig)
        if ch2_trig == "Positive":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_1, FT10X0_INPUT_EDGE_RISE)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH2 input edge is setted to: {}".format(ch2_trig))
            else:
                self.ft_info_msg.emit("Setting CH2 input edge failed.")
        elif ch1_trig == "Negative":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_1, FT10X0_INPUT_EDGE_FALL)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH2 input edge is setted to: {}".format(ch2_trig))
            else:
                self.ft_info_msg.emit("Setting CH2 input edge failed.")
        
        '''Setting CH3 input impedence'''
        ch3_imp = self.ch3_imp_cbx.currentText()
        if ch3_imp == "50Ω":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_2, FT10X0_INPUT_IMPEDENCE_50)
            if rtn == 0:
                self.ft_info_msg.emit("CH3 input impedence is setted to: {}".format(ch3_imp))
            else:
                self.ft_info_msg.emit("Setting CH3 input impedence failed.")
        elif ch3_imp == "1MΩ":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_2, FT10X0_INPUT_IMPEDENCE_HIGH)
            if rtn == 0:
                self.ft_info_msg.emit("CH3 input impedence is setted to: {}".format(ch3_imp))
            else:
                self.ft_info_msg.emit("Setting CH3 input impedence failed.")

        '''Setting CH3 input edge'''
        ch3_trig = self.ch3_trig_cbx.currentText()
        # print(ch3_trig)
        if ch3_trig == "Positive":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_2, FT10X0_INPUT_EDGE_RISE)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH3 input edge is setted to: {}".format(ch3_trig))
            else:
                self.ft_info_msg.emit("Setting CH3 input edge failed.")
        elif ch3_trig == "Negative":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_2, FT10X0_INPUT_EDGE_FALL)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH3 input edge is setted to: {}".format(ch3_trig))
            else:
                self.ft_info_msg.emit("Setting CH3 input edge failed.")

        '''Setting CH4 input impedence'''
        ch4_imp = self.ch4_imp_cbx.currentText()
        if ch4_imp == "50Ω":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_3, FT10X0_INPUT_IMPEDENCE_50)
            if rtn == 0:
                self.ft_info_msg.emit("CH4 input impedence is setted to: {}".format(ch4_imp))
            else:
                self.ft_info_msg.emit("Setting CH4 input impedence failed.")
        elif ch4_imp == "1MΩ":
            rtn = self.dev.SetStopImpedence(DEV_ID_0, 0, FTMT_CHANNEL_3, FT10X0_INPUT_IMPEDENCE_HIGH)
            if rtn == 0:
                self.ft_info_msg.emit("CH4 input impedence is setted to: {}".format(ch4_imp))
            else:
                self.ft_info_msg.emit("Setting CH4 input impedence failed.")

        '''Setting CH4 input edge'''
        ch4_trig = self.ch4_trig_cbx.currentText()
        # print(ch4_trig)
        if ch4_trig == "Positive":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_3, FT10X0_INPUT_EDGE_RISE)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH4 input edge is setted to: {}".format(ch4_trig))
            else:
                self.ft_info_msg.emit("Setting CH4 input edge failed.")
        elif ch4_trig == "Negative":
            rtn = self.dev.SetStopEdge(DEV_ID_0, 0, FTMT_CHANNEL_3, FT10X0_INPUT_EDGE_FALL)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("CH4 input edge is setted to: {}".format(ch4_trig))
            else:
                self.ft_info_msg.emit("Setting CH4 input edge failed.")
        
        '''Setting SYNC input threshold'''
        sync_thresh_str = self.sync_thresh_ledit.text()
        self.sync_thresh = ctypes.c_int(int(sync_thresh_str))
        rtn = self.dev.SetStartThreshold(DEV_ID_0, FTMT_BOARD_A, self.sync_thresh)
        if rtn == 0:
            self.ft_info_msg.emit("SYNC input threshold is setted to: {}".format(sync_thresh_str))
        else:
            self.ft_info_msg.emit("Setting SYNC input threshold failed.")
        
        '''Setting CH1 input threshold'''
        ch1_thresh_str = self.ch1_thresh_ledit.text()
        self.ch1_thresh = ctypes.c_int(int(ch1_thresh_str))
        rtn = self.dev.SetStopThreshold(DEV_ID_0, FTMT_BOARD_A, FTMT_CHANNEL_0, self.ch1_thresh)
        if rtn == 0:
            self.ft_info_msg.emit("CH1 input threshold is setted to: {}".format(ch1_thresh_str))
        else:
            self.ft_info_msg.emit("Setting CH1 input threshold failed.")

        '''Setting CH2 input threshold'''
        ch2_thresh_str = self.ch2_thresh_ledit.text()
        self.ch2_thresh = ctypes.c_int(int(ch2_thresh_str))
        rtn = self.dev.SetStopThreshold(DEV_ID_0, FTMT_BOARD_A, FTMT_CHANNEL_1, self.ch2_thresh)
        if rtn == 0:
            self.ft_info_msg.emit("CH2 input threshold is setted to: {}".format(ch2_thresh_str))
        else:
            self.ft_info_msg.emit("Setting CH2 input threshold failed.")

        '''Setting CH3 input threshold'''
        ch3_thresh_str = self.ch3_thresh_ledit.text()
        self.ch3_thresh = ctypes.c_int(int(ch3_thresh_str))
        rtn = self.dev.SetStopThreshold(DEV_ID_0, FTMT_BOARD_A, FTMT_CHANNEL_2, self.ch3_thresh)
        if rtn == 0:
            self.ft_info_msg.emit("CH3 input threshold is setted to: {}".format(ch3_thresh_str))
        else:
            self.ft_info_msg.emit("Setting CH3 input threshold failed.")

        '''Setting CH4 input threshold'''
        ch4_thresh_str = self.ch4_thresh_ledit.text()
        self.ch4_thresh = ctypes.c_int(int(ch4_thresh_str))
        rtn = self.dev.SetStopThreshold(DEV_ID_0, FTMT_BOARD_A, FTMT_CHANNEL_3  , self.ch4_thresh)
        if rtn == 0:
            self.ft_info_msg.emit("CH4 input threshold is setted to: {}".format(ch4_thresh_str))
        else:
            self.ft_info_msg.emit("Setting CH4 input threshold failed.")

        self.ft_info_msg.emit('-'*60)

    def ft_smp_ld(self):

        # Check file type
        if self.bin_ckbox.isChecked() or self.txt_ckbox.isChecked():
            if self.bin_ckbox.isChecked():
                rtn = self.dev.SetFileMode(FTMT_TASK_RUN_MODE_T3, FTMT_FILE_SAVE_MODE_BIN, FTMT_FILE_SERIES_MODE_EACH)
                if rtn == 0:
                    self.ft_info_msg.emit('Samples will be saved as *.bin.')
                    #get the chosen file path, return it as a string
                    self.filePath = QFileDialog.getExistingDirectory(
                        self,             # 父窗口对象
                        "Choose FT1040-T3Mode File Path", # 标题
                        r"d:"        # 起始目录
                    )
                    self.ft_file_path_ledit.setText(self.filePath)
                    file_path = ctypes.c_char_p(bytes(self.filePath, encoding='utf-8'))
                    rtn = self.dev.SetFilePath(DEV_ID_0, FTMT_TASK_RUN_MODE_T3, file_path)
                    # self.ft_sample_msg.emit(self.filePath)
                    if rtn ==0:
                        self.ft_info_msg.emit('Samples will be saved in: {}'.format(self.filePath))
                        self.ft_info_msg.emit("-"*60)
                    else:
                        self.ft_info_msg.emit('Setting file path failed.')
                        self.ft_info_msg.emit("-"*60)
                else:
                    self.ft_info_msg.emit('Setting file type failed.')
                    self.ft_info_msg.emit("-"*60)
            elif self.txt_ckbox.isChecked():
                rtn = self.dev.SetFileMode(FTMT_TASK_RUN_MODE_T3, FTMT_FILE_SAVE_MODE_TEXT, FTMT_FILE_SERIES_MODE_EACH)
                if rtn == 0:
                    self.ft_info_msg.emit('Samples will be saved as *.txt.')
                    #get the chosen file path, return it as a string
                    self.filePath = QFileDialog.getExistingDirectory(
                        self,             # 父窗口对象
                        "Choose FT1040-T3Mode File Path", # 标题
                        r"d:"        # 起始目录
                    )
                    self.ft_file_path_ledit.setText(self.filePath)
                    file_path = ctypes.c_char_p(bytes(self.filePath, encoding='utf-8'))
                    rtn = self.dev.SetFilePath(DEV_ID_0, FTMT_TASK_RUN_MODE_T3, file_path)
                    # self.ft_sample_msg.emit(self.filePath)
                    if rtn ==0:
                        self.ft_info_msg.emit('Samples will be saved in: {}'.format(self.filePath))
                        self.ft_info_msg.emit("-"*60)
                    else:
                        self.ft_info_msg.emit('Setting file path failed.')
                        self.ft_info_msg.emit("-"*60)
                else:
                    self.ft_info_msg.emit('Setting file type failed.')
                    self.ft_info_msg.emit("-"*60)
        else:
            self.ft_info_msg.emit('Choose file type first!')

    def file_size_setting(self):

        if self.split_file_btn.isChecked():
            file_size_str = self.file_size_cbx.currentText()
            file_size = ctypes.c_int(int(file_size_str))
            # print(file_size)
            rtn = self.dev.SetMaxFileSize(DEV_ID_0, file_size)
            if rtn == 0:
                self.ft_info_msg.emit("File size is setted to: {}".format(file_size_str))
                self.ft_info_msg.emit("-"*60)
            else:
                self.ft_info_msg.emit("Setting file size failed.")
                self.ft_info_msg.emit("-"*60)

    def open_folder(self):
        os.startfile(self.filePath)

    def enable_tttr_mode(self):

        mask = ''
        mask_list = [
            '0',
            'b',
            str(int(self.ch4_ckbox.isChecked())), 
            str(int(self.ch3_ckbox.isChecked())), 
            str(int(self.ch2_ckbox.isChecked())), 
            str(int(self.ch1_ckbox.isChecked()))
        ]
        mask = mask.join(mask_list)
        if mask == '0b0001':

            '''Enable CH1 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0001)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 TTTR mode failed")

        elif mask == '0b0010':

            '''Enable CH2 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0010)
            if rtn ==0:
                self.ft_info_msg.emit("CH2 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH2 TTTR mode failed")

        elif mask == '0b0100':

            '''Enable CH3 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0100)
            if rtn ==0:
                self.ft_info_msg.emit("CH3 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH3 TTTR mode failed")

        elif mask == '0b1000':

            '''Enable CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1000)
            if rtn ==0:
                self.ft_info_msg.emit("CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH4 TTTR mode failed")

        # Two ports are open
        elif mask == '0b0011':

            '''Enable CH1 CH2 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0011)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH2 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH2 TTTR mode failed")
        
        elif mask == '0b0110':

            '''Enable CH2 CH3 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0110)
            if rtn ==0:
                self.ft_info_msg.emit("CH2 CH3 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH2 CH3 TTTR mode failed")

        elif mask == '0b1100':

            '''Enable CH3 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1100)
            if rtn ==0:
                self.ft_info_msg.emit("CH3 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH3 CH4 TTTR mode failed")

        elif mask == '0b1010':

            '''Enable CH2 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1010)
            if rtn ==0:
                self.ft_info_msg.emit("CH2 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH2 CH4 TTTR mode failed")

        elif mask == '0b0101':

            '''Enable CH1 CH3 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0101)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH3 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH3 TTTR mode failed")

        elif mask == '0b1001':

            '''Enable CH1 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1001)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH4 TTTR mode failed")

        # Three ports are open
        elif mask == '0b0111':

            '''Enable CH1 CH2 CH3 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_0111)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH2 CH3 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH2 CH3 TTTR mode failed")

        elif mask == '0b1011':

            '''Enable CH1 CH2 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1011)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH2 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH2 CH4 TTTR mode failed")

        elif mask == '0b1101':

            '''Enable CH1 CH3 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1101)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH3 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH3 CH4 TTTR mode failed")
        
        elif mask == '0b1110':

            '''Enable CH2 CH3 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1110)
            if rtn ==0:
                self.ft_info_msg.emit("CH2 CH3 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH2 CH3 CH4 TTTR mode failed")
        
        # For ports are open
        elif mask == '0b1111':

            '''Enable CH1 CH2 CH3 CH4 TTTR mode''' 
            rtn = self.dev.EnableTTTR(DEV_ID_0, FTMT_BOARD_A, CH_MASK_1111)
            if rtn ==0:
                self.ft_info_msg.emit("CH1 CH2 CH3 CH4 TTTR mode enabled")
            else:
                self.ft_info_msg.emit("Enable CH1 CH2 CH3 CH4 TTTR mode failed")
        
        self.ft_info_msg.emit('-'*60)

    def time_stop_mode(self):

        if self.time_stp_ckbox.isChecked():
            '''Set time end mode'''
            rtn = self.dev.SetTTTREndMode(FTMT_TTTR_END_MODE_TIME, 0)
            # print(rtn)
            if rtn == 0:
                self.ft_info_msg.emit("Setting to time stop mode")
            else:
                self.ft_info_msg.emit("Setting to time stop mode failed.")

            '''Setting statistic time'''
        
            self.statisticTime = int(self.time_stp_ledit.text())
            self.sTime = ctypes.c_float(self.statisticTime)
            rtn = self.dev.SetStatisticsTime(FTMT_TASK_RUN_MODE_T3, self.sTime)
            if rtn == 0:
                self.ft_info_msg.emit("Statistic time is setted to: {}".format(self.statisticTime))
            else:
                self.ft_info_msg.emit("Setting statistic time failed.")
            self.ft_info_msg.emit('-'*60)

    def event_stop_mode(self):

        '''Setting event end mode'''
        if self.event_stp_ckbox.isChecked():
            self.eCounts = int(self.event_stp_ledit.text())
            rtn = self.dev.SetTTTREndMode(FTMT_TTTR_END_MODE_EVENT, self.eCounts)
            if rtn == 0:
                self.ft_info_msg.emit("Setting to event stop mode, {} counts required.".format(self.eCounts))
            else:
                self.ft_info_msg.emit("Setting to event stop mode failed.")

            self.ft_info_msg.emit('-'*60)

    def ft_ply(self):
        rtn = self.dev.StartTask(FTMT_TASK_RUN_MODE_T3)
        if rtn == 0:
            self.ft_info_msg.emit("Start succeeded.")
        else:
            self.ft_info_msg.emit("Start failed.")
        
        thread = Thread(
            target = self.ft_ply_threadFunc
        )
        thread.start()
        self.ft_ply_btn.setEnabled(False)

        progressBar_thread = Thread(
            target = self.progressBar_threadFunc,
            args = (self.statisticTime,)
        )
        progressBar_thread.start()

    def ft_ply_btn_enable(self,msg):
        if msg == '1':
            self.ft_ply_btn.setEnabled(True)
    def progressBar_setvalue(self,i):

        self.ft_progress_bar.setValue(i)

    '''Define thread function for progress bar and FT1040 play button'''
    def ft_ply_threadFunc(self):    

        while True:
            if self.dev.IsTaskCompleted() ==True:
                rtn = self.dev.StopTask(FTMT_TASK_RUN_MODE_T3)
                self.ft_info_msg.emit('Task completed: {}'.format(rtn))
                self.ft_ply_btn_msg.emit('1')
                break

    def progressBar_threadFunc(self, sTime):
        
        for i in range(0,101):
            time.sleep(sTime/100)
            self.ft_progressBar_msg.emit(i)
           
    '''Set FT1040 info ui'''
    def ft_info_ui(self):

        self.ft_msg.setWordWrap(True)  # 自动换行
        self.ft_msg.setAlignment(Qt.AlignTop)  # 靠上

        # 用于存放消息
        self.ft_msg_history = []

    def ft_slot(self, msg):

        self.ft_msg_history.append(msg)
        self.ft_msg.setText("<br>".join(self.ft_msg_history))
        self.ft_msg.resize(700, self.ft_msg.frameSize().height() + 20)
        self.ft_msg.repaint()  # 更新内容，如果不更新可能没有显示新内容   

    '''Set window ui'''
    def window_btn_signal(self):
        # window button sigmal
        self.close_btn.clicked.connect(self.close)
        self.max_btn.clicked.connect(self.maxornorm)
        self.min_btn.clicked.connect(self.showMinimized)
        
    #create window blur
    def render_shadow(self):
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(0, 0)  # 偏移
        self.shadow.setBlurRadius(30)  # 阴影半径
        self.shadow.setColor(QColor(128, 128, 255))  # 阴影颜色
        self.mainwidget.setGraphicsEffect(self.shadow)  # 将设置套用到widget窗口中

    def maxornorm(self):
        if self.isMaximized():
            self.showNormal()
            self.norm_icon = QIcon()
            self.norm_icon.addPixmap(QPixmap(":/my_icons/images/icons/max.svg"), QIcon.Normal, QIcon.Off)
            self.max_btn.setIcon(self.norm_icon)
        else:
            self.showMaximized()
            self.max_icon = QIcon()
            self.max_icon.addPixmap(QPixmap(":/my_icons/images/icons/norm.svg"), QIcon.Normal, QIcon.Off)
            self.max_btn.setIcon(self.max_icon)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = QPoint
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标
        
    def mouseMoveEvent(self, QMouseEvent):
        m_position = QPoint
        m_position = QMouseEvent.globalPos() - self.pos()
        width = QDesktopWidget().availableGeometry().size().width()
        height = QDesktopWidget().availableGeometry().size().height()
        if m_position.x() < width*0.7 and m_position.y() < height*0.06:
            self.m_flag = True
            if Qt.LeftButton and self.m_flag:                
                pos_x = int(self.m_Position.x())
                pos_y = int(self.m_Position.y())
                if pos_x < width*0.7 and pos_y < height*0.06:           
                    self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
                    QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
    def eventFilter(self, object, event):

        if event.type() == QEvent.HoverMove:
            print('鼠标在按钮上')
            return True
        elif event.type() == QEvent.MouseMove:
            print('按钮被点击')
            return True
        return False
    '''
    RF CONTROL
    '''
    def rf_info_ui(self):

        # create blank message QLabel
        # self.rf_msg = QLabel(" ")
        # self.rf_msg.resize(700, 20)
        self.rf_msg.setWordWrap(True)  # 自动换行
        self.rf_msg.setAlignment(Qt.AlignTop)  # 靠上
        # self.msg.setStyleSheet("background-color: yellow; color: black;")

        # add message QLabel to scroll area
        # self.rf_msg.setParent(self.rf_scroll)
        # scroll_layout = QVBoxLayout()
        # scroll_layout.addWidget(self.rf_scroll)
        # # self.rf_scroll.verticalScrollBarPolicy(self.rf_scroll.maximum())

        # # 用于存放消息
        self.rf_msg_history = []

    def rf_slot(self, msg):

        # print(msg)
        self.rf_msg_history.append(msg)
        self.rf_msg.setText("<br>".join(self.rf_msg_history))
        self.rf_msg.resize(700, self.rf_msg.frameSize().height() + 20)
        self.rf_msg.repaint()  # 更新内容，如果不更新可能没有显示新内容

    def my_rf_signal(self):

        #open button signal
        self.rf_connect_btn.clicked.connect(self.boot_rf)

        #message signal
        self.rf_info_msg.connect(self.rf_slot)

        # RF scroll area scrollbar signal
        self.rf_scroll.verticalScrollBar().rangeChanged.connect(
            lambda: self.rf_scroll.verticalScrollBar().setValue(
                self.rf_scroll.verticalScrollBar().maximum()
            )
        )

        # combobox restore signal
        self.rf_visa_rst_btn.clicked.connect(self.rf_cbx_test)

        # RF load sample button signal
        self.rf_load_btn.clicked.connect(self.rf_spl_ld)

        # RF On button signal
        self.rf_ply_stp_btn.clicked.connect(self.rf_ply_stp)

    def rf_cbx_test(self):
        
        self.rf_cbx.clear()
        self.rm = pyvisa.ResourceManager()
        self.ls = self.rm.list_resources()
        self.rf_cbx.addItems(self.ls)

    def boot_rf(self):
        
        # Boot RF generator
        self.rf_port = self.rf_cbx.currentText()
        print(self.rf_port)
        self.my_instrument = self.rm.open_resource(self.rf_port)
        self.my_instrument.write_termination = '\n'
        self.instrument_info = self.my_instrument.query('*IDN?')
        
        # 恢复出厂设置
        self.fac = self.my_instrument.write(':SYST:PRES:TYPE FAC')
        
        self.preset = self.my_instrument.write(':SYST:PRES')
        
        if self.fac != 0 and self.preset != 0:
            self.rf_info_msg.emit('Restored factory settings succeeded: {}, {}'.format(self.fac, self.preset))
        else:
            self.rf_info_msg.emit('Restoring factory settings failed')
            sys.emit()

        self.rf_info_msg.emit(self.instrument_info)
        
        '''
        This part defines some initial settings of RF generator suited to CW-ODMR measurement
        '''
        # time.sleep(5)

        # setting sweep type to list
        sweep_type = self.my_instrument.write(":SWE:TYPE LIST")
        if sweep_type != 0:
            self.rf_info_msg.emit('Setting sweep type to "LIST" succeeded: {}'.format(sweep_type))
        else:
            self.rf_info_msg.emit('Setting sweep type "LIST" failed')
            sys.emit()

        # setting file type to sweep csv
        file_type = self.my_instrument.write(":MMEM:FILE SWPCsv")
        if file_type != 0:
            self.rf_info_msg.emit('Setting file type to "SWPCsv" succeeded: {}'.format(file_type))
        else:
            self.rf_info_msg.emit('Setting file type "SWPCsv" failed')
            sys.emit()
        
        # setting sweep mode to continue
        sweep_mode = self.my_instrument.write(":SWE:MODE CONT")
        if sweep_mode != 0:
            self.rf_info_msg.emit('Setting sweep mode to "CONTinue" succeeded: {}'.format(sweep_mode))
        else:
            self.rf_info_msg.emit('Setting sweep mode to "CONTinue"failed')
            sys.emit()
        
        # setting period trigger type to auto
        pe_sweep_trig = self.my_instrument.write(":SWE:SWE:TRIG:TYPE AUTO")
        if pe_sweep_trig != 0:
            self.rf_info_msg.emit('Setting period trigger type TO "AUTO" succeeded: {}'.format(pe_sweep_trig))
        else:
            self.rf_info_msg.emit('Setting period trigger type "AUTO" failed')
            sys.emit()

        #setting poit trigger type to external
        pt_sweep_trig = self.my_instrument.write(":SWE:POIN:TRIG:TYPE EXT")
        if pt_sweep_trig != 0:
            self.rf_info_msg.emit('Setting point trigger type to "EXT" succeeded: {}'.format(pt_sweep_trig))
        else:
            self.rf_info_msg.emit('Setting point trigger type "EXT" failed')
            sys.emit()

        # setting triger_slope to positive
        trig_slope = self.my_instrument.write(":INP:TRIG:SLOP POS ")
        if trig_slope != 0:
            self.rf_info_msg.emit('Setting trigger slope to "Positive" succeeded: {}'.format(trig_slope))
        else:
            self.rf_info_msg.emit('Setting trigger slope to "Positive" failed')
            sys.emit()

        # setting sweep state to level and frequency
        sweep_state = self.my_instrument.write(":SWE:STAT LEV,FREQ")
        if sweep_state != 0:
            self.rf_info_msg.emit('Setting sweep state to "Level and Frequency" succeeded: {}'.format(sweep_state))
        else:
            self.rf_info_msg.emit('Setting sweep state to "Level and Frequency" failed')
            sys.emit()

    def rf_spl_ld(self):

        sample = self.rf_sample_ledit.text()
        load_status = self.my_instrument.write(':MMEMory:LOAD E:\RF_freqSW_list\cw_odmr\{}.csv'.format(sample))
        if load_status != 0:
            self.rf_info_msg.emit('Loading SWPcsv list sample succeeded: {}'.format(load_status))
        else:
            self.rf_info_msg.emit('Loading SWPcsv list sample failed')

    def rf_ply_stp(self):
        output_status = self.my_instrument.query(':OUTP?')
        if output_status == '0\n':
            
            self.rf_ply_stp_btn.setText('RF OFF')
            self.off_icon = QIcon()
            self.off_icon.addPixmap(QPixmap(":/my_icons/images/icons/stop.svg"), QIcon.Normal, QIcon.Off)
            self.rf_ply_stp_btn.setIcon(self.off_icon)
            rtn = self.my_instrument.write(":OUTP ON")
            if rtn != 0:
                self.rf_info_msg.emit('RF ON succeeded: {}'.format(rtn))
            else:
                self.rf_info_msg.emit('RF ON failed')
                sys.emit()
        elif output_status == '1\n':
            self.rf_ply_stp_btn.setText('RF ON  ')
            self.on_icon = QIcon()
            self.on_icon.addPixmap(QPixmap(":/my_icons/images/icons/play.svg"), QIcon.Normal, QIcon.Off)
            self.rf_ply_stp_btn.setIcon(self.on_icon)
            rtn = self.my_instrument.write(":OUTP OFF")
            if rtn != 0:
                self.rf_info_msg.emit('RF OFF succeeded: {}'.format(rtn))
            else:
                self.rf_info_msg.emit('RF OFF failed')
                sys.emit()
    
    '''
    ASG CONTROL
    '''
    

if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    app.exec()
