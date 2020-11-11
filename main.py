import sys
import time
from threading import Timer, Thread

from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork

# GUI FILE
from ui_main import Ui_MainWindow

# IMPORT UI FUNCTIONS
from ui_functions import UIFunctions

# IMPORT App FUNCTIONS
from app_functions import AppFunctions

GLOBAL_SERVICE_STATUS = 0
RUNTIME_HOURS = 0
RUNTIME_MINUTES = 0
RUNTIME_SECONDS = 0
TASK_SUCCESS = 0
TASK_FAILURE = 0
RUN_TIME_THREAD = None
REQUEST_THREAD = None

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        MainWindow.ping(self)

        # MOVE WINDOW
        def moveWindow(event):
            # RESTORE BEFORE MOVE
            if UIFunctions.returnStatus(self) == 1:
                UIFunctions.maximize_restore(self)

            # IF LEFT CLICK MOVE WINDOW
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # SET TITLE BAR
        self.ui.title_bar.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        UIFunctions.uiDefinitions(self)

        # CLOSE
        self.ui.btn_close.clicked.connect(lambda: closeWindow())

        def closeWindow():
            global RUN_TIME_THREAD, REQUEST_THREAD
            self.close()
            if RUN_TIME_THREAD != None:
                RUN_TIME_THREAD.cancel()
            if REQUEST_THREAD != None:
                REQUEST_THREAD.cancel()

        ## PAGES
        ########################################################################

        # PAGE 1
        self.ui.btn_setting.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting))

        # PAGE 2
        self.ui.btn_to_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_home))

        ## MAIN FUNCTIONS
        MainWindow.configInit(self)

        self.ui.btn_save_config.clicked.connect(lambda: MainWindow.updateConfig(self))

        def switchService(event):
            global RUN_TIME_THREAD, REQUEST_THREAD, GLOBAL_SERVICE_STATUS, RUNTIME_HOURS, RUNTIME_MINUTES, RUNTIME_SECONDS, SWITCH_SERVICE_PING_REQUEST
            status = GLOBAL_SERVICE_STATUS

            if status == 0:
                config = AppFunctions.call_config(self)
                url = config[0] + config[2]
                req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
                SWITCH_SERVICE_PING_REQUEST = QtNetwork.QNetworkAccessManager()
                SWITCH_SERVICE_PING_REQUEST.finished.connect(self.handleResponseOfSwitchService)
                SWITCH_SERVICE_PING_REQUEST.get(req)
            else:
                GLOBAL_SERVICE_STATUS = 0
                RUNTIME_HOURS = 0
                RUNTIME_MINUTES = 0
                RUNTIME_SECONDS = 0
                if RUN_TIME_THREAD != None:
                    RUN_TIME_THREAD.cancel()
                if REQUEST_THREAD != None:
                    REQUEST_THREAD.cancel()
                MainWindow.renderRunTime(self)
                MainWindow.uiSwitchService(self)
            
        ## Start&Stop Service
        self.ui.frame_circle.mousePressEvent = switchService


        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##

    ## APP EVENTS
    ########################################################################

    def printService(self):
        def response(reply):
            global RUN_TIME_THREAD, REQUEST_THREAD, GLOBAL_SERVICE_STATUS, RUNTIME_HOURS, RUNTIME_MINUTES, RUNTIME_SECONDS
            er = reply.error()
            if er == QtNetwork.QNetworkReply.NoError:
                print('response')
            else:
                GLOBAL_SERVICE_STATUS = 0
                RUNTIME_HOURS = 0
                RUNTIME_MINUTES = 0
                RUNTIME_SECONDS = 0
                if RUN_TIME_THREAD != None:
                    RUN_TIME_THREAD.cancel()
                if REQUEST_THREAD != None:
                    REQUEST_THREAD.cancel()
                MainWindow.renderRunTime(self)
                MainWindow.uiSwitchService(self)
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting)
        def requestTasks():
            print('request')
            config = AppFunctions.call_config(self)
            global REQUEST_THREAD, GLOBAL_SERVICE_STATUS, REQUEST_TASKS
            status = GLOBAL_SERVICE_STATUS
            url = config[0] + config[3]
            REQUEST_TASKS = QtNetwork.QNetworkAccessManager()
            reply = REQUEST_TASKS.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))
            response(reply)

            #MainWindow.renderTasksSuccessAndFailure(self)

            if status == 1:
                REQUEST_THREAD = Timer(float(config[1]), requestTasks)
                REQUEST_THREAD.start()

        requestTasks()

    def runTime(self):
        def timeRunning():
            global RUN_TIME_THREAD, GLOBAL_SERVICE_STATUS, RUNTIME_HOURS, RUNTIME_MINUTES, RUNTIME_SECONDS
            status = GLOBAL_SERVICE_STATUS
            if status == 1:
                RUNTIME_SECONDS = RUNTIME_SECONDS + 1
                if RUNTIME_SECONDS >= 60:
                    RUNTIME_MINUTES = RUNTIME_MINUTES + 1
                    RUNTIME_SECONDS = 0
                if RUNTIME_MINUTES >= 60:
                    RUNTIME_HOURS = RUNTIME_HOURS + 1
                    RUNTIME_MINUTES = 0
                RUN_TIME_THREAD = Timer(1.0, timeRunning)
                RUN_TIME_THREAD.start()
            MainWindow.renderRunTime(self)
        timeRunning()

    def renderRunTime(self):
        self.ui.label_detail_run_time.setText(str(RUNTIME_HOURS).zfill(2) + ":" + str(RUNTIME_MINUTES).zfill(2) + ":" + str(RUNTIME_SECONDS).zfill(2))

    def renderTasksSuccessAndFailure(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.label_detail_success.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">" + str(TASK_SUCCESS) + " </span><span style=\" font-size:9pt; color:#c7c7c7;\">Tasks</span></p></body></html>"))
        self.ui.label_detail_failed.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600;\">" + str(TASK_FAILURE) + " </span><span style=\" font-size:9pt; color:#c7c7c7;\">Tasks</span></p></body></html>"))

    def uiSwitchService(self):
        global GLOBAL_SERVICE_STATUS
        status = GLOBAL_SERVICE_STATUS
        _translate = QtCore.QCoreApplication.translate
        if status == 0:
            self.ui.label_circle_main.setText(_translate("MainWindow", "Start"))
            self.ui.frame_circle.setStyleSheet("QFrame{border: 5px solid rgba(255, 0, 0, 150);border-radius: 125px;}QFrame:hover {border: 5px solid rgb(85, 255, 0);}")
            self.ui.label_circle_status.setText(_translate("MainWindow", "<html><head/><body><p>Status: <span style=\" font-weight:600; color:#ff0000;\">Service not started</span></p></body></html>"))
        else:
            self.ui.label_circle_main.setText(_translate("MainWindow", "Stop"))
            self.ui.frame_circle.setStyleSheet("QFrame{border: 5px solid rgb(85, 255, 0);border-radius: 125px;}QFrame:hover {border: 5px solid rgba(255, 0, 0, 150);}")
            self.ui.label_circle_status.setText(_translate("MainWindow", "<html><head/><body><p>Status: <span style=\" font-weight:600; color:#55ff00;\">Service in progress</span></p></body></html>"))

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def configInit(self):
        config = AppFunctions.call_config(self)
        self.ui.lineEdit_host_address.setText(config[0])
        self.ui.label_circle_host.setText('Host: ' + config[0])
        self.ui.spinBox_inval_time.setValue(int(config[1]))

    def updateConfig(self):
        new_host = self.ui.lineEdit_host_address.text()
        new_inval = self.ui.spinBox_inval_time.text()
        AppFunctions.update_config(self, new_host, new_inval)
        MainWindow.configInit(self)
        MainWindow.ping(self)

    def ping(self):
        global PING_REQUEST
        config = AppFunctions.call_config(self)
        url = QtCore.QUrl(config[0] + config[2])
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        PING_REQUEST = QtNetwork.QNetworkAccessManager()
        PING_REQUEST.finished.connect(self.handleResponseOfPing)
        PING_REQUEST.get(req)

    def handleResponseOfPing(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            self.ui.frame_host_status.setStyleSheet("background-color: rgb(85, 255, 0); border-radius: 8px;")
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
        else:
            self.ui.frame_host_status.setStyleSheet("background-color: rgb(255, 0, 0); border-radius: 8px;")
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting)

    def handleResponseOfSwitchService(self, reply):
        global GLOBAL_SERVICE_STATUS
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            GLOBAL_SERVICE_STATUS = 1
            MainWindow.runTime(self)
            MainWindow.printService(self)
            MainWindow.uiSwitchService(self)
        else:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting)
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
