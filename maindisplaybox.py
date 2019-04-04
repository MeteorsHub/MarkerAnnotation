from PyQt5.QtWidgets import QGroupBox
from PyQt5 import QtGui, QtCore


class MainDisplayBox(QGroupBox):
    resized_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        super().resizeEvent(a0)
        self.resized_signal.emit()
