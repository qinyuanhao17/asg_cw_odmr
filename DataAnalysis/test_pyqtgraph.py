from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

# 创建 绘制窗口类 PlotWindow 对象，内置一个绘图控件类 PlotWidget 对象
pw = pg.plot()

# 设置图表标题、颜色、字体大小
pw.setTitle("气温趋势",size='12pt')

# 背景色改为白色
pw.setBackground('w')

# 显示表格线
pw.showGrid(x=True, y=True)

# 设置上下左右的label
# 第一个参数 只能是 'left', 'bottom', 'right', or 'top'
pw.setLabel("left", "气温(摄氏度)")
pw.setLabel("bottom", "时间")

# 设置Y轴 刻度 范围
pw.setYRange(min=-10,  # 最小值
             max=50)  # 最大值

# 创建 PlotDataItem ，缺省是曲线图
curve = pw.plot( pen=pg.mkPen('b')) # 线条颜色

hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

curve.setData(hour, # x坐标
              temperature  # y坐标
              )

QApplication.instance().exec_()