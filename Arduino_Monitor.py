#coding: UTF-8
from threading import Thread
import time
import serial

last_received = ''


def receiving(ser):
    global last_received
    buffer = ''
    while True:
        buffer += ser.read(ser.inWaiting())
        if '\n' in buffer:
            lines = buffer.split('\n')  # Guaranteed to have at least 2 entries
            last_received = lines[-2]
            # If the Arduino sends lots of empty lines, you'll lose the
            # last filled line, so you could make the above statement conditional
            # like so: if lines[-2]: last_received = lines[-2]
            buffer = lines[-1]


class SerialData(object):
    def __init__(self, port='com4', baudrate=9600, bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                 timeout=0.1, xonxoff=0, rtscts=0):
        """
        :param port: 端口
        :param baudrate: 波特率(1200/2400/4800/9600/19200/38400/57600/115200/230400/460800/921600)
        :param bytesize: 数据位(FIVEBITS;SIXBITS;SEVENBITS;EIGHTBITS)
        :param parity:校验(PARITY_NONE/ODD/EVEN/MARK/NAMES/SPACE)
        :param stopbits:停止位(STOPBITS_ONE/STOPBITS_ONE_POINT_FIVE/STOPBITS_TWO)
        :param timeout:超时
        :param xonxoff:
        :param rtscts:
        :param interCharTimeout:
        :return:
        """
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
                xonxoff=xonxoff,
                rtscts=rtscts)
        except serial.serialutil.SerialException:
            # no serial connection
            self.ser = None
        else:
            Thread(target=receiving, args=(self.ser,)).start()
        
    def next(self):
        if not self.ser:
            return 100      # return anything so we can test when Arduino isn't connected
        #return a float value or try a few times until we get one
        for i in range(40):
            raw_line = last_received
            try:
                return float(raw_line.strip())
            except ValueError:
                print 'bogus data', raw_line
                time.sleep(.005)
        return 0.

    def __del__(self):
        if self.ser:
            self.ser.close()

if __name__ == '__main__':
    s = SerialData()
    for i in range(500):
        time.sleep(.015)
        print s.next()
