from PyQt5.QtWidgets import QPushButton
from PyQt5 import QtCore, QtGui


class FingerButton(QPushButton):
    finger_button_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        while True:
            try:
                self.clicked.disconnect()
            except TypeError:
                break
        self.clicked.connect(self.on_click)

    def on_click(self):
        button_id = int(self.objectName().split('_')[-1])
        self.finger_button_signal.emit(button_id)

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        pass

    def keyReleaseEvent(self, e: QtGui.QKeyEvent):
        pass
