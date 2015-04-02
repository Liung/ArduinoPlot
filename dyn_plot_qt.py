#coding: UTF-8
import serial
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import \
    FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QTAgg as NavigationToolbar
import numpy as np
import pylab
from Arduino_Monitor import SerialData as DataGen

from dyn_plot_ui import Ui_MainWindow


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        self.set_port()
        self.update_port()

        self.paused = False

        self.init_plot()
        self.canvas = FigureCanvas(self.fig)
        self.navToolbar = NavigationToolbar(self.canvas,
                                            self.graphFrame)
        # self.canvas.setParent(self.graphFrame)
        self.graphLayout.addWidget(self.canvas)
        self.graphLayout.addWidget(self.navToolbar)
        # self.canvas.setSizePolicy(QSizePolicy.Expanding,
        #                           QSizePolicy.Expanding)
        # self.canvas.updateGeometry()
        self.draw_plot()

        self.cbPort.currentIndexChanged.connect(self.update_port)
        self.cbBaudrate.currentIndexChanged.connect(self.update_port)
        self.cbBytesize.currentIndexChanged.connect(self.update_port)
        self.cbParity.currentIndexChanged.connect(self.update_port)
        self.cbStopbits.currentIndexChanged.connect(self.update_port)
        self.spbTimeout.valueChanged.connect(self.update_port)
        self.btnDefault.clicked.connect(self.on_btnDefault_clicked)
        self.btnPause.clicked.connect(self.on_btnPause_clicked)
        self.btnPause.clicked.connect(self.on_update_btnPause_clicked)
        self.chbGrid.stateChanged.connect(self.on_chbGrid_stateChanged)
        self.chbXlabel.stateChanged.connect(self.on_chbXlabel_stateChanged)

        self.redraw_timer = QTimer(self)
        self.redraw_timer.timeout.connect(self.on_redraw_timer)
        self.redraw_timer.start(100)

    def set_port(self):
        # 设置端口
        self.cbPort.setCurrentIndex(4)
        self.cbBaudrate.addItems([str(baudrate) for baudrate in serial.Serial.BAUDRATES])
        self.cbBaudrate.setCurrentIndex(12)     # 9600
        self.cbBytesize.addItems([str(bytesize) for bytesize in serial.Serial.BYTESIZES])
        self.cbBytesize.setCurrentIndex(3)      # 8
        self.cbParity.addItems([str(parity) for parity in serial.Serial.PARITIES])
        self.cbParity.setCurrentIndex(0)        # None
        self.cbStopbits.addItems([str(stopbits) for stopbits in serial.Serial.STOPBITS])
        self.cbStopbits.setCurrentIndex(0)      # 1

        self.spbTimeout.setValue(0.01)

    def update_port(self):
        self.port = self.cbPort.currentIndex()
        self.baudrate = serial.Serial.BAUDRATES[self.cbBaudrate.currentIndex()]
        self.bytesize = serial.Serial.BYTESIZES[self.cbBytesize.currentIndex()]
        self.parity = serial.Serial.PARITIES[self.cbParity.currentIndex()]
        self.stopbits = serial.Serial.STOPBITS[self.cbStopbits.currentIndex()]
        self.timeout = self.spbTimeout.value()

        self.datagen = DataGen(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize,
                               parity=self.parity, stopbits=self.stopbits,
                               timeout=self.timeout)

        self.data = [self.datagen.next()]

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((8.0, 6.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Arduino Serial Data', size=12)

        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference
        # to the plotted line series
        #
        self.plot_data = self.axes.plot(
            self.data,
            linewidth=1,
            color=(1, 1, 0),
        )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.rbXmaxAuto.isChecked():
            xmax = len(self.data) if len(self.data) > 50 else 50
        else:
            xmax = float(self.XmaxManu.value())

        if self.rbXminAuto.isChecked():
            xmin = xmax - 50
        else:
            xmin = float(self.XminManu.value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        #
        # note that it's easy to change this scheme to the
        # minimal/maximal value in the current display, and not
        # the whole data set.
        #
        if self.rbYminAuto.isChecked():
            ymin = round(min(self.data), 0) - 1
        else:
            ymin = int(self.YminManu.value())

        if self.rbYmaxAuto.isChecked():
            ymax = round(max(self.data), 0) + 1
        else:
            ymax = int(self.YmaxManu.value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.chbGrid.isChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly
        # iterate, and setp already handles this.
        #
        pylab.setp(self.axes.get_xticklabels(),
                   visible=self.chbXlabel.isChecked())

        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))

        self.canvas.draw()

    def on_btnDefault_clicked(self):
        self.set_port()
        self.update_port()

    def on_btnPause_clicked(self):
        self.paused = not self.paused

    def on_update_btnPause_clicked(self):
        label = u"继续" if self.paused else u"暂停"
        self.btnPause.setText(label)

    def on_chbGrid_stateChanged(self):
        self.draw_plot()

    def on_chbXlabel_stateChanged(self):
        self.draw_plot()

    def on_redraw_timer(self):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if not self.paused:
            self.data.append(self.datagen.next())

        self.draw_plot()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    app.exec_()