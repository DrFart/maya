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



# import get_scrpaths
home_dir = os.environ.get("HOME").split('/')[:3]
user_home = '{0}/{1}/{2}/'.format(home_dir[0], home_dir[1], home_dir[2])

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


# noinspection PyAttributeOutsideInit
class RigUI(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(RigUI, self).__init__(parent)
        self.setWindowTitle('Autorigger by Hsunami')
        self.setFixedSize(380, 700)
        _winstyle = ('QDialog{ \
                            padding-top: 0; \
                            background-color: #1d628c; }')
        self.setStyleSheet(_winstyle)

        self.img_path = os.path.join(user_home, 'OneDrive/scripts3/maya/hh_autorig/')
        self.img_logo = os.path.join(self.img_path, "hsunami_logo.png")
        self.logo = QtWidgets.QLabel()
        self.logo.setGeometry(0, 0, 380, 30)
        self.logo.setMinimumSize(QtCore.QSize(380, 30))
        self.logo.setMaximumSize(QtCore.QSize(380, 30))
        pixmap = QtGui.QPixmap(self.img_logo)
        self.logo.setPixmap(pixmap)

        if pm.about(ntOS=True):
            # Windows: remove ? from menu bar
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowSystemMenuHint)
        elif pm.about(macOS=True):
            # macOS: keep window on top
            self.setWindowFlags(QtCore.Qt.Tool)

        self.ui_mode = self.get_ui_mode()

        self.create_build_ui() if self.ui_mode == 'build' else self.create_control_ui()

    def get_ui_mode(self):
        # ls for rig network node with custom attrs for storing metadata
        # create new if not found
        return "build"

    def create_control_ui(self):
        return 'created control ui'

    def create_build_ui(self):
        self.create_widgets_build_ui()
        self.create_layout_build_ui()
        self.create_connections_build_ui()

    def create_widgets_build_ui(self):
        # button font
        buttonfont = QtGui.QFont('Serif', 9)
        buttonfont.setItalic(False)
        buttonfont.setBold(False)
        button_sht = ('QPushButton {  \
                                border: 1px solid black; \
                                border-radius: 3px; \
                                text-align: left; \
                                padding-left: 10; \
                                padding-right: 10; \
                                color:  #005ea1; \
                                background-color:  #b79a78;}  \
                            QPushButton:hover {  \
                                color: #005ea1;\
                                background-color: #ecc59a;} \
                            QPushButton:pressed {  \
                                color: #F2E5D5; \
                                background-color:  #345573;}')

        buildbuttonfont = QtGui.QFont('Serif', 9)
        buildbuttonfont.setItalic(False)
        buildbuttonfont.setBold(False)
        buildbutton_sht = ('QPushButton {  \
                                border: 1px solid black; \
                                border-radius: 3px; \
                                text-align: left; \
                                padding-left: 10; \
                                padding-right: 10; \
                                color:  #005ea1; \
                                background-color:  #ecc59a;}  \
                            QPushButton:hover {  \
                                color: #F2E5D5;\
                                background-color: #345573;} \
                            QPushButton:pressed {  \
                                color: #F2E5D5; \
                                background-color:  #0D0D0D;}')

        toolbuttonfont = QtGui.QFont('Serif', 7)
        toolbuttonfont.setBold(True)
        toolbutton_sht = ('QPushButton {  \
                                border: 1px solid black; \
                                border-radius: 6px; \
                                text-align: left; \
                                padding-left: 10; \
                                padding-right: 10; \
                                color:  #005ea1; \
                                background-color:  #b79a78;}  \
                            QPushButton:hover {  \
                                color: #005ea1;\
                                background-color: #ecc59a;} \
                            QPushButton:pressed {  \
                                color: #F2E5D5; \
                                background-color:  #345573;}')

        labelfont = QtGui.QFont('Serif', 11)
        label_sht = ('QLabel {  \
                      color: #e4b895; ')

        checkbox_sht = ('QCheckBox {  \
                      color: #e4b895; ')

        self.place_arm_label = QtWidgets.QLabel("Body parts")
        self.place_arm_label.setFont(labelfont)
        self.place_arm_label.setStyleSheet(label_sht + 'padding-left: 10;}')

        self.place_arm_btn = QtWidgets.QPushButton("Place Arm")
        self.place_arm_btn.setMinimumSize(120, 25)
        self.place_arm_btn.setMaximumSize(120, 25)
        self.place_arm_btn.setStyleSheet(button_sht)
        self.place_arm_btn.setFont(buttonfont)

        self.arm_fingers_label = QtWidgets.QLabel("Number of fingers:")
        self.arm_fingers_label.setStyleSheet(label_sht + 'padding-left: 4;}')
        self.arm_fingers_combobox = QtWidgets.QComboBox()
        self.arm_fingers_combobox.addItems([str(i) for i in range(1,6)])
        self.arm_fingers_combobox.setCurrentIndex(4)

        self.place_leg_btn = QtWidgets.QPushButton("Place Leg")
        self.place_leg_btn.setMinimumSize(120, 25)
        self.place_leg_btn.setMaximumSize(120, 25)
        self.place_leg_btn.setStyleSheet(button_sht)
        self.place_leg_btn.setFont(buttonfont)

        self.place_torso_btn = QtWidgets.QPushButton("Place Torso")
        self.place_torso_btn.setMinimumSize(120, 25)
        self.place_torso_btn.setMaximumSize(120, 25)
        self.place_torso_btn.setStyleSheet(button_sht)
        self.place_torso_btn.setFont(buttonfont)

        self.torso_splineIK_chk = QtWidgets.QCheckBox("SplineIK")
        self.torso_splineIK_chk.setStyleSheet(checkbox_sht + '}')
        self.torso_ribbon_chk = QtWidgets.QCheckBox("Ribbon")
        self.torso_ribbon_chk.setStyleSheet(checkbox_sht + '}')

        self.place_face_btn = QtWidgets.QPushButton("Place Face")
        self.place_face_btn.setMinimumSize(120, 25)
        self.place_face_btn.setMaximumSize(120, 25)
        self.place_face_btn.setStyleSheet(button_sht)
        self.place_face_btn.setFont(buttonfont)

        self.place_hind_leg_btn = QtWidgets.QPushButton("Place Hind Leg")
        self.place_hind_leg_btn.setMinimumSize(120, 25)
        self.place_hind_leg_btn.setMaximumSize(120, 25)
        self.place_hind_leg_btn.setStyleSheet(button_sht)
        self.place_hind_leg_btn.setFont(buttonfont)

        self.place_wing_btn = QtWidgets.QPushButton("Place Wing")
        self.place_wing_btn.setMinimumSize(120, 25)
        self.place_wing_btn.setMaximumSize(120, 25)
        self.place_wing_btn.setStyleSheet(button_sht)
        self.place_wing_btn.setFont(buttonfont)

        self.wing_fingers_label = QtWidgets.QLabel("Number of fingers:")
        self.wing_fingers_label.setStyleSheet(label_sht + 'padding-left: 4;}')
        self.wing_fingers_combobox = QtWidgets.QComboBox()
        self.wing_fingers_combobox.addItems([str(i) for i in range(1,6)])
        self.wing_fingers_combobox.setCurrentIndex(2)

        self.rig_options_label = QtWidgets.QLabel("Extra options:")
        self.rig_options_label.setFont(labelfont)
        self.rig_options_label.setStyleSheet(label_sht + 'padding-left: 10;}')

        self.stretchy_chk = QtWidgets.QCheckBox("Stretchy")
        self.stretchy_chk.setStyleSheet(checkbox_sht + 'padding-left: 10;}')

        self.bendy_chk = QtWidgets.QCheckBox("Bendy")
        self.bendy_chk.setStyleSheet(checkbox_sht + '}')

        self.buildrig_btn = QtWidgets.QPushButton("Build Rig")
        self.buildrig_btn.setMinimumSize(60, 35)
        self.buildrig_btn.setMaximumSize(60, 35)
        self.buildrig_btn.setStyleSheet(buildbutton_sht)
        self.buildrig_btn.setFont(buildbuttonfont)

        self.goback_btn = QtWidgets.QPushButton("Reset Placers")
        self.goback_btn.setMinimumSize(60, 35)
        self.goback_btn.setMaximumSize(60, 35)
        self.goback_btn.setStyleSheet(buildbutton_sht)
        self.goback_btn.setFont(buildbuttonfont)

        self.rig_tools_label = QtWidgets.QLabel("Rigging tools")
        self.rig_tools_label.setFont(labelfont)
        self.rig_tools_label.setStyleSheet(label_sht + 'padding-left: 10;}')

        self.placehold01_btn = QtWidgets.QPushButton("Tool\n01")
        self.placehold01_btn.setMinimumSize(60, 35)
        self.placehold01_btn.setMaximumSize(60, 35)
        self.placehold01_btn.setStyleSheet(toolbutton_sht)
        self.placehold01_btn.setFont(toolbuttonfont)

        self.placehold02_btn = QtWidgets.QPushButton("Tool\n02")
        self.placehold02_btn.setMinimumSize(60, 35)
        self.placehold02_btn.setMaximumSize(60, 35)
        self.placehold02_btn.setStyleSheet(toolbutton_sht)
        self.placehold02_btn.setFont(toolbuttonfont)

        self.placehold03_btn = QtWidgets.QPushButton("Tool\n03")
        self.placehold03_btn.setMinimumSize(60, 35)
        self.placehold03_btn.setMaximumSize(60, 35)
        self.placehold03_btn.setStyleSheet(toolbutton_sht)
        self.placehold03_btn.setFont(toolbuttonfont)

        self.placehold04_btn = QtWidgets.QPushButton("Tool\n04")
        self.placehold04_btn.setMinimumSize(60, 35)
        self.placehold04_btn.setMaximumSize(60, 35)
        self.placehold04_btn.setStyleSheet(toolbutton_sht)
        self.placehold04_btn.setFont(toolbuttonfont)

        self.placehold05_btn = QtWidgets.QPushButton("Tool\n05")
        self.placehold05_btn.setMinimumSize(60, 35)
        self.placehold05_btn.setMaximumSize(60, 35)
        self.placehold05_btn.setStyleSheet(toolbutton_sht)
        self.placehold05_btn.setFont(toolbuttonfont)

        self.placehold06_btn = QtWidgets.QPushButton("Tool\n06")
        self.placehold06_btn.setMinimumSize(60, 35)
        self.placehold06_btn.setMaximumSize(60, 35)
        self.placehold06_btn.setStyleSheet(toolbutton_sht)
        self.placehold06_btn.setFont(toolbuttonfont)

        self.placer_parts_in_scene_lst = QtWidgets.QListWidget()
        # write getter for placer parts in scene

        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout_build_ui(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0, 0, 0, 0)

        _layout.addWidget(self.logo)
        # _layout.setAlignment(QtCore.Qt.Aligntop())

        _layout.addWidget(self.place_arm_label)
        arm_row_layout = QtWidgets.QHBoxLayout()
        arm_row_layout.setSpacing(3)
        arm_row_layout.setContentsMargins(3, 3, 3, 3)
        arm_row_layout.addWidget(self.place_arm_btn)
        arm_row_layout.addWidget(self.arm_fingers_label)
        arm_row_layout.addWidget(self.arm_fingers_combobox)
        arm_row_layout.addStretch()
        _layout.addLayout(arm_row_layout)

        leg_row_layout = QtWidgets.QHBoxLayout()
        leg_row_layout.setSpacing(3)
        leg_row_layout.setContentsMargins(3, 3, 3, 3)
        leg_row_layout.addWidget(self.place_leg_btn)
        leg_row_layout.addWidget(self.place_hind_leg_btn)
        leg_row_layout.addStretch()
        _layout.addLayout(leg_row_layout)

        torso_row_layout = QtWidgets.QHBoxLayout()
        torso_row_layout.setSpacing(3)
        torso_row_layout.setContentsMargins(3, 3, 3, 3)
        torso_row_layout.addWidget(self.place_torso_btn)
        torso_row_layout.addWidget(self.torso_splineIK_chk)
        torso_row_layout.addWidget(self.torso_ribbon_chk)
        torso_row_layout.addStretch()
        _layout.addLayout(torso_row_layout)

        wing_row_layout = QtWidgets.QHBoxLayout()
        wing_row_layout.setSpacing(3)
        wing_row_layout.setContentsMargins(3, 3, 3, 3)
        wing_row_layout.addWidget(self.place_wing_btn)
        wing_row_layout.addWidget(self.wing_fingers_label)
        wing_row_layout.addWidget(self.wing_fingers_combobox)
        wing_row_layout.addStretch()
        _layout.addLayout(wing_row_layout)

        face_row_layout = QtWidgets.QHBoxLayout()
        face_row_layout.setSpacing(3)
        face_row_layout.setContentsMargins(3, 3, 3, 3)
        face_row_layout.addWidget(self.place_face_btn)
        face_row_layout.addStretch()
        _layout.addLayout(face_row_layout)

        _layout.addWidget(self.rig_options_label)
        body_rig_options_layout = QtWidgets.QHBoxLayout()
        body_rig_options_layout.setSpacing(20)
        body_rig_options_layout.setContentsMargins(30,3,3,3)
        body_rig_options_layout.addWidget(self.stretchy_chk)
        body_rig_options_layout.addWidget(self.bendy_chk)
        body_rig_options_layout.addStretch()
        _layout.addLayout(body_rig_options_layout)

        _layout.addWidget(self.rig_tools_label)
        _row3_layout = QtWidgets.QHBoxLayout()
        _row3_layout.setSpacing(3)
        _row3_layout.setContentsMargins(3, 3, 3, 3)
        _row3_layout.addWidget(self.placehold01_btn)
        _row3_layout.addWidget(self.placehold02_btn)
        _row3_layout.addWidget(self.placehold03_btn)
        _row3_layout.addWidget(self.placehold04_btn)
        _row3_layout.addWidget(self.placehold05_btn)
        _row3_layout.addWidget(self.placehold06_btn)
        _layout.addLayout(_row3_layout)


        _placer_list_layout = QtWidgets.QHBoxLayout()
        _placer_list_layout.addWidget(self.placer_parts_in_scene_lst)
        # _layout.addLayout(_placer_list_layout)
        _layout.addStretch()

    def create_connections_build_ui(self):
        pass
        # self.set_frame_range.clicked.connect()
        # self.asset_type_comboBox.addItems()
        # self.close_btn.clicked.connect(self.close)
        # self.mesh_list_wdg.itemClicked.connect()


