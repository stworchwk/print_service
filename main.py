import sys
import time
import json
from threading import Timer, Thread

from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork

# GUI FILE
from ui_main import Ui_MainWindow

# IMPORT UI FUNCTIONS
from ui_functions import UIFunctions

# IMPORT App FUNCTIONS
from app_functions import AppFunctions

#IMPORT Generate Pdf
from generate_pdf import GeneratePdf

GLOBAL_SERVICE_STATUS = 0
RUNTIME_HOURS = 0
RUNTIME_MINUTES = 0
RUNTIME_SECONDS = 0
TASK_SUCCESS = 0
TASK_FAILURE = 0
RUN_TIME_THREAD = None
REQUEST_THREAD = None
MAIN_WINDOW = None

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
            self.hide()
            #global RUN_TIME_THREAD, REQUEST_THREAD
            #self.close()
            #MainWindow.stopAllThread(self)

        ## PAGES
        ########################################################################

        # PAGE 1
        self.ui.btn_setting.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting))

        # PAGE 2
        self.ui.btn_to_home.clicked.connect(lambda: toHomePage())

        def toHomePage():
            #self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
            MainWindow.ping(self)

        ## MAIN FUNCTIONS
        MainWindow.configInit(self)

        self.ui.btn_save_config.clicked.connect(lambda: MainWindow.updateConfig(self))

        def switchService(event):
            def response(reply):
                global GLOBAL_SERVICE_STATUS
                er = reply.error()
                if er == QtNetwork.QNetworkReply.NoError:
                    GLOBAL_SERVICE_STATUS = 1
                    MainWindow.runTime(self)
                    MainWindow.printService(self)
                    MainWindow.uiSwitchService(self)
                else:
                    self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting)

            global RUN_TIME_THREAD, REQUEST_THREAD, GLOBAL_SERVICE_STATUS, RUNTIME_HOURS, RUNTIME_MINUTES, RUNTIME_SECONDS, TASK_SUCCESS, TASK_FAILURE
            status = GLOBAL_SERVICE_STATUS

            if status == 0:
                config = AppFunctions.call_config(self)
                url = config[0] + config[2]
                req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
                switch_service_ping_request = QtNetwork.QNetworkAccessManager()
                reply = switch_service_ping_request.get(req)
                loop = QtCore.QEventLoop()
                reply.finished.connect(loop.quit)
                loop.exec_()
                response(reply)
            else:
                GLOBAL_SERVICE_STATUS = 0
                RUNTIME_HOURS = 0
                RUNTIME_MINUTES = 0
                RUNTIME_SECONDS = 0
                TASK_SUCCESS = 0
                TASK_FAILURE = 0
                MainWindow.stopAllThread(self)
                MainWindow.renderRunTime(self)
                MainWindow.uiSwitchService(self)
                MainWindow.renderTasksSuccessAndFailure(self)
            
        ## Start&Stop Service
        self.ui.frame_circle.mousePressEvent = switchService


        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##

    ## APP EVENTS
    ########################################################################

    def stopAllThread(self):
        global RUN_TIME_THREAD, REQUEST_THREAD
        if RUN_TIME_THREAD != None:
            RUN_TIME_THREAD.cancel()
        if REQUEST_THREAD != None:
            REQUEST_THREAD.cancel()

    def printTaskClear(self, task):
        def response(reply):
            global TASK_SUCCESS, TASK_FAILURE
            er = reply.error()
            if er == QtNetwork.QNetworkReply.NoError:
                TASK_SUCCESS = TASK_SUCCESS + 1
            else:
                TASK_FAILURE = TASK_FAILURE + 1
            MainWindow.renderTasksSuccessAndFailure(self)

        config = AppFunctions.call_config(self)
        url = config[0] + config[4]
        data = '?'
        countloop = 0
        for task_id in task:
            andText = ''
            if countloop != 0:
                andText = '&'
            data +=  andText + 'task_id[' + str(countloop) + ']=' + str(task_id)
            countloop = countloop + 1
        request_tasks = QtNetwork.QNetworkAccessManager()
        reply = request_tasks.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url + data)))
        loop = QtCore.QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec_()
        response(reply)

    def printService(self):
        def response(reply):
            global RUN_TIME_THREAD, REQUEST_THREAD, GLOBAL_SERVICE_STATUS, RUNTIME_HOURS, RUNTIME_MINUTES, RUNTIME_SECONDS, TASK_SUCCESS, TASK_FAILURE
            er = reply.error()
            if er == QtNetwork.QNetworkReply.NoError:
                bytes_string = reply.readAll()
                data  = json.loads(str(bytes_string, 'utf-8'))
                for task in data['tasks']:
                    if task['is_receipt'] == True:
                        print_status = GeneratePdf.receipt(self, task)
                        if print_status:
                            MainWindow.printTaskClear(self, [task['id']])
                        else:
                            TASK_FAILURE = TASK_FAILURE + 1
                            MainWindow.renderTasksSuccessAndFailure(self)
                    else:
                        print_status = GeneratePdf.bill(self, task)
                        if print_status:
                            MainWindow.printTaskClear(self, [task['id']])
                        else:
                            TASK_FAILURE = TASK_FAILURE + 1
                            MainWindow.renderTasksSuccessAndFailure(self)

                #if len(data['tasks']) > 0:
                #    MainWindow.printTaskClear(self, data['task_id'])
            else:
                GLOBAL_SERVICE_STATUS = 0
                RUNTIME_HOURS = 0
                RUNTIME_MINUTES = 0
                RUNTIME_SECONDS = 0
                TASK_SUCCESS = 0
                TASK_FAILURE = 0
                MainWindow.stopAllThread(self)
                MainWindow.renderRunTime(self)
                MainWindow.uiSwitchService(self)
                MainWindow.renderTasksSuccessAndFailure(self)
                #to setting page
                self.ui.frame_host_status.setStyleSheet("background-color: rgb(255, 0, 0); border-radius: 8px;")
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting) #### show some error in debug console

        def requestTasks():
            config = AppFunctions.call_config(self)
            global REQUEST_THREAD, GLOBAL_SERVICE_STATUS
            status = GLOBAL_SERVICE_STATUS
            url = config[0] + config[3]
            request_tasks = QtNetwork.QNetworkAccessManager()
            reply = request_tasks.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))
            loop = QtCore.QEventLoop()
            reply.finished.connect(loop.quit)
            loop.exec_()
            response(reply)

            MainWindow.renderTasksSuccessAndFailure(self)

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
        def response(reply):
            er = reply.error()
            if er == QtNetwork.QNetworkReply.NoError:
                self.ui.frame_host_status.setStyleSheet("background-color: rgb(85, 255, 0); border-radius: 8px;")
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
            else:
                self.ui.frame_host_status.setStyleSheet("background-color: rgb(255, 0, 0); border-radius: 8px;")
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting)

        config = AppFunctions.call_config(self)
        url = QtCore.QUrl(config[0] + config[2])
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        ping_request = QtNetwork.QNetworkAccessManager()
        reply = ping_request.get(req)
        loop = QtCore.QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec_()
        response(reply)

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip('DSK Print Service')
        menu = QtWidgets.QMenu(parent)

        open_app = menu.addAction("Open - DSK Print Service")
        open_app.triggered.connect(self.open_print_service)
        open_app.setIcon(QtGui.QIcon('icon.ico'))

        close_app = menu.addAction("Close")
        close_app.triggered.connect(self.close_print_service)
        close_app.setIcon(QtGui.QIcon('close-btn.ico'))

        menu.addSeparator()

        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            MAIN_WINDOW.show()

    def open_print_service(self):
        MAIN_WINDOW.show()

    def close_print_service(self):
        MAIN_WINDOW.stopAllThread()
        MAIN_WINDOW.close()
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MAIN_WINDOW = MainWindow()
    MAIN_WINDOW.show()

    #Tray
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("icon.ico"), w)
    tray_icon.show()
    tray_icon.showMessage("DSK Print Service", 'Welcome to our product\nPowered by Dot Socket Co., Ltd.', QtGui.QIcon("icon.ico"))
    sys.exit(app.exec_())
