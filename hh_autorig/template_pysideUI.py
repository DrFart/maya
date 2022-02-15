import os
import sys
import json
import platform

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import pymel.core as pm
import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance((main_window_ptr), QtWidgets.QWidget)

class _UI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(_UI, self).__init__(parent)
        self.setWindowTitle('Window ')
        self.setFixedSize(350, 500)

        if pm.about(ntOS=True):
            # Windows: remove ? from menu bar
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowSystemMenuHint)
        elif pm.about(macOS=True):
            # macOS: keep window on top
            self.setWindowFlags(QtCore.Qt.Tool)

        self.img_logo = os.path.join(self.img_path, "filepng")

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.asset_type_comboBox = QtWidgets.QComboBox()

        self.set_frame_range = QtWidgets.QPushButton("Set Frame Range")
        self.set_frame_range.setMinimumSize(335, 50)
        self.set_frame_range.setMaximumSize(335, 50)

        menufont = QtGui.QFont('Serif', 8)
        menufont.setItalic(True)
        menufont.setBold(True)
        self.set_frame_range.setFont(menufont)

        sht = ('QPushButton {    \
                text-align: left;\
                padding-left: 10;')
        self.set_frame_range.setStyleSheet(sht + 'color: #f8ff1f' + '}')

        self.mesh_list_wdg = QtWidgets.QListWidget()
        # for icon in sorted(self.ASSETS.keys()):
        #     self.mesh_list_wdg.addItem(' '.join(icon.split('_')))

        self.preview_image_label = QtWidgets.QLabel()
        self.preview_image_label.setMinimumSize(QtCore.QSize(256, 256))
        # pixmap = QtGui.QPixmap(self.img_logo)
        # pixmap = pixmap.scaled(QtCore.QSize(256, 256), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        # self.preview_image_label.setPixmap(pixmap)

        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(6, 6, 6, 6)

        _layout.addWidget(self.set_frame_range)

        _layout.addWidget(self.mesh_list_wdg)
        _layout.addWidget(self.preview_image_label)

    def create_connections(self):
        pass
        # self.set_frame_range.clicked.connect()
        # self.asset_type_comboBox.addItems()
        # self.close_btn.clicked.connect(self.close)
        # self.mesh_list_wdg.itemClicked.connect()



def main():
    pass
    # Show UI


if __name__ == "__main__":
    try:
        b.close()  # pylint: disable=E0601
        b.deleteLater()
    except:
        pass

    b = _UI()
    b.show()
