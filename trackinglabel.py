from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui, QtCore


class TrackingLabel(QLabel):
    label_click_signal = QtCore.pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        if self.objectName() == 'img_11':
            if ev.button() == QtCore.Qt.LeftButton:
                self.label_click_signal.emit(1, ev.x(), ev.y())
            if ev.button() == QtCore.Qt.RightButton:
                self.label_click_signal.emit(2, ev.x(), ev.y())
        elif self.objectName() == 'img_21':
            if ev.button() == QtCore.Qt.LeftButton:
                self.label_click_signal.emit(3, ev.x(), ev.y())
            if ev.button() == QtCore.Qt.RightButton:
                self.label_click_signal.emit(4, ev.x(), ev.y())