# OLD UI methods
def OLDrig_UI(self, uimode):
    self.ui_window = cmds.window(self.rig_name, widthHeight=(300, 500),
                                 title=("%s Autorig v1.0 - %s" % (self.rig_name, datestamp)), vis=1)

    self.form = cmds.formLayout()

    if uimode == "build":  # BUILD MODE UI
        child1 = cmds.rowColumnLayout(numberOfColumns=2, cs=(2, 10), rs=(4, 10))

        cmds.text("RIG BUILDING MODE", align="center", rs=True)
        cmds.text(label="", align="left")

        ## SPINE PLACER ##
        cmds.text("SPINE", align="left", rs=True)
        cmds.text(label="", align="left")

        cmds.textFieldGrp('spine_verts', label='Num of Vertebrae', text='3', cw2=(100, 30), cl2=("left", "left"),
                          parent=child1)
        cmds.checkBox('spine_stretchy_checkbox', label="Stretchy", align="left")

        cmds.optionMenu('spine_controls', label="Num of Controls", w=3)
        cmds.menuItem(label='3')
        cmds.menuItem(label='4')
        cmds.menuItem(label='5')
        cmds.text(label="")

        cmds.button(label="Create Spine", command=lambda *args: self.ui_create_placer("spine", "spine",
                                                                                      int(cmds.textFieldGrp(
                                                                                          'spine_verts', query=True,
                                                                                          text=True)),
                                                                                      int(cmds.optionMenu(
                                                                                          'spine_controls', query=True,
                                                                                          value=True)),
                                                                                      cmds.checkBox(
                                                                                          'spine_stretchy_checkbox',
                                                                                          q=1, value=1)))
        cmds.text(label="", align="left")

        ## ARM PLACER ##
        cmds.text("ARMS", align="left", rs=True)
        cmds.text(label="", align="left")

        cmds.textFieldGrp('num_fingers', label='Number of Fingers', text='5', cw2=(100, 30), cl2=("left", "left"),
                          parent=child1)
        cmds.checkBox('arm_stretchy_checkbox', label="Stretchy", align="left")

        cmds.button(label="Create Arm", command=lambda *args: self.ui_create_placer("L", "arm",
                                                                                    int(cmds.textFieldGrp('num_fingers',
                                                                                                          query=True,
                                                                                                          text=True)),
                                                                                    cmds.checkBox(
                                                                                        'arm_stretchy_checkbox', q=1,
                                                                                        value=1)), align="left")
        cmds.text(label="", align="left")

        cmds.text(label="")
        cmds.text(label="")

        ## LEG PLACER ##
        cmds.text("LEGS", align="left", rs=True)
        cmds.text(label="", align="left")

        cmds.textFieldGrp('num_toes', label='Number of Toes', text='5', cw2=(100, 30), cl2=("left", "left"),
                          parent=child1)
        cmds.checkBox('leg_stretchy_checkbox', label="Stretchy", align="left")

        cmds.button(label="Create Leg", command=lambda *args: self.ui_create_placer("L", "leg",
                                                                                    int(cmds.textFieldGrp('num_toes',
                                                                                                          query=True,
                                                                                                          text=True)),
                                                                                    cmds.checkBox(
                                                                                        'leg_stretchy_checkbox', q=1,
                                                                                        value=1),
                                                                                    cmds.checkBox('leg_rfik_checkbox',
                                                                                                  q=1, value=1)))
        cmds.checkBox('leg_rfik_checkbox', label="RFIK", align="left")

        cmds.text(label="")
        cmds.text(label="")

        ## BUILD BUTTON ##
        cmds.text(label="")
        cmds.button(label="Build Rig!", height=50, command=lambda *args: self.build_rig())

        cmds.setParent('..')

    elif uimode == "control":  # CONTROL MODE UI
        cmds.text(" RIG CONTROL MODE", align="center")
        cmds.text(label=" ", align="left")
        child1 = cmds.rowColumnLayout(numberOfColumns=2, cs=(2, 10), rs=(4, 10))

        cmds.text(label=" ", align="left")
        cmds.text(label=" ", align="left")

        if cmds.objExists("%s.ikfkarms" % self.RIG_ROOT_NODE):
            for i in range(1, cmds.getAttr("%s.ikfkarms" % self.RIG_ROOT_NODE) + 1):
                self.ui_armikfkbutton(i, "ARM%s" % i)

        cmds.setParent('..')


