import os
import sys

from Windows_.tehnovizor import TehnoVizor
from Windows_.bookvizor import BookVizor

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication


class Ui_Form(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.normModeBtn.clicked.connect(self.openNormalMode)
        self.bookModeBtn.clicked.connect(self.openBookMode)

    def openNormalMode(self):
        self.hide()
        self.norm = TehnoVizor()
        self.norm.show()

    def openBookMode(self):
        self.hide()
        self.book = BookVizor()
        self.book.show()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(564, 260)
        Form.setMinimumSize(QtCore.QSize(564, 260))
        Form.setMaximumSize(QtCore.QSize(564, 260))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 2, 1, 1)
        self.normModeBtn = QtWidgets.QPushButton(Form)
        self.normModeBtn.setObjectName("normModeBtn")
        self.gridLayout.addWidget(self.normModeBtn, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 2, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 4, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 0, 2, 1, 1)
        self.bookModeBtn = QtWidgets.QPushButton(Form)
        self.bookModeBtn.setObjectName("bookModeBtn")
        self.gridLayout.addWidget(self.bookModeBtn, 2, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form",
                                      "<html><head/><body><p>"
                                      "<span style=\" font-size:18pt;\">ТекстоВизор</span></p></body></html>"))
        self.normModeBtn.setText(_translate("Form", "Обычный режим"))
        self.bookModeBtn.setText(_translate("Form", "Режим сканирования книг"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Ui_Form()
    ex.show()
    sys.exit(app.exec_())
