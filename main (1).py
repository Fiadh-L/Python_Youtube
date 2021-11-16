import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QUrl, QThread
from PyQt5 import uic
from lib.You_View_Layout import Ui_MainWindow
from lib.AuthDialog import AuthDialog
from lib.IntroWorker import IntroWorker
from PyQt5 import QtWebEngineWidgets
import re
import datetime
from pytube import YouTube
import pytube
from PyQt5.QtMultimedia import QSound

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        #UI초기화
        self.setupUi(self)
        #초기 잠금(인증안된상태)
        self.initAuthLock() #인증 버튼
        #t시그널
        self.initSignal()
        #로그인 관련 변수 선언
        self.user_id = None
        self.user_pw = None
        #재생 여부
        self.is_play=False
        #Youtube 관련 작업
        self.youtb = None
        self.youtb_fsize = 0
        #배경음악 Thread 작업 선언
        self.initIntroThread()
        #Qthread 사용
        #QSound.play("D:/Bigpy_Pro/resource/intro.wav")


    #기본 UI 비활성화
    def initAuthLock(self):
        self.previewButton.setEnabled(False)
        self.fileNavButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.streamCombobox.setEnabled(False)
        self.calendarWidget.setEnabled(False)
        self.urlTextEdit.setEnabled(False)
        self.pathTextEdit.setEnabled(False)
        self.showStatusMsg('인증안됨')

    #기본 UI 활성화
    def initAuthActive(self):
        self.previewButton.setEnabled(True)
        self.fileNavButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.streamCombobox.setEnabled(True)
        self.calendarWidget.setEnabled(True)
        self.urlTextEdit.setEnabled(True)
        self.pathTextEdit.setEnabled(True)
        self.showStatusMsg('인증완료')

    def showStatusMsg(self, msg):
        self.statusbar.showMessage(msg)

    #인증 시그널 초기화
    def initSignal(self): #인터페이스라고 생각해주면 됨
        self.loginButton.clicked.connect(self.authCheck)
        self.previewButton.clicked.connect(self.load_url)
        #종료버튼
        self.endButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        #로딩바
        self.webEngineView.loadProgress.connect(self.showProgressBrowserLoading)
        #저장하기
        self.fileNavButton.clicked.connect(self.selectDownPath)
        #달력 구현
        self.calendarWidget.clicked.connect(self.append_date)
        #스타트 버튼 구현
        self.startButton.clicked.connect(self.downloadYoutb)

    #인트로 쓰레드 초기화 및 활성화
    def initIntroThread(self):
        #Worker 선언
        self.introObj=IntroWorker()
        #Qthread 선언
        self.introThread=QThread()
        #QObject를 상속받았으므로 moveToThread메소드 사용 가능 즉 Worker To thread로 변환 작업
        self.introObj.moveToThread(self.introThread)
        #시그널 연결
        self.introObj.startMsg.connect(self.showIntroInfo)
        #Thread 시작 메소드 연결
        self.introThread.started.connect(self.introObj.playBgm)
        #Thread 스타트
        self.introThread.start()

    #인트로 쓰레드 Signal 실행
    def showIntroInfo(self, msg, filename):
        self.plainTextEdit.appendPlainText("Program Started by : " + msg)
        self.plainTextEdit.appendPlainText("Playing intoro infomation id  : " + filename)

    @pyqtSlot() #명시적 표현
    def authCheck(self):
        #print('login test commit')
        dlg=AuthDialog()
        dlg.exec_()
        #위젯에 있는 id,pw가 넘어옴
        self.user_id = dlg.user_id
        self.user_pw = dlg.user_pw
        print("id: %s pw: %s" % (self.user_id, self.user_pw))

        #DB연동 또는 서버 연동 코드

        if True : #강제로 아이디 비번 모두 맞게 선언
            self.initAuthActive() #로그인 후 모두 활성화
            self.loginButton.setText("Logout")
            self.loginButton.setEnabled(False) #인증버튼 1회 사용후 잠금
            self.urlTextEdit.setFocus(True) #커서 이동
            self.append_log_msg("login Success") #로그기록 쓰기
        else:
            QMessageBox.about(self, "인증오류", "아이디 비밀번호를 확인하세요!")

    def load_url(self):
        url=self.urlTextEdit.text().strip()
        v=re.compile('^https://www.youtube.com/watch?')
        if self.is_play: #재생중일때 멈춤
            self.append_log_msg('Stop Click')
            self.webEngineView.load(QUrl('about:blank')) #about:blank: 빈페이지로 초기화
            self.previewButton.setText("Play")
            self.is_play=False
            self.urlTextEdit.clear()
            self.urlTextEdit.setFocus(True)
            self.startButton.setEnabled(False)
            self.streamCombobox.clear() #저장완료시(또는 중지시) 초기화
            self.progressBar_2.setValue(0)  #다운로드 완료시 초기화
            self.showStatusMsg("인증완료")

        else : #재생전이므로 재생가능하도록 구현
            if v.match(url) is not None:
                self.append_log_msg('Play Click')
                self.webEngineView.load(QUrl(url))

                #상태표시줄
                self.showStatusMsg(url + " 재생중")
                self.previewButton.setText("중지")
                self.is_play=True
                self.startButton.setEnabled(True)
                self.initialYouWork(url)
            else:
                QMessageBox.about(self, "URL 형식오류","Youtube 주소형식이 다름니다.")
                self.urlTextEdit.clear()
                self.urlTextEdit.setFocus(True)

    def initialYouWork(self,url):
        video_list = pytube.YouTube(url)
        #로딩바 계산 (register_on_progress_callback:pytube에서 제공)
        video_list.register_on_progress_callback(self.showProgressDownLoading)
        #self.youtb = video_list.streams.all()
        self.youtb = video_list.streams
        self.streamCombobox.clear() #streamCombobox 초기화
        for i,q in enumerate(self.youtb.all()):
            print(i, ":", q)
            #print('step1 : ',q.itag,q.mime_type,q.abr)
            tmp_list, str_list = [], []
            #1차 가공
            tmp_list.append(str(q))
            '''
            tmp_list.append(str(q.itag or ''))
            tmp_list.append(str(q.mime_type or ''))
            tmp_list.append(str(q.res or ''))
            tmp_list.append(str(q.fps or ''))
            tmp_list.append(str(q.vcodec or ''))
            tmp_list.append(str(q.acodec or ''))
            tmp_list.append(str(q.progressive or ''))
            tmp_list.append(str(q.type or ''))
            '''
            #print('step_2',tmp_list)
            #2차 가공
            str_list = [x for x in tmp_list if x != ''] #Python Generator
            #print('step3',str_list)
            #print('join',','.join(str_list))
            self.streamCombobox.addItem(','.join(str_list))


    def append_log_msg(self, act): #act => "login Success"
        now=datetime.datetime.now()
        nowDatetime=now.strftime('%Y-%m-%d %H:%M:%S')
        app_msg=self.user_id + ' : '+act+'-->('+ nowDatetime +')'
        #print(app_msg)
        self.plainTextEdit.appendPlainText(app_msg) #insertPlaintext
        #활동 로그 저장 (DB를 사용 추#)
        with open('D:/Python_App/Python_Youtube/log/log.txt', 'a') as f:
            f.write(app_msg+'\n')

    @pyqtSlot(int) #진행율을 int로 받음
    def showProgressBrowserLoading(self, v):
        self.progressBar.setValue(v)

    @pyqtSlot()
    def selectDownPath(self):
        #print('save test')
        #경로 선택
        fpath=QFileDialog.getExistingDirectory(self, 'Select Directory')
        self.pathTextEdit.setText(fpath)

    @pyqtSlot()
    def append_date(self):
        cur_date=self.calendarWidget.selectedDate()
        #print('cur_date : ', cur_date)
        #년 월 일 출력
        print(str(cur_date.year()) +'-'+str(cur_date.month())+'-'+str(cur_date.day()))
        Calender_msg='Calendar Click ('+str(cur_date.year()) +'-'+str(cur_date.month())+'-'+str(cur_date.day())+')'
        self.append_log_msg(Calender_msg)
        #self.append_log_msg('Calendar Click')

    @pyqtSlot()
    def downloadYoutb(self):
        down_dir = self.pathTextEdit.text().strip() #strip():공백제거
        if down_dir is None or down_dir == '' or not down_dir:
            QMessageBox.about(self,'경로 선택','다운로드 받을 경로를 선택하세요.')
            return None

        self.youtb_fsize = self.youtb[self.streamCombobox.currentIndex()].filesize
        print('fsize : ',self.youtb_fsize)
        self.youtb[self.streamCombobox.currentIndex()].download(down_dir)
        self.append_log_msg('Download Click')
         # 100->90->80->70->60...

    # def showProgressDownLoading(self, stream, chunk, bytes_remaining):
    #      print(int(self.youtb_fsize - bytes_remaining))
    #      print('bytes_remaining',bytes_remaining)
    #      self.progressBar_2.setValue(int(((self.youtb_fsize - bytes_remaining) / self.youtb_fsize) * 100))

    def showProgressDownLoading(self, stream, chunk, bytes_remaining): #stream, chunk, bytes_remaining: 서버 레지스트리에서 주는거라고함.
        #bytes_remaining: 서버 레지스트리에서 주는 현재 다운받기에서 남은 용량
        print(int(self.youtb_fsize - bytes_remaining))
        print('bytes_remaining',bytes_remaining)
        self.progressBar_2.setValue(int(((self.youtb_fsize - bytes_remaining) / self.youtb_fsize) * 100))

if __name__=="__main__":
    app=QApplication(sys.argv)
    you_viewer_main=Main()
    you_viewer_main.show()
    app.exec_()
