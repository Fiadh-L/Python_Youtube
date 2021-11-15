import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from lib.you_view_layout import Ui_MainWindow
from PyQt5 import QtWebEngineWidgets
from lib.AuthDialog import AuthDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import re
import datetime

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #초기 잠금
        self.initAuthLock() #인증버튼
        #시그널 초기화되는 메서드 선언
        self.initSignal()
        #로그인 관련 변수 선언
        self.user_id = None
        self.user_pw = None

    def initAuthLock(self):
        self.previewButton.setEnabled(False)
        self.fileNavButton.setEnabled(False)
        self.streamCombobox.setEnabled(False)
        self.startButton.setEnabled(False)
        self.calendarWidget.setEnabled(False)
        self.urlTextEdit.setEnabled(False)
        self.pathTextEdit.setEnabled(False)
        self.showStatusMsg('인증안됨')

    #기본 UI 활성화
    def initAuthActive(self):
        self.previewButton.setEnabled(True)
        self.fileNavButton.setEnabled(True)
        self.streamCombobox.setEnabled(True)
        self.calendarWidget.setEnabled(True)
        self.urlTextEdit.setEnabled(True)
        self.pathTextEdit.setEnabled(True)
        self.showStatusMsg('인증 완료')

    #시그널 초기화
    def initSignal(self):
        self.loginButton.clicked.connect(self.authCheck)

    @pyqtSlot() #명시적 표현
    def authCheck(self):
        dlg = AuthDialog()
        dlg.exec_()
        self.user_id = dlg.user_id
        self.user_pw = dlg.user_pw

        print("id :  %s password : %s" %(self.user_id, self.user_pw))

        if True: # 강제로 아이디 비번 모두 맞게 선언
            self.initAuthActive() #로그인후 모두 활성화
            self.loginButton.setText("인증완료")
            self.loginButton.setEnabled(False) #인증버튼 1회 사용후 잠금
            self.urlTextEdit.setFocus(True) #커서 자동 이동
        else:
            QMessageBox.about(self, "인증오류", "아이디 또는 비밀번호 인증 오류")

    def showStatusMsg(self,msg): #self는 java의 this와 같으니까 신경쓰지마!
        self.statusbar.showMessage(msg) #상태바에 메시지 띄워!

if __name__=="__main__":
    app=QApplication(sys.argv)
    you_view_main=Main()
    you_view_main.show()
    app.exec()
