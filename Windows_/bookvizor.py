from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPixmap

import cv2
import pytesseract

class BookVizor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.startThreads()

    @pyqtSlot(tuple)
    def imgWorck(self, data):
        self.video.setPixmap(QPixmap.fromImage(data[0]))

    def startThreads(self):
        self.cam_th = CameraThread(self, self.statusbar)
        self.cam_th.changePixmap.connect(self.imgWorck)
        self.cam_th.start()
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1305, 834)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.SelectBtn = QtWidgets.QPushButton(self.groupBox)
        self.SelectBtn.setObjectName("SelectBtn")
        self.horizontalLayout_5.addWidget(self.SelectBtn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.thresholdSlider = QtWidgets.QSlider(self.groupBox)
        self.thresholdSlider.setMinimumSize(QtCore.QSize(320, 0))
        self.thresholdSlider.setOrientation(QtCore.Qt.Horizontal)
        self.thresholdSlider.setObjectName("thresholdSlider")
        self.horizontalLayout_4.addWidget(self.thresholdSlider)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.resetBtn = QtWidgets.QPushButton(self.groupBox)
        self.resetBtn.setObjectName("resetBtn")
        self.horizontalLayout_6.addWidget(self.resetBtn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.saveImgBtn = QtWidgets.QPushButton(self.groupBox)
        self.saveImgBtn.setObjectName("saveImgBtn")
        self.horizontalLayout_3.addWidget(self.saveImgBtn)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.video = QtWidgets.QLabel(self.groupBox)
        self.video.setMinimumSize(QtCore.QSize(640, 480))
        self.video.setText("")
        self.video.setObjectName("video")
        self.verticalLayout_4.addWidget(self.video)
        self.horizontalLayout_7.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox_2)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scanBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.scanBtn.setObjectName("scanBtn")
        self.horizontalLayout_2.addWidget(self.scanBtn)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.deleteBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.deleteBtn.setObjectName("deleteBtn")
        self.horizontalLayout_2.addWidget(self.deleteBtn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_7.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox_3)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveTextBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.saveTextBtn.setObjectName("saveTextBtn")
        self.horizontalLayout.addWidget(self.saveTextBtn)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_7.addWidget(self.groupBox_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.SelectBtn.setText(_translate("MainWindow", "Выделить"))
        self.label_2.setText(_translate("MainWindow", "Чувтсвительность: "))
        self.resetBtn.setText(_translate("MainWindow", "Сбросить"))
        self.saveImgBtn.setText(_translate("MainWindow", "Сохранить"))
        self.scanBtn.setText(_translate("MainWindow", "Сканировать"))
        self.deleteBtn.setText(_translate("MainWindow", "Удалить"))
        self.saveTextBtn.setText(_translate("MainWindow", "Сохранить"))


class CameraThread(QThread):
    changePixmap = pyqtSignal(tuple)

    def __init__(self, par, statusBar: QtWidgets.QStatusBar):
        super().__init__(par)

        self.statusBar = statusBar
        self.isStop = False

    def run(self):
        cap = cv2.VideoCapture(0)
        self.statusBar.showMessage('Камера подключена')
        while cv2.waitKey(1):
            if not self.isStop:
                ret, frame = cap.read()
                if not ret:
                    self.statusBar.showMessage('Камера работает неправильно')
                    break

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

                to_ui = (p, )
                self.changePixmap.emit(to_ui)
            else:
                cap.release()
                self.statusBar.showMessage('Камера отключена')
                break
