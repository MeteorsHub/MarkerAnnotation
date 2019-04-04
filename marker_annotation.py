import os
import sys
from ui_main_window_ui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5 import QtCore, QtGui
import traceback

from sequence_model import SequenceModel


class MarkerAnnotationMainWindow(QMainWindow, Ui_MainWindow):
    default_label_texts = ['机位1 标签图', '机位2 标签图', '机位1 参考图', '机位2 参考图']

    def __init__(self, parent=None):
        super(MarkerAnnotationMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.cwd = os.getcwd()
        self.q_pixmaps = [None, None, None, None]
        self.finger_button_id = 1

        self.seq_model = SequenceModel()

        self.finger_buttons = [self.pushButton_1, self.pushButton_2, self.pushButton_3, self.pushButton_4,
                               self.pushButton_5, self.pushButton_6, self.pushButton_7, self.pushButton_8,
                               self.pushButton_9, self.pushButton_10]
        for i in range(10):
            color = '(%d, %d, %d)' % (self.seq_model.anno_color[i][0],
                                      self.seq_model.anno_color[i][1],
                                      self.seq_model.anno_color[i][2])
            self.finger_buttons[i].setStyleSheet('color: rgb%s;' % color)

        self.setWindowState(QtCore.Qt.WindowMaximized)

    def update_seq_list(self):
        self.SeqListWidget.clear()
        flag = True
        for _id, _anno in self.seq_model.seq_list.items():
            item = QListWidgetItem(str(_id), self.SeqListWidget)
            if _anno is None:
                item.setForeground(QColor(255, 0, 0))
                if flag:
                    item.setSelected(True)
                    flag = False
            else:
                item.setForeground(QColor(0, 255, 0))
            self.SeqListWidget.addItem(item)
        if flag:
            self.SeqListWidget.item(0).setSelected(True)
        self.SeqListWidget.setFocus()

    def update_seq_list_color(self):
        for i in range(self.SeqListWidget.count()):
            seq_id = int(self.SeqListWidget.item(i).text())
            if seq_id in self.seq_model.seq_list:
                if self.seq_model.seq_list[seq_id] is None:
                    self.SeqListWidget.item(i).setForeground(QColor(255, 0, 0))
                else:
                    self.SeqListWidget.item(i).setForeground(QColor(0, 255, 0))

    def update_imgs(self, seq_list_id=None):
        if seq_list_id is None:
            seq_list_id = int(self.SeqListWidget.currentItem().text())
        imgs = self.seq_model.load_imgs_with_anno(seq_list_id)
        for i in range(4):
            if imgs[i] is not None:
                qimage = QImage(imgs[i].data, imgs[i].shape[1], imgs[i].shape[0], QImage.Format_RGB888)
                self.q_pixmaps[i] = QPixmap(qimage)
            else:
                self.q_pixmaps[i] = None
        self.show_imgs()

    def show_imgs(self):
        img_labels = [self.img_11, self.img_21, self.img_12, self.img_22]
        for i in range(4):
            if self.q_pixmaps[i] is None:
                img_labels[i].setText(self.default_label_texts[i])
            else:
                w = img_labels[i].width()
                h = img_labels[i].height()
                img_labels[i].setPixmap(self.q_pixmaps[i].scaled(w, h, QtCore.Qt.KeepAspectRatio))
        for i in range(4):
            img_labels[i].show()
        return

    def update_anno(self, camera_id, mouse_button_id, x, y):
        if not self.SeqListWidget.count():
            return
        seq_list_id = int(self.SeqListWidget.currentItem().text())
        if camera_id == 1 and self.finger_button_id > 5:
            return
        if camera_id == 2 and self.finger_button_id <= 5:
            return
        if camera_id == 1 and self.q_pixmaps[0] is None:
            return
        if camera_id == 2 and self.q_pixmaps[1] is None:
            return

        if mouse_button_id == 2:
            u, v = [-1, -1]
        else:
            if camera_id == 1:
                label_h = self.img_11.height()
                label_w = self.img_11.width()
                new_pixmap = self.q_pixmaps[0].scaled(label_w, label_h, QtCore.Qt.KeepAspectRatio)
                img_h = new_pixmap.height()
                img_w = new_pixmap.width()
            else:
                label_h = self.img_21.height()
                label_w = self.img_21.width()
                new_pixmap = self.q_pixmaps[1].scaled(label_w, label_h, QtCore.Qt.KeepAspectRatio)
                img_h = new_pixmap.height()
                img_w = new_pixmap.width()

            label_h, label_w, img_h, img_w = [float(label_h), float(label_w), float(img_h), float(img_w)]
            if label_w - img_w > 0:
                x -= (label_w - img_w) / 2
            elif label_h - img_h > 0:
                y -= (label_h - img_h) / 2
            else:
                raise ValueError('locating click position error')
            u = 640 * x / img_w
            v = 480 * y / img_h

        self.seq_model.update_anno(seq_list_id, self.finger_button_id - 1, u, v)
        self.update_imgs(seq_list_id)
        self.refresh_buttons()

    def refresh_buttons(self, button_id=None):
        self.finger_buttons[self.finger_button_id - 1].setChecked(False)
        if button_id is None:
            self.finger_button_id += 1
            # next item
            if self.finger_button_id > 10:
                if self.SeqListWidget.count():
                    current_item_row = self.SeqListWidget.currentRow() + 1
                    if current_item_row < self.SeqListWidget.count():
                        self.SeqListWidget.item(current_item_row).setSelected(True)
                        self.SeqListWidget.setCurrentRow(current_item_row)
                self.finger_button_id -= 10
        else:
            self.finger_button_id = button_id
        self.finger_buttons[self.finger_button_id - 1].setChecked(True)

    @QtCore.pyqtSlot(int)
    def fingerButtonClicked(self, button_id):
        self.refresh_buttons(button_id)

    @QtCore.pyqtSlot(int)
    def listWidgetOnCurrentRowChanged(self, item_id):
        if self.SeqListWidget.item(item_id) is not None:
            seq_list_id = int(self.SeqListWidget.item(item_id).text())
            self.update_imgs(seq_list_id)

    @QtCore.pyqtSlot()
    def mainDisplayBoxResized(self):
        self.show_imgs()

    @QtCore.pyqtSlot(int, int, int)
    def trackingLabelOnClicked(self, click_type, x, y):
        button_id = (click_type + 1) % 2 + 1
        camera_id = (click_type - 1) // 2 + 1
        self.update_anno(camera_id, button_id, x, y)

    @QtCore.pyqtSlot()
    def menuOpenTriggered(self):
        folder_name = QFileDialog.getExistingDirectory(self, '选择工作目录', self.cwd)
        if folder_name:
            self.seq_model.load_working_dir(folder_name)
            self.update_seq_list()

    @QtCore.pyqtSlot()
    def menuSaveTriggered(self):
        try:
            self.seq_model.save_annotation_file()
        except FileExistsError:
            QMessageBox.warning(self, '保存失败', '请检查保存目录')
            return
        QMessageBox.information(self, '保存成功', '保存成功')

    @QtCore.pyqtSlot()
    def menuExportTriggered(self):
        file_name = QFileDialog.getSaveFileName(self, '导出标注文件', self.cwd)
        try:
            self.seq_model.save_annotation_file(file_name)
        except FileExistsError:
            QMessageBox.warning(self, '保存失败', '请检查保存目录')
            return
        QMessageBox.information(self, '保存成功', '保存成功')

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        if self.SeqListWidget.count():
            self.update_seq_list_color()


def error_handler(etype, value, tb):
    error_msg = ''.join(traceback.format_exception(etype, value, tb))
    error_msg = '请截图联系管理员：\n' + error_msg
    QMessageBox.critical(None, '程序出错', error_msg)


if __name__ == '__main__':
    sys.excepthook = error_handler

    app = QApplication(sys.argv)
    main_window = MarkerAnnotationMainWindow()
    main_window.show()
    sys.exit(app.exec_())
