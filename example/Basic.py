import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from pyqu_ui import Ui_MainWindow

#form_class = uic.loadUiType('D:/Python_App/Python_Youtube/pyqt_youtube.ui')[0]

class TestForm(QMainWindow, Ui_MainWindow): #TestForm(QMainWindow, form_class):
    def __init__(self): #init 생성
        super().__init__() #super 최상위
        self.setupUi(self)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestForm() #창띄우/
    window.show()
    app.exec_()
