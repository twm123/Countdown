#Countdown - Clock display with elapsed/remaining time
#Author - Tyler Medlin
#
import os
import sys
import threading
import time
import operator
import countdown_qrc_rc

from datetime import datetime, timedelta
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QImage, QPalette, QBrush

#QT UI Resource
display_ui = "time_display_ui.ui" # Enter file here.
control_ui = "controller_display_ui.ui" # Enter file here.
Ui_DisplayWindow, QtBaseClass = uic.loadUiType(display_ui)
Ui_ControlWindow, QtBaseClass2 = uic.loadUiType(control_ui)

#Time format
TIME_FMT = '%H:%M:%S'
MAX_BLINK = 3


#Thread for updating the clock text field
class TimeThread(QtCore.QThread):
    time_upd = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        THREAD_RUNNING = True
        while THREAD_RUNNING == True:
            time.sleep(.5) #Sleep for 500 milliseconds so that there isn't an unncessary CPU load
            self.time_upd.emit((datetime.now().strftime(TIME_FMT)))


class TimerDisplay(QtWidgets.QMainWindow, Ui_DisplayWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_DisplayWindow.__init__(self)

        #UI Initialization
        self.setupUi(self)
        self.min_label.setAlignment(QtCore.Qt.AlignRight)
        self.clock_text.setAlignment(QtCore.Qt.AlignRight)
        self.elapsed_text.setAlignment(QtCore.Qt.AlignRight)
        self.remaining_text.setAlignment(QtCore.Qt.AlignRight)

        self.setWindowIcon(QtGui.QIcon('countdown_icon.png'))
        self.setWindowTitle('Countdown Display')

        self.fullscreen = False




class ControlDisplay(QtWidgets.QMainWindow, Ui_ControlWindow):
    def __init__(self):
        #initialize the control display
        QtWidgets.QMainWindow.__init__(self)
        Ui_ControlWindow.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowIcon(QtGui.QIcon('countdown_icon.png'))
        self.setWindowTitle('Countdown Control')
        self.oldPos = ''
        self.mousePosX = ''
        self.update_history('')

        #Set up background image
        oImage = QImage("control_bg_img.jpg")
        sImage = oImage.scaled(QSize(570,250))                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))
        self.setPalette(palette)

        #init start/stop times
        self.start_time = ''
        self.stop_time = ''
        self.current_time = ''
        self.blink_count = 0
        self.pause_flag = False
        self.counting = False
        self.previous_time = datetime.now().strftime(TIME_FMT)
        #spawn the background thread for updating the current time
        self.timekeeper_thread = TimeThread()
        self.timekeeper_thread.start()

        #Build time display window
        self.timeDisplay = TimerDisplay()
        self.timeDisplay.show()

        #Set up slot to receive incoming time data
        self.timekeeper_thread.time_upd.connect(self.update_time)
        self.startButton.clicked.connect(self.set_countdown)
        self.resetButton.clicked.connect(self.reset)
        self.deleteButton.clicked.connect(self.delete_history)
        self.fullscreenButton.clicked.connect(self.toggle_fullscreen)
        self.exitButton.clicked.connect(self.exit_click)
        self.history_display.itemClicked.connect(self.set_time)

    def set_time(self, time):
        hour = int(time.text().split(':')[0])
        minute = int(time.text().split(':')[1])
        second = int(time.text().split(':')[2])
        self.hr_box.setValue(hour)
        self.min_box.setValue(minute)
        self.sec_box.setValue(second)


    def delete_history(self):
        filename = os.path.expanduser('~\Documents\history.txt')
        #filename = 'history.txt'
        f = open(filename, 'w+')
        f.close()
        self.history_display.clear()

    def update_history(self, time):

        time_found = False
        filename = os.path.expanduser('~\Documents\history.txt')
        if os.path.isfile(filename) == False:
            f = open(filename, 'w+')
            f.close()
        if time == '':
            time_found = True
        lines = [line.rstrip('\n') for line in open(filename)]
        write_lines = []
        if len(lines) > 0:
            for line in lines:
                if len(line.split('!')) > 1:
                    if time == line.split('!')[1]:
                        line = (str(1 + int(line.split('!')[0])) + '!' + line.split('!')[1])
                        write_lines.append(line)
                        time_found = True
                    else:
                        write_lines.append(line)

        f = open(filename, 'w+')
        f.close()
        f = open(filename, 'a')

        if time_found == False and len(write_lines) < 6:
                write_lines.append('1!' + time)

        indexed_write_lines = []
        for line in write_lines:
            indexed_write_lines.append([int(line.split('!')[0]), line])

        indexed_write_lines.sort(reverse = True)

        self.history_display.clear()
        first = True
        for line in indexed_write_lines:
            if first == True:
                self.history_display.addItem(line[1].split('!')[1])
                f.write(line[1])
                first = False
            else:
                self.history_display.addItem(line[1].split('!')[1])
                f.write('\n' + line[1])
        f.close()

    def update_time(self, time):
        temp_time = time
        self.previous_time = self.current_time
        self.current_time = datetime.strptime(time, TIME_FMT)

        if self.start_time != '':
            if self.pause_flag == False:
                elapsed_time = str(self.current_time - self.start_time).split('.',2)[0]
                remaining_time = str(self.stop_time - self.current_time).split('.',2)[0]

                self.clock_text.setText(temp_time)
                self.elapsed_text.setText(elapsed_time)

                self.timeDisplay.clock_text.setText(temp_time)
                self.timeDisplay.elapsed_text.setText(elapsed_time)


                if self.current_time < self.stop_time:
                    self.remaining_text.setText(remaining_time)
                    self.timeDisplay.remaining_text.setText(remaining_time)
                elif self.remaining_text.text() == '0:00:00' and self.blink_count < MAX_BLINK:
                    self.remaining_text.setText('')
                    self.timeDisplay.remaining_text.setText('')
                    self.blink_count += 1
                    self.counting = False
                else:
                    self.remaining_text.setText('0:00:00')
                    self.timeDisplay.remaining_text.setText('0:00:00')
            else:
                self.start_time += (self.current_time - self.previous_time)
                self.stop_time += (self.current_time - self.previous_time)
                self.clock_text.setText(temp_time)
                self.timeDisplay.clock_text.setText(temp_time)

        else:
            self.clock_text.setText(temp_time)
            self.timeDisplay.clock_text.setText(temp_time)

    def set_countdown(self):
        #If counting down and not paused - PAUSE
        if self.counting == True and self.pause_flag == False:
                self.pause_flag = True
                self.counting = False

        #else if not counting down and not paused - SETSTART
        elif self.counting == False and self.pause_flag == False:
            self.start_time = self.current_time
            countdown_seconds = (self.hr_box.value()*(60**2)) + (self.min_box.value()*60) + self.sec_box.value()
            hr_str = str(self.hr_box.value())
            min_str = ''
            sec_str = ''

            if self.min_box.value() < 10:
                min_str = ('0' + str(self.min_box.value()))
            else:
                min_str = str(self.min_box.value())

            if self.sec_box.value() < 10:
                sec_str = ('0' + str(self.sec_box.value()))
            else:
                sec_str = str(self.sec_box.value())

            time_string = hr_str + ':' + min_str + ':' + sec_str

            self.update_history(time_string)
            self.stop_time = self.start_time + timedelta(seconds = countdown_seconds)
            self.blink_count = 0
            self.counting = True

        #else if not counting and paused - START
        elif self.counting == False and self.pause_flag == True:
            self.pause_flag = False
            self.counting = True

    def reset(self):
        self.start_time = ''
        self.stop_time = ''
        self.elapsed_text.setText('0:00:00')
        self.remaining_text.setText('0:00:00')
        self.timeDisplay.elapsed_text.setText('0:00:00')
        self.timeDisplay.remaining_text.setText('0:00:00')
        self.counting = False
        self.pause_flag = False

    def toggle_fullscreen(self):
        if self.timeDisplay.fullscreen == False:
            self.timeDisplay.showFullScreen()
            self.timeDisplay.fullscreen = True
        else:
            self.timeDisplay.showNormal()
            self.timeDisplay.fullscreen = False

    def exit_click(self):
        QtCore.QCoreApplication.instance().quit()

    def mousePressEvent(self, event):
        if event.y() < 30:
            self.oldPos = event.globalPos()
            self.mousePosX = event.x()
        else:
            self.oldPos = None

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.oldPos = None

    def mouseMoveEvent(self, event):
        if self.oldPos != None:
            delta = QtCore.QPoint (event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

def main():
    app = QtWidgets.QApplication(sys.argv)
    control_window = ControlDisplay()
    control_window.show()

    sys.exit(app.exec_())

#main thread duties
if __name__ == "__main__":
    main()
