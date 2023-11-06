import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt, pyqtSlot

import sqlite3 as sql
import cv2
import pytesseract
from datetime import datetime
from speech_recognition import Recognizer, Microphone, UnknownValueError, WaitTimeoutError, RequestError


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = "./tesseract/tesseract.exe"
        super().__init__()
        self.setupUi(self)
        self.loadDB()

        self.getPhotoButton.clicked.connect(self.loadPhoto)
        self.reloadButton.clicked.connect(self.getTextPhoto)
        self.saveButton.clicked.connect(self.saveText)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.loadButton.clicked.connect(self.loadFromHistory)

        self.micButton.clicked.connect(self.getWhisperPres)

        self.recognizer = Recognizer()

        self.startThreads()
        self.loadLast()

    def loadLast(self):
        last_text = self.cur.execute('''SELECT text FROM history ORDER BY id DESC LIMIT 1''').fetchone()
        if last_text is not None:
            self.textEdit.setText(last_text[0])

    def closeEvent(self, a0):
        ok = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти?",
                                  QMessageBox.Yes, QMessageBox.Cancel)

        if ok == QMessageBox.Yes:
            text = self.textEdit.toPlainText()
            if text != '':
                text = ''.join(map(lambda x: '\'' if x == '\"' else x, text))
                self.cur.execute(f'''INSERT INTO history(date, text) 
                            VALUES(\'{datetime.now().strftime("%d.%m.%Y %H:%M")}\', \"{text}\")''')
                self.con.commit()

            self.cam_th.isStop = True
            self.cam_th.wait()
            self.mic_th.wait()


            a0.accept()
        else:
            a0.ignore()

    def getWhisperPres(self):
        if not self.mic_th.isRunning():
            self.mic_th.start()
            self.micButton.setText("🔄️")
            self.micButton.setEnabled(False)

    @pyqtSlot(str)
    def whisper(self, text):
        self.textEdit.textCursor().insertText(text)

    def loadFromHistory(self):
        table_indx = self.tableWidget.selectedItems()[0].row()
        id = self.tableWidget.item(table_indx, 0).text()
        data = self.cur.execute(f'''SELECT text FROM history WHERE id = \'{id}\'''').fetchall()[0][0]
        self.textEdit.setText(data)

    def tabChanged(self):
        if self.tabWidget.currentIndex() == 0:
            self.cam_th.start()
        elif self.tabWidget.currentIndex() == 2:
            history = self.cur.execute('''SELECT * FROM history''').fetchall()[::-1]
            self.tableWidget.setRowCount(0)
            for y, row in enumerate(history):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for x, elem in enumerate(row):
                    self.tableWidget.setItem(y, x, QTableWidgetItem(str(elem)))
            self.tableWidget.resizeColumnsToContents()

    def loadDB(self):
        self.con = sql.connect('history_db.sqlite3')
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY,
                        date TEXT NOT NULL, 
                        text TEXT NOT NULL)''')

        if self.cur.execute('''SELECT count(*) FROM history''').fetchone()[0] > 100:
            last_text = self.cur.execute('''SELECT * FROM history ORDER BY id DESC LIMIT 1''').fetchone()
            self.cur.execute('''DELETE FROM history''')
            self.cur.execute(f'''INSERT INTO history VALUES({last_text[0]}, \'{last_text[1]}\', \"{last_text[2]}\")''')
        self.con.commit()

    def saveText(self):
        try:
            text = self.textEdit.toPlainText()

            fname = QFileDialog.getSaveFileName(self, 'Сохранить текст', '', 'Текстовый файл (*.txt)')[0]

            with open(fname, mode='w') as f:
                f.write(text)
            self.statusbar.showMessage(f'Сохраненн файл: \"{fname}\"')

            text = ''.join(map(lambda x: '\'' if x == '\"' else x, text))
            self.cur.execute(f'''INSERT INTO history(date, text) 
                        VALUES(\'{datetime.now().strftime("%d.%m.%Y %H:%M")}\', \"{text}\")''')
            self.con.commit()

        except Exception as e:
            self.statusbar.clearMessage()
            self.statusbar.showMessage(str(e))

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key_Space:
            self.fixedBox.setChecked(not self.fixedBox.isChecked())

    @pyqtSlot(tuple)
    def setImage(self, img_data):
        if not self.cam_th.isStop:
            self.video.setPixmap(QPixmap.fromImage(img_data[0]))
            self.textEdit.setText(str(img_data[1]))

    def loadPhoto(self):
        try:
            fname = QFileDialog.getOpenFileName(self, 'Выбрать фото', '.',
                                                'Изображение (*.jpg *.png);;Все файлы (*)')[0]
            if fname == '':
                raise FileNotFoundError

            self.img = cv2.imread(fname)

            rgbImage = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            pixmap = QPixmap.fromImage(p)

            self.photo.setPixmap(pixmap)

            self.getTextPhoto()

            self.statusbar.showMessage(f'Загружен файл: \"{fname}\"')
        except FileNotFoundError:
            self.statusbar.showMessage("Файл не выбран")
        except Exception as e:
            self.statusbar.showMessage(str(e))

    def getTextPhoto(self):
        try:
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 3)
            text = pytesseract.image_to_string(gray, lang='eng')
            self.textEdit.setText(text)
        except AttributeError:
            self.statusbar.showMessage("Изображение не загружено")
        except Exception as e:
            self.statusbar.showMessage(str(e))

    def startThreads(self):
        self.cam_th = CameraThread(self, self.tabWidget, self.fixedBox, self.statusbar)
        self.cam_th.changePixmap.connect(self.setImage)

        self.mic_th = MicThread(self, self.statusbar, self.micButton)
        self.mic_th.audioToText.connect(self.whisper)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.video = QtWidgets.QLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video.sizePolicy().hasHeightForWidth())
        self.video.setSizePolicy(sizePolicy)
        self.video.setObjectName("video")
        self.gridLayout_4.addWidget(self.video, 1, 0, 1, 1)
        self.fixedBox = QtWidgets.QCheckBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fixedBox.sizePolicy().hasHeightForWidth())
        self.fixedBox.setSizePolicy(sizePolicy)
        self.fixedBox.setObjectName("fixedBox")
        self.gridLayout_4.addWidget(self.fixedBox, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.photo = QtWidgets.QLabel(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.photo.sizePolicy().hasHeightForWidth())
        self.photo.setSizePolicy(sizePolicy)
        self.photo.setText("")
        self.photo.setObjectName("photo")
        self.gridLayout_3.addWidget(self.photo, 1, 0, 1, 1)
        self.getPhotoButton = QtWidgets.QPushButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.getPhotoButton.sizePolicy().hasHeightForWidth())
        self.getPhotoButton.setSizePolicy(sizePolicy)
        self.getPhotoButton.setObjectName("getPhotoButton")
        self.gridLayout_3.addWidget(self.getPhotoButton, 0, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.reloadButton = QtWidgets.QPushButton(self.tab_2)
        self.reloadButton.setObjectName("reloadButton")
        self.horizontalLayout_2.addWidget(self.reloadButton)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.tab_3)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.loadButton = QtWidgets.QPushButton(self.tab_3)
        self.loadButton.setObjectName("loadButton")
        self.gridLayout.addWidget(self.loadButton, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setMinimumSize(QtCore.QSize(418, 733))
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.textEdit, 1, 1, 1, 1)
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveButton.sizePolicy().hasHeightForWidth())
        self.saveButton.setSizePolicy(sizePolicy)
        self.saveButton.setObjectName("saveButton")
        self.gridLayout_2.addWidget(self.saveButton, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.micButton = QtWidgets.QPushButton(self.groupBox)
        self.micButton.setObjectName("micButton")
        self.horizontalLayout_3.addWidget(self.micButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)
        self.horizontalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.hideColumn(0)
        self.tableWidget.setRowCount(0)

        self.tableWidget.setHorizontalHeaderLabels(('id', 'Дата Время', 'Текст'))

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Текстовизор"))
        self.fixedBox.setText(_translate("MainWindow", "Зафиксировать"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Видео"))
        self.getPhotoButton.setText(_translate("MainWindow", "Выбрать фото"))
        self.reloadButton.setText(_translate("MainWindow", "🔁"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Фото"))
        self.loadButton.setText(_translate("MainWindow", "Загрузить"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "История"))
        self.saveButton.setText(_translate("MainWindow", "Сохранить"))
        self.micButton.setText(_translate("MainWindow", "🎙️"))


class MicThread(QThread):
    audioToText = pyqtSignal(str)

    def __init__(self, par, statusBar: QtWidgets.QStatusBar, micBtn):
        super().__init__(par)
        self.statusBar = statusBar
        self.mic_btn = micBtn

        self.recognizer = Recognizer()

    def run(self):
        try:
            with Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.mic_btn.setText("⏹️")
                recorded_audio = self.recognizer.listen(source, timeout=1)
            self.mic_btn.setText("🔄️")

            text = self.recognizer.recognize_google(
                recorded_audio,
                language="en-US"
            )

            self.audioToText.emit(text)
        except WaitTimeoutError or UnknownValueError:
            pass
        except RequestError:
            self.statusBar.showMessage("Отсутствует подключение к интернету")
        except Exception as e:
            self.statusBar.clearMessage()
            self.statusBar.showMessage(str(e))
            print([e])
        self.mic_btn.setText("🎙️")
        self.mic_btn.setEnabled(True)


class CameraThread(QThread):
    changePixmap = pyqtSignal(tuple)

    def __init__(self, par, tabW: QtWidgets.QTabWidget, isFix: QtWidgets.QCheckBox, statusBar: QtWidgets.QStatusBar):
        super().__init__(par)

        self.tabWidget = tabW
        self.isfixBox = isFix
        self.statusBar = statusBar
        self.isStop = False

    def run(self):
        cap = cv2.VideoCapture(0)
        self.statusBar.showMessage('Камера подключена')
        while cv2.waitKey(1):
            if self.tabWidget.currentIndex() == 0 and not self.isfixBox.isChecked() and not self.isStop:
                ret, frame = cap.read()
                if not ret:
                    self.statusBar.showMessage('Камера работает неправильно')
                    break

                y, x, _ = frame.shape
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 3)
                text = pytesseract.image_to_string(gray, lang='eng')

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

                to_ui = (p, text)
                self.changePixmap.emit(to_ui)
            elif self.isfixBox.isChecked():
                pass
            else:
                cap.release()
                self.statusBar.showMessage('Камера отключена')
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Ui_MainWindow()
    ex.show()

    sys.exit(app.exec_())
