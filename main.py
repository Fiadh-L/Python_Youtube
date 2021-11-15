import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from lib.you_view_layout import Ui_MainWindow
from PyQt5 import QtWebEngineWidgets
import re
import datetime

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #초기 잠금
        self.initAuthLock() #인증버튼

if __name__=="__main__":
    app=QApplication(sys.argv)
    you_view_main=Main()
    you_view_main.show()
    app.exec()
