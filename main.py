import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import uic
from lib.You_View_Layout import Ui_MainWindow
from lib.AuthDialog import AuthDialog
from PyQt5 import QtWebEngineWidgets
import re
import datetime
from pytube import YouTube
import pytube

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
        #재생여부
        self.is_play=False
        #Youtube 관련 작업
        self.youtb = None
        self.youtb_fsize = 0

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

    def showStatusMsg(self,msg):
        self.statusbar.showMessage(msg)


    #시그널 초기화
    def initSignal(self):
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

    @pyqtSlot()
    def authCheck(self):
        dlg = AuthDialog()
        dlg.exec_()
        self.user_id = dlg.user_id
        self.user_pw = dlg.user_pw

        print("id : %s password : %s" %(self.user_id, self.user_pw))

        if True: # 강제로 아이디 비번 모두 맞게 선언
            self.initAuthActive() #로그인후 모두 활성화
            self.loginButton.setText("인증완료")
            self.loginButton.setEnabled(False) #인증버튼 1회 사용후 잠금
            self.urlTextEdit.setFocus(True) #커서 자동 이동
        else:
            QMessageBox.about(self, "인증오류", "아이디 또는 비밀번호 인증 오류")

    def load_url(self):
        url=self.urlTextEdit.text().strip()
        v=re.compile('^https://www.youtube.com/watch?')
        if self.is_play: # 재생중일때 재생멈추는 코드
            self.append_log_msg('Stop Click')
            self.webEngineView.load(QUrl('about:blank')) # about:blank : 빈페이지로 초기화
            self.previewButton.setText("Play")
            self.is_play=False
            self.urlTextEdit.clear()
            self.urlTextEdit.setFocus(True)
            self.startButton.setEnabled(False)
            self.streamCombobox.clear() #저장완료시(또는 중지시) 초기화
            self.progressBar_2.setValue(0)  #다운로드 완료시 초기화
            self.showStatusMsg("인증완료")

        else : #재생전이므로 재생이 가능하도록 구현
            if v.match(url) is not None :
                self.append_log_msg('Play Click')
                self.webEngineView.load(QUrl(url))

                #상태 표시줄
                self.showStatusMsg(url + " 재생중")
                self.previewButton.setText("Stop")
                self.is_play=True
                self.startButton.setEnabled(True)
                self.initialYouWork(url) #url의 핵심부분

            else:
                QMessageBox.about(self, "URL 형식오류","Youtube 주소형식이 다름니다.")
                self.urlTextEdit.clear()
                self.urlTextEdit.setFocus(True)

    def initialYouWork(self,url):
        video_list = pytube.YouTube(url)
        #로딩바 계산 (register_on_progress_callback:pytube에서 제공)
        video_list.register_on_progress_callback(self.showProgressDownLoading) # 작업중인 것을 데리고 와봐
        #self.youtb = video_list.streams.all()
        self.youtb = video_list.streams
        self.streamCombobox.clear() #StreamCombobox 초기화
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

    def append_log_msg(self, act):
        now=datetime.datetime.now()
        nowDatetime=now.strftime('%Y-%m-%d %H:%M:%S')
        app_msg=self.user_id + ' : '+act+'-->('+ nowDatetime +')'
        print(app_msg)
        self.plainTextEdit.appendPlainText(app_msg)
        #활동 로그 저장 (DB를 사용 추#)
        with open('D:/Python_App/Python_Youtube/log/log.txt', 'a') as f:
            f.write(app_msg+'\n')

    @pyqtSlot(int) #진행율을 int로 받음
    def showProgressBrowserLoading(self, v):
        self.progressBar.setValue(v)

    @pyqtSlot()
    def selectDownPath(self):
        print('save test')
        #경로 선택
        fpath=QFileDialog.getExistingDirectory(self, 'Select Directory')
        self.pathTextEdit.setText(fpath)

    #캘린더 부분
    @pyqtSlot()
    def append_date(self):
        cur_date=self.calendarWidget.selectedDate()
        #print('cur_date : ', cur_date)
        #년 월 일 출력
        print(str(cur_date.year()) +'-'+str(cur_date.month())+'-'+str(cur_date.day()))
        Calender_msg='Calendar Click ('+str(cur_date.year()) +'-'+str(cur_date.month())+'-'+str(cur_date.day())+')'
        self.append_log_msg(Calender_msg)
        #self.append_log_msg('Calendar Click')

    #저장부분
    @pyqtSlot()
    def downloadYoutb(self):
        down_dir = self.pathTextEdit.text().strip() #strip():공백제거
        if down_dir is None or down_dir == '' or not down_dir:
            QMessageBox.about(self,'경로 선택','다운로드 받을 경로를 선택하세요.')
            return None

        self.youtb_fsize = self.youtb[self.streamCombobox.currentIndex()].filesize
        print('fsize : ',self.youtb_fsize)
        self.youtb[self.streamCombobox.currentIndex()].download(down_dir)
        # 주소 입력하면 최소 15개 정도의 index가 생성되며, 선택한 것의 파일 사이즈를 가져와!
        self.append_log_msg('Download Click')

    def showProgressDownLoading(self, stream, chunk, bytes_remaining): #stream, chunk, bytes_remaining: 서버 레지스트리에서 주는거라고함.
        #bytes_remaining: 서버 레지스트리에서 주는 현재 다운받기에서 남은 용량
        #register_on_progress_callback에서 stream, chunk, bytes_remaining을 줌!
        print(int(self.youtb_fsize - bytes_remaining))
        print('bytes_remaining',bytes_remaining)
        self.progressBar_2.setValue(int(((self.youtb_fsize - bytes_remaining) / self.youtb_fsize) * 100))

if __name__=="__main__":
    app=QApplication(sys.argv)
    you_view_main=Main()
    you_view_main.show()
    app.exec()
