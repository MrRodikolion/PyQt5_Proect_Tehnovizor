'''
В /Lib/site-packages/speech_recognition/audio.py возможно нужно заменить
    flac_converter = shutil_which("flac")
на  flac_converter = shutil_which("flac.exe")
'''

import sys

from PyQt5.QtWidgets import QApplication

from Windows_.tehnovizor import TehnoVizor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TehnoVizor()
    ex.show()
    sys.exit(app.exec_())
