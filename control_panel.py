import sys
import os
import time
import platform
import struct
import socket
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from awg4100 import AwgDevice
import asg_cw_odmr_ui
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QMouseEvent, QColor, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtWidgets import QWidget, QApplication, QGraphicsDropShadowEffect, QVBoxLayout, QLabel, QFileDialog, QDesktopWidget

class MyWindow(asg_cw_odmr_ui.Ui_Form, QWidget):

    rf_info_msg = pyqtSignal(str)

    def __init__(self):

        super().__init__()

        # init UI
        self.setupUi(self)
        ui_width = int(QDesktopWidget().availableGeometry().size().width()*0.65)
        ui_height = int(QDesktopWidget().availableGeometry().size().height()*0.72)
        self.resize(ui_width, ui_height)
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
        
        self.m_flag = True
        if Qt.LeftButton and self.m_flag:
            
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

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
        self.rf_msg.resize(700, self.awg_info_msg.frameSize().height() + 20)
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
