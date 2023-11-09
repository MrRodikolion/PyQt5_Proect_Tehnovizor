import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QMouseEvent

import cv2
import pytesseract
import os


class BookVizor(QMainWindow):
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = "C:\\Users\\Mr.Rodikolion\\PycharmProjects\\yandex_PyQt5\\tesseract/tesseract.exe"
        super().__init__()
        self.setupUi(self)
        self.startThreads()
        self.book_img_data = None

        self.selectBtn.clicked.connect(self.selectImg)
        self.deleteBtn.clicked.connect(self.deletePage)
        self.saveTextBtn.clicked.connect(self.saveBook)

        self.pages = []

    def saveBook(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Выбрать фото', '.')
        img_dir = f'{dir_name}/pages_img'
        try:
            os.mkdir(img_dir)
        except Exception:
            pass

        for y, filename in enumerate(os.listdir('../imgs/')):
            file_path = os.path.join('../imgs/', filename)
            os.replace(file_path, os.path.join(img_dir, filename))

        text = self.textEdit.toPlainText()

        fname = os.path.join(dir_name, 'text.txt')
        with open(fname, mode='w') as f:
            f.write(text)
        self.statusbar.showMessage(f'Сохраненн файл: \"{fname}\"')

    def loadText(self):
        self.textEdit.setText('\n'.join(self.pages))

    def loadTable(self):
        self.tableWidget.setRowCount(0)
        for y, filename in enumerate(os.listdir('../imgs/')):
            file_path = os.path.join('../imgs/', filename)

            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)

            pixmap = QPixmap(file_path)
            label = QtWidgets.QLabel()
            label.setPixmap(pixmap.scaled(self.tableWidget.size().width(), self.tableWidget.size().width(),
                                          Qt.KeepAspectRatio))
            label.setAlignment(Qt.AlignCenter)

            self.tableWidget.setCellWidget(y, 0, label)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def deletePage(self):
        try:
            row = self.tableWidget.selectedIndexes()
            if row != []:
                row = row[0].row()
            else:
                return

            self.tableWidget.removeRow(row)
            del self.pages[row]
            os.unlink(f'../imgs/page_{row}.jpg')

            path_dir = sorted(os.listdir('../imgs/'), key=lambda x: int(x[x.index('_') + 1:-4]))
            for n, filename in enumerate(path_dir):
                file_path = os.path.join('../imgs/', filename)
                new_file_path = file_path.replace(filename, f'page_{n}.jpg')
                os.rename(file_path, new_file_path)

            for n, page in enumerate(self.pages):
                self.pages[n] = page.replace(page[page.index('\npage_'):], f'\npage_{n}')

            self.loadText()
            self.loadTable()
        except Exception as e:
            print(e)

    def closeEvent(self, a0):
        self.cam_th.stop()
        self.hide()
        for filename in os.listdir('../imgs/'):
            file_path = os.path.join('../imgs/', filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        a0.accept()

    def selectImg(self):
        self.cam_th.isPaused = True

        try:
            if self.book_img_data[1] is not None:
                cv2.imwrite(f'C:\\Users\\Mr.Rodikolion\\PycharmProjects\\yandex_PyQt5/imgs/page_{len(self.pages)}.jpg',
                            self.book_img_data[1])

                gray = cv2.cvtColor(self.book_img_data[1], cv2.COLOR_BGR2GRAY)
                gray = cv2.medianBlur(gray, 3)
                text = pytesseract.image_to_string(gray, lang='eng')

                self.pages.append(f'{text}\npage_{len(self.pages)}')

                self.loadText()
                self.loadTable()


        except Exception as e:
            print(e)
        self.cam_th.isPaused = False

    @pyqtSlot(tuple)
    def imgSliceWork(self, book_data):
        try:
            self.book_img_data = book_data

            if book_data[1] is not None:
                cv2.rectangle(book_data[0], book_data[2], book_data[3], (0, 0, 255), 1)

            rgbImage = cv2.cvtColor(book_data[0], cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            qimg = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            qimg = qimg.scaled(640, 480, Qt.KeepAspectRatio)
            self.video.setPixmap(QPixmap.fromImage(qimg))
        except Exception as e:
            print(e)

    def startThreads(self):
        self.cam_th = CameraThread(self, self.statusbar, self.thresholdSlider)
        self.cam_th.selectImg.connect(self.imgSliceWork)
        self.cam_th.start()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1305, 769)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.selectBtn = QtWidgets.QPushButton(self.groupBox)
        self.selectBtn.setObjectName("SelectBtn")
        self.horizontalLayout_5.addWidget(self.selectBtn)
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
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
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
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
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
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_7.addWidget(self.groupBox_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.thresholdSlider.setMaximum(255)
        self.thresholdSlider.setValue(150)

        self.tableWidget.setColumnCount(1)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.selectBtn.setText(_translate("MainWindow", "Выделить"))
        self.label_2.setText(_translate("MainWindow", "Чувтсвительность: "))
        self.deleteBtn.setText(_translate("MainWindow", "Удалить"))
        self.saveTextBtn.setText(_translate("MainWindow", "Сохранить"))


class CameraThread(QThread):
    selectImg = pyqtSignal(tuple)

    def __init__(self, par, statusBar: QtWidgets.QStatusBar, slider: QtWidgets.QSlider):
        super().__init__(par)

        self.statusBar = statusBar
        self.slider = slider

        self.isStop = False
        self.isPaused = False

    def stop(self):
        self.isStop = True
        self.wait()

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            self.statusBar.showMessage('Камера подключена')
            while cv2.waitKey(1):
                if not self.isStop and not self.isPaused:
                    ret, frame = cap.read()
                    if not ret:
                        self.statusBar.showMessage('Камера работает неправильно')
                        break

                    l_th = self.slider.value()

                    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    img_gray = cv2.medianBlur(img_gray, 7)
                    _, img_gray = cv2.threshold(img_gray, l_th, 255, cv2.THRESH_BINARY)

                    img_canny = cv2.Canny(img_gray, 40, 255, 2)
                    contours = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    contours = contours[0]

                    max_area = 0
                    book_img = None
                    for i in contours:
                        area_contur = cv2.contourArea(i)
                        if area_contur > 2100 and max_area < area_contur:
                            max_area = area_contur
                            perimetr = 0.02 * cv2.arcLength(i, True)
                            approx = cv2.approxPolyDP(i, perimetr, True)
                            if len(approx) >= 4:
                                rect = cv2.boundingRect(i)

                                book_img = frame[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
                                book_pt1 = (rect[0], rect[1])
                                book_pt2 = (rect[0] + rect[2], rect[1] + rect[3])

                    if book_img is not None:
                        self.selectImg.emit((frame, book_img, book_pt1, book_pt2))
                    else:
                        self.selectImg.emit((frame, None))
                elif self.isPaused:
                    pass
                else:
                    cap.release()
                    self.statusBar.showMessage('Камера отключена')
                    break
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BookVizor()
    ex.show()
    sys.exit(app.exec_())
