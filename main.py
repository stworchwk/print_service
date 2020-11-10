import sys
import platform
import subprocess
from threading import Timer

from PyQt5 import QtCore, QtGui, QtWidgets

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

        ## PAGES
        ########################################################################

        # PAGE 1
        self.ui.btn_setting.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting))

        # PAGE 2
        self.ui.btn_to_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_home))

        ## MAIN FUNCTIONS
        MainWindow.configInit(self)

        MainWindow.printService(self)

        self.ui.btn_save_config.clicked.connect(lambda: MainWindow.updateConfig(self))

        def switchService(event):
            global GLOBAL_SERVICE_STATUS
            status = GLOBAL_SERVICE_STATUS

            if status == 0:
                GLOBAL_SERVICE_STATUS = 1
                MainWindow.runTime(self)
            else:
                GLOBAL_SERVICE_STATUS = 0
            
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
        def requestTasks():
            config = AppFunctions.call_config(self)
            global GLOBAL_SERVICE_STATUS
            status = GLOBAL_SERVICE_STATUS
            if status == 0:
                print("Service Start")
            else:
                print("Service Stop")
                
            Timer(float(config[1]), requestTasks).start()

        requestTasks()

    def runTime(self):
        t = None
        def timeRunning():
            global t, GLOBAL_SERVICE_STATUS, RUNTIME_HOURS, RUNTIME_MINUTES, RUNTIME_SECONDS
            status = GLOBAL_SERVICE_STATUS
            if status == 0:
                t.cancel()
                RUNTIME_HOURS = 0
                RUNTIME_MINUTES = 0
                RUNTIME_SECONDS = 0
            else:
                RUNTIME_SECONDS = RUNTIME_SECONDS + 1
                if RUNTIME_SECONDS >= 60:
                    RUNTIME_MINUTES = RUNTIME_MINUTES + 1
                    RUNTIME_SECONDS = 0
                if RUNTIME_MINUTES >= 60:
                    RUNTIME_HOURS = RUNTIME_HOURS + 1
                    RUNTIME_MINUTES = 0
                t = Timer(1.0, timeRunning)
                t.start()
            renderRunTime()

        def renderRunTime():
            self.ui.label_detail_run_time.setText(str(RUNTIME_HOURS).zfill(2) + ":" + str(RUNTIME_MINUTES).zfill(2) + ":" + str(RUNTIME_SECONDS).zfill(2))

        timeRunning()
            
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
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '1', self.ui.lineEdit_host_address.text()]
        _translate = QtCore.QCoreApplication.translate
        if subprocess.call(command) == 0:
            self.ui.frame_host_status.setStyleSheet("background-color: rgb(85, 255, 0); border-radius: 8px;")
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)

        else:
            self.ui.frame_host_status.setStyleSheet("background-color: rgb(255, 0, 0); border-radius: 8px;")
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_setting)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