def ui_armikfkbutton(self, x, _limb):
    cmds.button(label="L %s" % _limb, height=30, width=100, command=lambda *args: self.ikfk_switch("L", "ARM%s" % x))
    cmds.button(label="R %s" % _limb, height=30, width=100, command=lambda *args: self.ikfk_switch("R", "ARM%s" % x))


def ui_create_placer(self, side, limb, *args, **kwargs):  # callback method to create placers from UI buttons
    if limb == "arm":
        self.refresh_active_placers()
        self.arm_placers += 1
        new_arm_placer = self.build_arm_placer(side, args[1], num=self.arm_placers)
        self.placers[new_arm_placer[0]] = "arm"
        for i in range(args[0]):
            new_finger_placer = self.build_phalange_placer("%s_ARM%sFINGER%s" % (side, self.arm_placers, i), 3, "x",
                                                           "ARM%s_wrist" % self.arm_placers, "finger",
                                                           (55, 55, 10 - i * 5), side)

    elif limb == "leg":
        self.refresh_active_placers()
        self.leg_placers += 1
        new_leg_placer = self.build_leg_placer(side, args[1], args[2], num=self.leg_placers)
        # self.L_leg_toes_placer = self.build_toes_placer(side)
        self.placers[new_leg_placer[0]] = "leg"
        for i in range(args[0]):
            self.build_phalange_placer("%s_LEG%sTOE%s" % (side, self.leg_placers, i), 2, "z",
                                       "LEG%s_toe" % self.leg_placers, "toe", (2 * i + 16, 0, 25), side)

    elif limb == "spine":
        self.refresh_active_placers()
        self.spine_placer = self.build_spine_placer(args[0], args[1], [2, 2, 2], args[2])


# boilerplate
def main():
    pass
    # Show UI


if __name__ == "__main__":
    try:
        b.close()  # pylint: disable=E0601
        b.deleteLater()
    except:
        pass

    b = RigUI()
    b.show()
