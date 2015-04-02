##ArduinoPlot##
ArduinoPlot是在原作者的基础上进行了改进设计。

###主要改动###
- 使用PyQt4模块，替换原来的wxPython模块
- 允许改变端口参数，相比较原版本的文件内置端口，这点是一个相当灵活的改动

### 原版本Read Me ###
Shows a plot of numeric lines sent to serial port. 
(set up for com4 right now, change in the code if neded)

Install the following to run it:

Python 2.6 (2.5 should probably work too)
pyserial
wx
matplotlib
numpy
pylab

To use, simply run:
python wx_mpl_dynamic_graph.py

from the command line.

Note: Make sure you have your Arduino IDE closed, or it will block other programs
like this one from using the serial port.
