# # AUTORIG 2.0 By Hsunami

# # method to export/bake out bones/animation as FK skeleton
# # make Hierarchy type dropdown menu for broken or continuous hierarchy (?)
# # adjust values for current unit (working in m for LL)
# # add hind leg rig placer/build method
# # variable FK tail using phalange placer with new build method
# # Then add FK spine and IK-only leg.
# # make flexiplane spine
# # rewrite mirroring method to mirror behavior

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.OpenMayaUI as omu
import maya.api.OpenMaya as api

import math
import sys

import hh_autorig.hh_utils as hhu
import hh_autorig.widgets as w
widgets = w.Widgets()

RAD2DEG = (180/math.pi)
DEG2RAD = (math.pi/180)

class Autorig():
    def __init__(self, name="hhu_Autorig"):
         # # check units with pm.currentUnit(q=1)
        #
        # # check for network node called RIG_NAME IN CAPS

        # self.rig_name = self.rig_name.upper()
        # if pm.ls("%s" % self.rig_name):
        #     self.RIG_ROOT_NODE = pm.ls("%s" % self.rig_name)[0]
        #     if not pm.objExists("%s.uimode" % self.RIG_ROOT_NODE):
        #         pm.addAttr(self.RIG_ROOT_NODE, ln="uimode", dt="string")
        #         pm.setAttr("%s.uimode" % self.RIG_ROOT_NODE, "build")
        #
        # # if not there, create it as RIG_ROOT_NODE
        # else:
        #     self.RIG_ROOT_NODE = pm.group(name = "%s" % self.rig_name, empty=True)
        #     pm.addAttr(self.RIG_ROOT_NODE, ln="uimode", dt="string")
        #     pm.setAttr("%s.uimode" % self.RIG_ROOT_NODE, "build", type="string")
        #
        # keep list of bones
        self.rig_bones = []

        # check for placers, store in dict
        self.placers = {}
        # self.refresh_active_placers()
        #
        # # get number of placers by type (arm, leg)
        # self.arm_placers = 0
        # for placer in self.placers:
        #     if self.placers[placer] == "arm":
        #         self.arm_placers += 1
        #
        # self.leg_placers = 0
        # for placer in self.placers:
        #     if self.placers[placer] == "leg":
        #         self.leg_placers += 1
        #
        # # rebuild spine_placer object if already built
        # if pm.ls("%s_SPINE_RIG_PLACER*" % self.rig_name):
        #     self.spine_placer = []
        #
        #     _tmp_ary = []
        #     for i in range(0, pm.getAttr("%s_SPINE_RIG_PLACER.placers" % self.rig_name, size=True)):
        #         _tmp_ary.append( pm.ls(pm.getAttr("%s_SPINE_RIG_PLACER.placers[%s]" % (self.rig_name, i)))[0] )
        #     self.spine_placer.append(_tmp_ary)
        #
        #     _tmp_ary = []
        #     for i in range(0, pm.getAttr("%s_SPINE_RIG_PLACER.controlPieces" % self.rig_name, size=True)):
        #         _tmp_ary.append( pm.ls(pm.getAttr("%s_SPINE_RIG_PLACER.controlPieces[%s]" % (self.rig_name, i)))[0] )
        #     self.spine_placer.append(_tmp_ary)
        #
        #     self.spine_placer.append(pm.getAttr("%s_SPINE_RIG_PLACER.controls" % self.rig_name))
        #     self.spine_placer.append(pm.getAttr("%s_SPINE_RIG_PLACER.curve" % self.rig_name))
        #
        # if pm.getAttr("%s.uimode" % self.RIG_ROOT_NODE) == "control":
        #     self.UImode = "control"
        # elif pm.getAttr("%s.uimode" % self.RIG_ROOT_NODE) == "build":
        #     self.UImode = "build"
        #
        # if pm.window(self.rig_name, q=1, exists=1):
        #     pm.deleteUI(self.rig_name)
        # self.rig_UI(self.UImode)
        #
        # pm.select(d=True)


    # # Utility methods
    # def get_offset(self, control):
    #     return pm.listRelatives(control, parent=True)[0]
    #
    # def set_rotate_to_joint_orient(self, bone=None):
    #     if not bone:
    #         bone = pm.ls(sl=True)[0]
    #
    #     pm.setAttr("%s.rotate" % bone, pm.getAttr("%s.jointOrient" % bone))
    #     pm.setAttr("%s.jointOrient" % bone, 0, 0, 0)
    #
    # def set_joint_orient_to_rotate(self, bone=None):
    #     if not bone:
    #         bone = pm.ls(sl=True)[0]
    #     bone_rotate = pm.xform(bone, q=True, r=True, ro=True)
    #
    #     pm.setAttr("%s.jointOrient" % bone, bone_rotate[0], bone_rotate[1], bone_rotate[2])
    #     pm.setAttr("%s.rotate" % bone, 0, 0, 0)
    #
    # def add_rotate_to_joint_orient(self, bone=None):
    #     if not bone:
    #         bone = pm.ls(sl=True)[0]
    #     bone_rotate = pm.xform(bone, q=True, r=True, ro=True)
    #     bone_jo = pm.getAttr("%s.jointOrient" % bone)[0]
    #
    #     pm.setAttr("%s.jointOrient" % bone, bone_jo[0]+bone_rotate[0], bone_jo[1]-bone_rotate[2], bone_jo[2]+bone_rotate[1])
    #     pm.setAttr("%s.rotate" % bone, 0, 0, 0)
    #
    # def reset_group_node(self, placer):
    #     # to be used so that placer group node stays at 0 even if user moves it
    #     placer_children = pm.listRelatives(placer, children=True)
    #     pm.parent(placer_children, w=True)
    #     pm.xform(placer, ws=True, t=(0,0,0))
    #     pm.parent(placer_children, placer)
    #     pm.select(d=True)
    #
    # def orient_joint_chain(self, root_bone, side="L"):
    #     if side == "L":
    #         pm.joint(root_bone, e=True, oj="xyz", sao="yup", ch=True, zso=True)
    #     else:
    #         pm.joint(root_bone, e=True, oj="xyz", sao="ydown", ch=True, zso=True)
    #
    # def refresh_active_placers(self):
    #     self.placers = {}
    #     self.arm_placers = 0
    #     self.leg_placers = 0
    #
    #     for node in pm.ls(exactType="transform"):
    #         if pm.objExists("%s.placertype" % node):
    #             self.placers[node] = pm.getAttr("%s.placertype" % node)
    #             if self.placers[node] == 'arm':
    #                 self.arm_placers += 1
    #             if self.placers[node] == 'leg':
    #                 self.leg_placers += 1
    #
    # def lock_attrs(self, control, attrs, lock=1):
    #     for i in range (0, len(attrs)):
    #         if lock == 0:
    #             pm.setAttr("%s.%s" % (control, attrs[i]), lock=0, keyable=0, channelBox=0)
    #         elif lock==1:
    #             pm.setAttr("%s.%s" % (control, attrs[i]), lock=1, keyable=0, channelBox=0)
    #
    # def clear_placer_scale(self, group):
    #     _nodes = pm.listRelatives(group)
    #     _tmp_grp = pm.group(name="_tmp_grp", em=1, w=1)
    #     pm.parent(_nodes, _tmp_grp)
    #     pm.makeIdentity(group, a=1, t=0, r=0, s=1)
    #     pm.parent(_nodes, group)
    #     pm.delete(_tmp_grp)
    #
    #     for node in _nodes:
    #         if node[-12:] == '_proxy_curve':
    #             pm.setAttr('%s.t' % node, 0,0,0)
    #             pm.setAttr('%s.r' % node, 0,0,0)
    #
    # Placer creation methods
    def build_arm_placer(self, side, stretchy, num=1):
        _arm_pieces = []
        arm_placer_group = pm.group(name="%s_RIG_PLACER" % side, empty=True)

        # create clavicle, shoulder, elbow, wrist, bones
        clavicle_bone_placer = pm.createNode('joint', n="clavicle_%s" % side)
        clavicle_bone_placer.displayLocalAxis.set(1)
        pm.xform(clavicle_bone_placer, r=False, ws=True, t=(20, 0, 100 ))
        pm.xform(arm_placer_group, ws=1, t=( pm.xform(clavicle_bone_placer, ws=1, q=1, t=1) ))
        _arm_pieces.append(clavicle_bone_placer)

        shoulder_bone_placer = pm.createNode('joint', n="shoulder_%s" % side)
        shoulder_bone_placer.displayLocalAxis.set(1)
        pm.xform(shoulder_bone_placer, r=False, ws=True, t=(30, 0, 100))
        _arm_pieces.append(shoulder_bone_placer)

        elbow_bone_placer = pm.createNode('joint', n="elbow_%s" % side)
        elbow_bone_placer.displayLocalAxis.set(1)
        pm.xform(elbow_bone_placer, r=False, ws=True, t=(50, 5, 100))
        _arm_pieces.append(elbow_bone_placer)

        wrist_bone_placer = pm.createNode('joint', n="wrist_%s" % side)
        wrist_bone_placer.displayLocalAxis.set(1)
        pm.xform(wrist_bone_placer, r=False, ws=True, t=(70, 0, 100))
        _arm_pieces.append(wrist_bone_placer)

        pm.parent(shoulder_bone_placer, clavicle_bone_placer)
        pm.parent(elbow_bone_placer, shoulder_bone_placer)
        pm.parent(wrist_bone_placer, elbow_bone_placer)

        # create cube control at clav, shoulder, elbow, wrist
        clavicle_control_placer = widgets.create_circle_control("%s_clavicle_control_placer" % side, scale=[6,6,6])
        shoulder_control_placer = widgets.create_circle_control("%s_shoulder_control_placer" % side, scale=[10,10,10])
        elbow_control_placer = widgets.create_circle_control("%s_elbow_control_placer" % side, scale=[8,8,8])
        wrist_control_placer = widgets.create_circle_control("%s_wrist_control_placer" % side, scale=[6,6,6])

        # create cube control for hand IK, cone control for pole vector  IK_hand_control_placer
        IK_hand_control_placer = widgets.create_cube_control(("%s_IK_control_placer" % side), [1, 3, 3])
        hhu.snap_t(IK_hand_control_placer, wrist_bone_placer)

        arm_pole_vector_placer = widgets.create_cube_control("%s_pole_vector_placer" % side, scale=[.75,.75,.75])
        hhu.snap_t(arm_pole_vector_placer, elbow_bone_placer)
        arm_pole_vector_placer.setTranslation(arm_pole_vector_placer.getTranslation() + (0, 20, 0), ws=0)
        # arm_pole_vector_placer.move(0,35,0)

        # parent constrain to respective bone
        pm.parentConstraint(clavicle_bone_placer, clavicle_control_placer, name="_tmp_cnst")
        pm.delete("_tmp_cnst")
        pm.parentConstraint(clavicle_bone_placer, clavicle_control_placer)

        pm.parentConstraint(shoulder_bone_placer, shoulder_control_placer, name="_tmp_cnst")
        pm.delete("_tmp_cnst")
        pm.parentConstraint(shoulder_bone_placer, shoulder_control_placer)

        pm.parentConstraint(elbow_bone_placer, elbow_control_placer, name="_tmp_cnst")
        pm.delete("_tmp_cnst")
        pm.parentConstraint(elbow_bone_placer, elbow_control_placer)

        pm.parentConstraint(wrist_bone_placer, wrist_control_placer, name="_tmp_cnst")
        pm.delete("_tmp_cnst")
        pm.parentConstraint(wrist_bone_placer, wrist_control_placer)

        # pm.parentConstraint(palm_bone_placer, palm_control_placer, name="_tmp_cnst")
        # pm.delete("_tmp_cnst")
        # pm.parentConstraint(palm_bone_placer, palm_control_placer)

        pm.parent(clavicle_bone_placer, clavicle_control_placer, shoulder_control_placer,
        elbow_control_placer, wrist_control_placer, IK_hand_control_placer, arm_pole_vector_placer, arm_placer_group)
        pm.select(d=True)
        # pm.setAttr("%s.t" % _arm_proxy_curve, 0,0,0)
        # pm.setAttr("%s.r" % _arm_proxy_curve, 0,0,0)
        _arm_pieces.insert(0, arm_placer_group)

        # store placer metadata in placer root node
        pm.addAttr(arm_placer_group, ln="placers", dt="string", m=True)
        i=0
        for _piece in _arm_pieces:
            pm.setAttr("%s.placers[%s]" % (arm_placer_group, i), _piece, type="string")
            i += 1

        pm.addAttr(arm_placer_group, ln="placertype", dt="string")        # type of placer (arm, leg, etc.)
        pm.setAttr("%s.placertype" % arm_placer_group, "arm", type="string")

        pm.addAttr(arm_placer_group, ln="connector", dt="string")        # where placer connects (spine, etc.)
        pm.setAttr("%s.connector" % arm_placer_group, "spine3", type="string")
        # pm.setAttr("%s.connector" % arm_placer_group, "%s_spine3" % self.rig_name, type="string")

        pm.addAttr(arm_placer_group, ln="stretchy", at="bool")        # stretchiness flag
        pm.setAttr("%s.stretchy" % arm_placer_group, stretchy)

        self.placers[arm_placer_group] = pm.getAttr("%s.placertype" % arm_placer_group)    # add placer to dict
        pm.select(d=1)

        return _arm_pieces
    #
    # def build_leg_placer(self, side, stretchy, rfik, num=1):
    #     _leg_pieces = []
    #     side = "%s_%s_LEG%s" % (self.rig_name, side, num)
    #     leg_placer_group = pm.group(name="%s_RIG_PLACER" % side, empty=True)
    #
    #     # create hip, knee, ankle, pointer placer bones
    #     hip_bone_placer = widgets.create_circle_control("%s_hip_bone_placer" % side, scale=[3,3,3])
    #     pm.xform(hip_bone_placer, r=False, ws=True, t=(20, 70, 0))
    #     pm.xform(leg_placer_group, ws=1, t=( pm.xform(hip_bone_placer, ws=1, q=1, t=1) ))
    #     _leg_pieces.append(hip_bone_placer)
    #
    #     knee_bone_placer = widgets.create_circle_control("%s_knee_bone_placer" % side, scale=[3,3,3])
    #     pm.xform(knee_bone_placer, r=False, ws=True, t=(20, 40, 20))
    #     _leg_pieces.append(knee_bone_placer)
    #
    #     ankle_bone_placer = widgets.create_circle_control("%s_ankle_bone_placer" % side, scale=[3,3,3])
    #     pm.xform(ankle_bone_placer, r=False, ws=True, t=(20, 10, 0))
    #     _leg_pieces.append(ankle_bone_placer)
    #
    #     ball_bone_placer = widgets.create_circle_control("%s_ball_bone_placer" % side, scale=[3,3,3])
    #     pm.xform(ball_bone_placer, r=False, ws=True, t=(20, 4, 6))
    #     _leg_pieces.append(ball_bone_placer)
    #
    #     toe_bone_placer = widgets.create_circle_control("%s_toe_bone_placer" % side, scale=[3,3,3])
    #     pm.xform(toe_bone_placer, r=False, ws=True, t=(20, 0, 15))
    #     _leg_pieces.append(toe_bone_placer)
    #
    #     toe_pointer_placer = widgets.create_circle_control("%s_toepointer_placer" % side, scale=[3,3,3])
    #     pm.xform(toe_pointer_placer, r=False, ws=True, t=(20, 0, 20))
    #     _leg_pieces.append(toe_pointer_placer)
    #
    #     _leg_proxy_curve = pm.curve(d=1,
    #                 p=[(1, 0, 1),
    #                 (3, 0, 1),
    #                 (5, 0, 1),
    #                 (7, 0, 1),
    #                 (9, 0, 1),
    #                 (11,0, 1)],
    #                 k=[0, 1, 2, 3, 4, 5],
    #                 name="_%s_leg_proxy_curve" % side)
    #
    #     # make cluster at each CV
    #     _number_of_cvs = pm.getAttr("%s.degree" % _leg_proxy_curve) + pm.getAttr("%s.spans" % _leg_proxy_curve)
    #     for i in range(0, _number_of_cvs):
    #         pm.select("%s.cv[%s]" % (_leg_proxy_curve, i))
    #         _cluster = pm.cluster(name="_%s_placer_cluster_%s" % (side, i))
    #         pm.pointConstraint(_leg_pieces[i], _cluster)
    #         pm.hide(_cluster)
    #
    #     pm.setAttr("%s.overrideEnabled" % _leg_proxy_curve, 1)
    #     pm.setAttr("%s.overrideDisplayType" % _leg_proxy_curve, 2)
    #     pm.setAttr("%s.inheritsTransform" % _leg_proxy_curve, 0)
    #
    #
    #     # create cube control at clav, hip, knee, ankle, ball, toe
    #     hip_control_placer = widgets.create_cube_control("%s_hip_control_placer" % side, scale=[3,3,3])
    #     knee_control_placer = widgets.create_cube_control("%s_knee_control_placer" % side, scale=[3,3,3])
    #     ankle_control_placer = widgets.create_cube_control("%s_ankle_control_placer" % side, scale=[2,2,2])
    #     ball_control_placer = widgets.create_cube_control("%s_ball_control_placer" % side, scale=[3,1.5,1.5])
    #     toe_control_placer = widgets.create_cube_control("%s_toe_control_placer" % side, scale=[3,1.5,1.5])
    #
    #     # create cube control for RFIK, IK control, total foot control, and pole vector
    #     RFIK_leg_control_placer = widgets.create_cube_control("%s_RFIK_control_placer" % side, [3,.5,6])
    #     IK_leg_control_placer = widgets.create_cube_control("%s_IK_control_placer" % side, [3,3,3])
    #     leg_pole_vector_placer = widgets.create_cube_control("%s_pole_vector_placer" % side, scale=[1.5, .5, 1.5])
    #     foot_control_placer = widgets.create_cube_control("%s_foot_control_placer" % side, [4.5,3,8])
    #
    #     # parent constrain to respective bone
    #     pm.parentConstraint(hip_bone_placer, hip_control_placer, name="_tmp_cnst")
    #     pm.delete("_tmp_cnst")
    #     pm.parentConstraint(hip_bone_placer, hip_control_placer)
    #
    #     pm.parentConstraint(knee_bone_placer, knee_control_placer, name="_tmp_cnst")
    #     pm.delete("_tmp_cnst")
    #     pm.parentConstraint(knee_bone_placer, knee_control_placer)
    #
    #     pm.parentConstraint(ankle_bone_placer, ankle_control_placer, name="_tmp_cnst")
    #     pm.delete("_tmp_cnst")
    #     pm.parentConstraint(ankle_bone_placer, ankle_control_placer)
    #
    #     pm.parentConstraint(ball_bone_placer, ball_control_placer, name="_tmp_cnst")
    #     pm.delete("_tmp_cnst")
    #     pm.parentConstraint(ball_bone_placer, ball_control_placer)
    #
    #     pm.parentConstraint(toe_bone_placer, toe_control_placer, name="_tmp_cnst")
    #     pm.delete("_tmp_cnst")
    #     pm.parentConstraint(toe_bone_placer, toe_control_placer)
    #
    #     # move IK and RFIK controllers to default starting position
    #     pm.xform(RFIK_leg_control_placer, ws=1, t=( pm.xform(toe_control_placer, q=1, ws=1, t=1) ))
    #     pm.xform(IK_leg_control_placer, ws=1, t=( pm.xform(ankle_control_placer, q=1, ws=1, t=1) ))
    #     # pm.setAttr("%s.v" % leg_pole_vector_placer, 0)
    #     pm.xform(foot_control_placer, ws=1, t=( pm.xform(ball_control_placer, q=1, ws=1, t=1) ))
    #
    #     # put everything in a placer group
    #     pm.parent(pm.ls("_%s_placer_cluster*Handle" % side), hip_bone_placer, knee_bone_placer, ankle_bone_placer,
    #             ball_bone_placer, toe_bone_placer, toe_pointer_placer, hip_control_placer, knee_control_placer, ankle_control_placer,
    #             ball_control_placer, toe_control_placer, _leg_proxy_curve, IK_leg_control_placer, RFIK_leg_control_placer,
    #             leg_pole_vector_placer, foot_control_placer, leg_placer_group)
    #     pm.select(d=True)
    #     pm.setAttr("%s.t" % _leg_proxy_curve, 0,0,0)
    #     pm.setAttr("%s.r" % _leg_proxy_curve, 0,0,0)
    #     _leg_pieces.insert(0, leg_placer_group)
    #
    #     # store placer metadata in placer root node
    #     pm.addAttr(leg_placer_group, ln="placers", dt="string", m=True)
    #     i=0
    #     for _piece in _leg_pieces:
    #         pm.setAttr("%s.placers[%s]" % (leg_placer_group, i), _piece, type="string")
    #         i += 1
    #
    #     pm.addAttr(leg_placer_group, ln="placertype", dt="string")        # type of placer (arm, leg, etc.)
    #     pm.setAttr("%s.placertype" % leg_placer_group, "leg", type="string")
    #
    #     pm.addAttr(leg_placer_group, ln="connector", dt="string")        # where placer connects (spine, etc.)
    #     pm.setAttr("%s.connector" % leg_placer_group, "%s_pelvis_control" % self.rig_name, type="string")
    #
    #     pm.addAttr(leg_placer_group, ln="stretchy", at="bool")        # stretchiness flag
    #     pm.setAttr("%s.stretchy" % leg_placer_group, stretchy)
    #
    #     self.placers[leg_placer_group] = pm.getAttr("%s.placertype" % leg_placer_group)    # add placer to dict
    #
    #     return _leg_pieces
    #
    # def build_phalange_placer(self, name, joints, pointing, connector, phalange_type, start_pos=(0,0,0), side="L"):
    #     pm.select(d=1)
    #     phalange_placer_group = pm.group(name="%s_%s_PLACER" % (self.rig_name, name), empty=True)
    #     pm.addAttr(phalange_placer_group, ln="placers", dt="string", m=True)
    #     pm.setAttr("%s.placers[0]" % phalange_placer_group, phalange_placer_group, type="string")
    #     pm.xform(phalange_placer_group, ws=1, t=(start_pos))
    #     phalange_pieces = []
    #
    #     _parms = []
    #     _knots = []
    #
    #     prev_placer = phalange_placer_group
    #     for i in range(0, joints + 1):
    #         phalange_placer = widgets.create_circle_control("%s_%s_%s_bone_placer" % (self.rig_name, name, i), scale=[1,1,1])
    #         _tmp_cnst = pm.parentConstraint(prev_placer, phalange_placer, mo=False)
    #         pm.delete(_tmp_cnst)
    #
    #         if i < joints:
    #             control_placer = widgets.create_cube_control("%s_%s_%s_control_placer" % (self.rig_name, name, i), scale=[1,1,1])
    #             pm.parentConstraint(phalange_placer, control_placer, name="_tmp_cnst")
    #             pm.delete("_tmp_cnst")
    #             pm.parentConstraint(phalange_placer, control_placer)
    #             pm.parent(control_placer, phalange_placer_group)
    #
    #         if pointing == "x":
    #             pm.move(2, 0, 0, phalange_placer, r=True)
    #             if i < joints: pm.scale(.2, 1, 1, control_placer, r=1)
    #         elif pointing == "y":
    #             pm.move(0, 2, 0, phalange_placer, r=True)
    #             if i < joints: pm.scale(1, .2, 1, control_placer, r=1)
    #         elif pointing == "z":
    #             pm.move(0, 0, 2, phalange_placer, r=True)
    #             if i < joints: pm.scale(1, 1, .2, control_placer, r=1)
    #
    #         pm.parent(phalange_placer, phalange_placer_group)
    #         phalange_pieces.append(phalange_placer)
    #         pm.setAttr("%s.placers[%s]" % (phalange_placer_group, i+1), phalange_placer, type="string")
    #
    #         _parms.append((0, i+1, 0))
    #         _knots.append(i+1)
    #
    #         prev_placer = phalange_placer
    #
    #     _phalange_proxy_curve = pm.curve(d=1,
    #         p=_parms,
    #         k=_knots,
    #         name="_%s_%s_proxy_curve" % (self.rig_name, name))
    #
    #     pm.setAttr("%s.overrideEnabled" % _phalange_proxy_curve, 1)
    #     pm.setAttr("%s.overrideDisplayType" % _phalange_proxy_curve, 2)
    #     pm.setAttr("%s.inheritsTransform" % _phalange_proxy_curve, 0)
    #
    #     pm.parent(_phalange_proxy_curve, phalange_placer_group)
    #
    #     # make cluster at each CV
    #     #_number_of_cvs = pm.getAttr("%s.degree" % _phalange_proxy_curve) + pm.getAttr("%s.spans" % _phalange_proxy_curve)
    #     for i in range(0, joints+1):
    #         pm.select("%s.cv[%s]" % (_phalange_proxy_curve, i))
    #         _cluster = pm.cluster(name="%s_%s_placer_cluster_%s" % (self.rig_name, name, i))
    #         pm.pointConstraint(phalange_pieces[i], _cluster)
    #         pm.hide(_cluster)
    #         pm.parent(_cluster[1], phalange_placer_group)
    #         pm.select(d=1)
    #
    #     phalange_pieces.insert(0, phalange_placer_group)
    #
    #     pm.addAttr(phalange_placer_group, ln="placertype", dt="string")        # type of placer (arm, leg, etc.)
    #     pm.setAttr("%s.placertype" % phalange_placer_group, phalange_type, type="string")
    #
    #     pm.addAttr(phalange_placer_group, ln="connector", dt="string")        # where placer connects (spine, etc.)
    #     pm.setAttr("%s.connector" % phalange_placer_group, "%s_%s_%s" % (self.rig_name, side, connector), type="string")
    #
    #     self.placers[phalange_placer_group] = pm.getAttr("%s.placertype" % phalange_placer_group)    # add placer to dict
    #
    #     return phalange_pieces
    #
    # def build_hindleg_placer(self, side="L"):
    #     # create 4 placers (hip, knee01, knee02, ankle)
    #
    #     pass
    #
    # def build_spine_placer(self, vertebrae, controls, scale, stretchy):
    #     _spine_pieces = []
    #     _control_pieces = []
    #     _parms = [(0,0,0), (0,0,0)]
    #     _knots = [-2,-1]
    #     spine_placer_group = pm.group(name="%s_SPINE_RIG_PLACER" % self.rig_name, empty=True)
    #
    #     # create pelvis, COG, and spine placer bones and controls
    #     pelvis_bone_placer = widgets.create_circle_control("%s_pelvis_bone_placer" % self.rig_name, scale=[3,3,3])
    #     pm.xform(pelvis_bone_placer, r=False, ws=True, t=(0, 60, 0))
    #     _spine_pieces.append(pelvis_bone_placer)
    #
    #     root_bone_placer = widgets.create_circle_control("%s_root_bone_placer" % self.rig_name, scale=[4.5, 4.5, 4.5])
    #     pm.xform(root_bone_placer, r=False, ws=True, t=(0, 60, 0))
    #     _spine_pieces.append(root_bone_placer)
    #     pm.parentConstraint(root_bone_placer, pelvis_bone_placer, mo=True)
    #
    #     root_control_placer = widgets.create_cube_control("%s_root_control_placer" % self.rig_name, scale=[5,15,3])
    #     _tmp_cnst = pm.parentConstraint(pelvis_bone_placer, root_control_placer, mo=False, name="_tmp_cnst")
    #     pm.delete(_tmp_cnst)
    #     pm.xform(root_control_placer, r=False, ws=True, t=(0, 75, -35))
    #     pm.parentConstraint(pelvis_bone_placer, root_control_placer, mo=True)
    #     _control_pieces.append(root_control_placer)
    #
    #     pelvis_control_placer = widgets.create_pelvis_control("%s_pelvis_control_placer" % self.rig_name, scale=.5)
    #     _tmp_cnst = pm.parentConstraint(pelvis_bone_placer, pelvis_control_placer, mo=False, name="_tmp_cnst")
    #     pm.delete(_tmp_cnst)
    #     pm.parentConstraint(pelvis_bone_placer, pelvis_control_placer)
    #     _control_pieces.append(pelvis_control_placer)
    #
    #     #create bone placers
    #     spine_y = 60
    #     for i in range(0, vertebrae + 1):
    #         if (i == vertebrae):
    #             neck_placer = widgets.create_circle_control("%s_neck_bone_placer" % self.rig_name, scale=[3,3,3])
    #             neck_y = (20 + spine_y)
    #             pm.xform(neck_placer, r=False, ws=True, t=(0, neck_y, 0))
    #             _spine_pieces.append(neck_placer)
    #             _parms.append((0, i+1, 0))
    #             _knots.append(i+1)
    #             # create cube control
    #             neck_control_placer = widgets.create_cube_control("%s_neck_control_placer" % self.rig_name, [4, 1, 4])
    #             # parent constrain to neck bone
    #             _tmp_cnst = pm.parentConstraint(neck_placer, neck_control_placer, mo=False, name="_tmp_cnst")
    #             pm.delete(_tmp_cnst)
    #             pm.parentConstraint(neck_placer, neck_control_placer)
    #             _control_pieces.append(neck_control_placer)
    #             pm.parent(neck_placer, neck_control_placer, spine_placer_group)
    #
    #             head_placer = widgets.create_circle_control("%s_head_bone_placer" % self.rig_name, scale=[3,3,3])
    #             head_y = (10 + neck_y)
    #             pm.xform(head_placer, r=False, ws=True, t=(0, head_y, 0))
    #             _spine_pieces.append(head_placer)
    #             _parms.append((0, i+2, 0))
    #             _knots.append(i+2)
    #             # create cube control
    #             head_control_placer = widgets.create_cube_control("%s_head_control_placer" % self.rig_name, [2, .5, 2])
    #             # parent constrain to neck bone
    #             _tmp_cnst = pm.parentConstraint(head_placer, head_control_placer, mo=False, name="_tmp_cnst")
    #             pm.delete(_tmp_cnst)
    #             pm.parentConstraint(head_placer, head_control_placer)
    #             _control_pieces.append(head_control_placer)
    #             pm.parent(head_placer, head_control_placer, spine_placer_group)
    #
    #         else:
    #             spine_placer = widgets.create_circle_control("%s_spine%s_bone_placer" % (self.rig_name, (i + 1)), scale=[3,3,3])
    #             spine_y = ((40/vertebrae) + spine_y)
    #             pm.xform(spine_placer, r=False, ws=True, t=(0, spine_y, 0))
    #
    #             pm.parent(spine_placer, spine_placer_group)
    #             _spine_pieces.append(spine_placer)
    #             _parms.append((0, i+1, 0))
    #             _knots.append(i+1)
    #
    #     ##create control placers for spine
    #     spine_y = 60
    #     for i in range(0, controls):
    #         control_placer = widgets.create_cube_control("%s_spine%s_control_placer" % (self.rig_name, (i + 1)), scale=[9, 3, 5])
    #         spine_y = ((40/3) + spine_y)
    #         pm.xform(control_placer, r=False, ws=True, t=(0, spine_y, 0))
    #         pm.parent(control_placer, spine_placer_group)
    #
    #     _spine_proxy_curve = pm.curve(d=1,
    #         p=_parms,
    #         k=_knots,
    #         name="_spine_proxy_curve")
    #
    #     # make cluster at each CV
    #     _number_of_cvs = pm.getAttr("%s.degree" % _spine_proxy_curve) + pm.getAttr("%s.spans" % _spine_proxy_curve)
    #     for i in range(0, _number_of_cvs):
    #         pm.select("%s.cv[%s]" % (_spine_proxy_curve, i))
    #         _cluster = pm.cluster(name="spine_placer_cluster_%s" % i)
    #         pm.pointConstraint(_spine_pieces[i], _cluster)
    #         pm.hide(_cluster)
    #
    #     pm.setAttr("%s.overrideEnabled" % _spine_proxy_curve, 1)
    #     pm.setAttr("%s.overrideDisplayType" % _spine_proxy_curve, 2)
    #     pm.setAttr("%s.inheritsTransform" % _spine_proxy_curve, 0)
    #
    #     # put everything in a placer group
    #     _spine_pieces.insert(0, spine_placer_group)
    #     pm.parent(pm.ls("spine_placer_cluster*Handle"), _spine_proxy_curve, root_control_placer,
    #                         pelvis_control_placer, pelvis_bone_placer, root_bone_placer, spine_placer_group)
    #     pm.select(d=True)
    #
    #     # create world control
    #     world_control_placer = widgets.create_four_way_arrow_control("%s_world_control_placer" % self.rig_name, scale=[1,1,1])
    #     pm.parent(world_control_placer, spine_placer_group)
    #     _control_pieces.append(world_control_placer)
    #
    #     # store placers in multi attr in pelvis node
    #     pm.addAttr(spine_placer_group, ln="placers", dt="string", m=True)
    #     i=0
    #     for _piece in _spine_pieces:
    #         pm.setAttr("%s.placers[%s]" % (spine_placer_group, i), _piece, type="string")
    #         i += 1
    #     # store control pieces in attr
    #     pm.addAttr(spine_placer_group, ln="controlPieces", dt="string", m=True)
    #     i=0
    #     for _piece in _control_pieces:
    #         pm.setAttr("%s.controlPieces[%s]" % (spine_placer_group, i), _piece, type="string")
    #         i += 1
    #
    #     # store spine controls in attr
    #     pm.addAttr(spine_placer_group, ln="controls", m=False)
    #     pm.setAttr("%s.controls" % spine_placer_group, controls)
    #
    #     pm.addAttr(spine_placer_group, ln="curve", dt="string", m=False)
    #     pm.setAttr("%s.curve" % spine_placer_group, _spine_proxy_curve, type="string")
    #     pm.select(d=1)
    #
    #     pm.addAttr(spine_placer_group, ln="stretchy", at="bool")        # stretchiness flag
    #     pm.setAttr("%s.stretchy" % spine_placer_group, stretchy)
    #
    #     return [(_spine_pieces), (_control_pieces), controls, _spine_proxy_curve ]
    #
    #
    # # Face Rig Placers
    # def build_lip_placer(self, position, numbones):
    #     pass
    #     # build curve, create numbones
    #     # motion path all bones
    #     # evenly space bones apart on U-pos
    #
    #
    # # Rig Building utility methods
    # def build_bones(self, side, limb, placers):
    #     pm.select(d=True)
    #     returnbones = []
    #
    #     for placer in placers:
    #         # build bone at placer
    #         if side is not "middle":
    #             bonename = placer.split("_")[3]
    #             bone = pm.joint(name=("%s_%s_%s_%s" % (self.rig_name, side, limb, bonename)))
    #         elif side is "middle":
    #             bonename = placer.split("_")[1]
    #             bone = pm.joint(name=("%s_%s" % (self.rig_name, bonename)))
    #         pm.xform(bone, ws=True, t=(pm.xform(placer, q=True, ws=True, t=True)))
    #         returnbones.append(bone)
    #
    #         # duplicate and constraint bone control
    #         control_placer = placer.replace("bone", "control")
    #         if pm.ls(control_placer):
    #             control = pm.duplicate(control_placer, renameChildren=True, name=control_placer.rstrip("placer")[0:-1])
    #             if pm.listRelatives(control, type="constraint"):
    #                 pm.delete(pm.listRelatives(control, type="constraint"))
    #
    #     if side is not "middle":
    #         rig_offset = pm.createNode("transform", name="%s_%s_%s_RIG_OFFSET" % (self.rig_name, side, limb))
    #         rig_group = pm.createNode("transform", name="%s_%s_%s_RIG" % (self.rig_name, side, limb))
    #         bones_group = pm.createNode("transform", name="%s_%s_%s_BONES" % (self.rig_name, side, limb))
    #     elif side is "middle":
    #         rig_offset = pm.createNode("transform", name="%s_%s_RIG_OFFSET" % (self.rig_name, limb))
    #         rig_group = pm.createNode("transform", name="%s_%s_RIG" % (self.rig_name, limb))
    #         bones_group = pm.createNode("transform", name="%s_%s_BONES" % (self.rig_name, limb))
    #
    #
    #     pm.xform(rig_offset, pivots=pm.xform(returnbones[0], q=True, ws=True, t=True))
    #     pm.xform(rig_group, pivots=pm.xform(returnbones[0], q=True, ws=True, t=True))
    #     pm.parent(rig_group, self.RIG_ROOT_NODE)
    #     pm.parent(rig_offset, rig_group)
    #     pm.parent(returnbones[0], bones_group)
    #     pm.parent(bones_group, rig_offset)
    #
    #     # copy IK curve controls but don't parent to bone shape yet
    #     if pm.ls("%s_%s_%s_IK_control_placer" % (self.rig_name, side, limb)):
    #         IK_control_placer = pm.ls("%s_%s_%s_IK_control_placer" % (self.rig_name, side, limb))
    #         IK_control = pm.duplicate(IK_control_placer, name=("%s_%s_%s_IK_control" % (self.rig_name, side, limb)))
    #         pm.parent(IK_control[0], rig_offset)
    #
    #         pole_vector_placer = pm.ls("%s_%s_%s_pole_vector_placer" % (self.rig_name, side, limb))
    #         pole_vector = pm.duplicate(pole_vector_placer, name="%s_%s_%s_pole_vector" % (self.rig_name, side, limb))
    #         pm.parent(pole_vector[0], rig_offset)
    #
    #     if pm.ls("%s_%s_%s_foot_control_placer" % (self.rig_name, side, limb)):
    #         foot_control = pm.duplicate(pm.ls("%s_%s_%s_foot_control_placer" % (self.rig_name, side, limb)),
    #                       name="%s_%s_%s_foot_control" % (self.rig_name, side, limb))
    #         pm.parent(foot_control[0], rig_offset)
    #
    #     returnbones.insert(0, rig_group)
    #     returnbones.insert(1, rig_offset)
    #     returnbones.insert(2, bones_group)
    #
    #     return returnbones
    #
    # def mirror_placer(self, source_placer):
    #     if source_placer[0].split("%s_" % self.rig_name)[1][0] == "L":
    #         side = "%s_L_" % self.rig_name
    #         opposite = "%s_R_" % self.rig_name
    #     else:
    #         side = "%s_R_" % self.rig_name
    #         opposite = "%s_L_" % self.rig_name
    #
    #     if (pm.getAttr('%s.scale' % source_placer[0])[0] != (1,1,1)) or (pm.getAttr('%s.scale' % source_placer[0])[0] != (1,1,1)):
    #         self.clear_placer_scale(source_placer[0])
    #
    #     new_placer = pm.duplicate(source_placer, rr=False, renameChildren=True)
    #     pm.setAttr("%s.sx" % new_placer[0], -1)
    #     # pm.setAttr("%s.tx" % new_placer[0], (pm.xform(source_placer[1], ws=1, q=1, t=1)[0] * -1))
    #     pm.setAttr("%s.ry" % new_placer[0], (pm.xform(source_placer[1], ws=1, q=1, ro=1)[1] * -1))
    #     pm.setAttr("%s.rz" % new_placer[0], (pm.xform(source_placer[1], ws=1, q=1, ro=1)[2] * -1))
    #
    #     for node in new_placer:
    #         newName = node.replace(side, opposite)
    #         newName = newName[:-1]
    #         pm.rename(node, newName)
    #
    #     mirrored_placers = []
    #
    #     for node in source_placer:
    #         if node.replace(side, opposite):
    #             mirrored_placers.append(node.replace(side, opposite))
    #
    #     return mirrored_placers
    #
    # def mirror_bones(self, bone_chain_root, placers=None):
    #     if bone_chain_root.split('_')[1] == "L":
    #         side = "R"
    #     else:
    #         side = "L"
    #     limb = bone_chain_root.split('_')[2]
    #     bone = bone_chain_root.split('_')[3]
    #     mirrored_bones = []
    #
    #     # select bone_chain_root
    #     pm.select(bone_chain_root, r=1)
    #     # mirror in YZ and copy behavior
    #     mirrored_joint_chain = pm.mirrorJoint(bone_chain_root, mirrorYZ=1, mirrorBehavior=1, searchReplace=("L_", "R_"))
    #     # make group nodes: rigName_side_limb_RIG
    #     #                   rigName_side_limb_RIG_OFFSET
    #     #                   rigName_side_limb_BONES
    #
    #     rig_group =   pm.group(name="%s_%s_%s_RIG" % (self.rig_name, side, limb), w=1, em=1)
    #     rig_offset =  pm.group(name="%s_%s_%s_RIG_OFFSET" % (self.rig_name, side, limb), w=1, em=1)
    #     bones_group = pm.group(name="%s_%s_%s_BONES" % (self.rig_name, side, limb), w=1, em=1)
    #
    #     mirrored_bones.append(rig_group)
    #     mirrored_bones.append(rig_offset)
    #     mirrored_bones.append(bones_group)
    #     for bone in mirrored_joint_chain:
    #         mirrored_bones.append(bone)
    #
    #     pm.parent(bones_group, rig_offset)
    #     pm.parent(rig_offset, rig_group)
    #     pm.parent(mirrored_joint_chain[0], bones_group)
    #
    #     # duplicate and constraint bone controls
    #     for placer in placers:
    #         control_placer = placer.replace("bone", "control")
    #         print(control_placer)
    #         if pm.ls(control_placer):
    #             control = pm.duplicate(control_placer, renameChildren=True, name=control_placer.rstrip("placer")[0:-1])
    #             if pm.listRelatives(control, type="constraint"):
    #                 pm.delete(pm.listRelatives(control, type="constraint"))
    #
    #     pm.parent(rig_group, self.RIG_ROOT_NODE)
    #     # copy IK curve controls but don't parent to bone shape yet
    #     if pm.ls("%s_%s_%s_IK_control_placer" % (self.rig_name, side, limb)):
    #         IK_control_placer = pm.ls("%s_%s_%s_IK_control_placer" % (self.rig_name, side, limb))
    #         IK_control = pm.duplicate(IK_control_placer, name=("%s_%s_%s_IK_control" % (self.rig_name, side, limb)))
    #         pm.parent(IK_control[0], rig_offset)
    #
    #         pole_vector_placer = pm.ls("%s_%s_%s_pole_vector_placer" % (self.rig_name, side, limb))
    #         pole_vector = pm.duplicate(pole_vector_placer, name="%s_%s_%s_pole_vector" % (self.rig_name, side, limb))
    #         pm.parent(pole_vector[0], rig_offset)
    #
    #     if pm.ls("%s_%s_%s_foot_control_placer" % (self.rig_name, side, limb)):
    #         foot_control = pm.duplicate(pm.ls("%s_%s_%s_foot_control_placer" % (self.rig_name, side, limb)),
    #                       name="%s_%s_%s_foot_control" % (self.rig_name, side, limb))
    #         pm.parent(foot_control[0], rig_offset)
    #
    #     return mirrored_bones
    #
    # def mirror_controls(self, source_placer):
    #     if source_placer[0].split("%s_" % self.rig_name)[1][0] == "L":
    #         side = "%s_L_" % self.rig_name
    #         opposite = "%s_R_" % self.rig_name
    #     else:
    #         side = "%s_R_" % self.rig_name
    #         opposite = "%s_L_" % self.rig_name
    #
    #     if (pm.getAttr('%s.scale' % source_placer[0])[0] != (1,1,1)) or (pm.getAttr('%s.scale' % source_placer[0])[0] != (1,1,1)):
    #         self.clear_placer_scale(source_placer[0])
    #
    #     new_placer = pm.duplicate(source_placer, rr=False, renameChildren=True)
    #     pm.setAttr("%s.sx" % new_placer[0], -1)
    #     # pm.setAttr("%s.tx" % new_placer[0], (pm.xform(source_placer[1], ws=1, q=1, t=1)[0] * -1))
    #     pm.setAttr("%s.ry" % new_placer[0], (pm.xform(source_placer[1], ws=1, q=1, ro=1)[1] * -1))
    #     pm.setAttr("%s.rz" % new_placer[0], (pm.xform(source_placer[1], ws=1, q=1, ro=1)[2] * -1))
    #
    #     for node in new_placer:
    #         newName = node.replace(side, opposite)
    #         newName = newName[:-1]
    #         pm.rename(node, newName)
    #
    #     mirrored_placers = []
    #
    #     for node in source_placer:
    #         if node.replace(side, opposite):
    #             mirrored_placers.append(node.replace(side, opposite))
    #
    #     return mirrored_placers
    #
    # def make_limb_planar(self, limb, origin_bone, side="L"):
    #     # This will ensure the arm chain is planar by adjusting the wrist bone
    #     if not origin_bone:
    #         origin_bone = pm.ls(sl=True)[0]
    #     center_bone = pm.listRelatives(origin_bone, children=True)[0]
    #     end_bone = pm.listRelatives(center_bone, children=True)[0]
    #
    #     if limb == "arm":
    #         clavicle_bone = pm.listRelatives(origin_bone, parent=True)[0]
    #         wrist_bone_pointer =  pm.listRelatives(end_bone, children=True)[0]
    #         # palm_pointer = pm.listRelatives(palm_bone, children=True)[0]
    #         # palm_bone_translation =  pm.xform(palm_bone, q=True, ws=True, t=True)
    #         wrist_bone_pointer_translation =  pm.xform(wrist_bone_pointer, q=True, ws=True, t=True)
    #         # palm_pointer_translation = pm.xform(palm_pointer, q=True, ws=True, t=True)
    #
    #     if limb == "leg":
    #         ball_bone =  pm.listRelatives(end_bone, children=True)[0]
    #         toe_bone = pm.listRelatives(ball_bone, children=True)[0]
    #         print "ball bone: %s" % ball_bone
    #         print "toe_bone: %s" % toe_bone
    #         toe_pointer = pm.listRelatives(toe_bone, children=True)[0]
    #         ball_bone_translation =  pm.xform(ball_bone, q=True, ws=True, t=True)
    #         toe_bone_translation = pm.xform(toe_bone, q=True, ws=True, t=True)
    #         toe_pointer_translation = pm.xform(toe_pointer, q=True, ws=True, t=True)
    #
    #     # orient arm chain
    #     pm.joint(origin_bone, e=True, oj="xzy", sao="zup", ch=True, zso=True)
    #
    #     # get xforms of shoulder rotation and end bone translation
    #     origin_rotation =  pm.xform(origin_bone, q=True, ws=True, ro=True)
    #     endbone_translation = pm.xform(end_bone, q=True, ws=True, t=True)
    #
    #     # zero out joint orientations on bones
    #     pm.setAttr("%s.jointOrient" % origin_bone, 0, 0, 0)
    #     pm.setAttr("%s.jointOrient" % center_bone, 0, 0, 0)
    #
    #     # rotate shoulder bone to original rotation
    #     # translate wrist and palm bones to original position
    #     pm.xform(origin_bone, r=False, ws=True, ro=(origin_rotation[0], origin_rotation[1], origin_rotation[2]))
    #     pm.xform(end_bone, r=False, ws=True, t=(endbone_translation[0], endbone_translation[1], endbone_translation[2]))
    #
    #     # zero out ty on wrist
    #     pm.setAttr("%s.translateY" % end_bone, 0)
    #
    #     # swap origin_bone rotate values to joint orientations
    #     self.set_joint_orient_to_rotate(origin_bone)
    #
    #     # reorient entire arm chain from clavicle if arm
    #     if limb == "arm":
    #         pm.xform(wrist_bone_pointer, r=False, ws=True, t=(wrist_bone_pointer_translation[0], wrist_bone_pointer_translation[1], wrist_bone_pointer_translation[2]))
    #         # pm.xform(palm_pointer, r=False, ws=True, t=(palm_pointer_translation[0], palm_pointer_translation[1], palm_pointer_translation[2]))
    #         if side == "L":
    #             pm.joint(clavicle_bone, e=True, oj="xzy", sao="zup", ch=True, zso=True)
    #         elif side == "R":
    #             pm.joint(clavicle_bone, e=True, oj="xzy", sao="zup", ch=True, zso=True)
    #     elif limb == "leg":
    #         pm.xform(ball_bone, r=False, ws=True, t=(ball_bone_translation[0], ball_bone_translation[1], ball_bone_translation[2]))
    #         pm.xform(toe_bone, r=False, ws=True, t=(toe_bone_translation[0], toe_bone_translation[1], toe_bone_translation[2]))
    #         pm.xform(toe_pointer, r=False, ws=True, t=(toe_pointer_translation[0], toe_pointer_translation[1], toe_pointer_translation[2]))
    #         pm.joint(origin_bone, e=True, oj="xzy", sao="zup", ch=True, zso=True)
    #
    # def build_stretchy_limb(self, limb_chain, ikcontrol, stretchAttr='translate', ikfkblended=False):
    #     _limb = "%s_%s" % (limb_chain[0].split("_")[1], limb_chain[0].split("_")[2])
    #     _start_bone = limb_chain[0]
    #     _mid_bone = limb_chain[1]
    #     _end_bone = limb_chain[2]
    #
    #     stretchy_util_group = pm.group(em=True, name = '%s_%s_STRETCHY' % (self.rig_name, _limb))
    #
    #     if stretchAttr == 'translate':
    #         up_limb_dist = pm.distanceDimension(sp=(pm.xform(_start_bone, q=True, ws=True, t=True)), ep=(pm.xform(_mid_bone, q=True, ws=True, t=True)))
    #         up_limb_dist = pm.rename(pm.listRelatives(up_limb_dist, parent=True), "%s_%s_uplimbDistanceDimension" % (self.rig_name, _limb))
    #         low_limb_dist = pm.distanceDimension(sp=(pm.xform(_mid_bone, q=True, ws=True, t=True)), ep=(pm.xform(_end_bone, q=True, ws=True, t=True)))
    #         low_limb_dist = pm.rename(pm.listRelatives(low_limb_dist, parent=True), "%s_%s_lowlimbDistanceDimension" % (self.rig_name, _limb))
    #         total_limb_dist = pm.distanceDimension(sp=(pm.xform(_start_bone, q=True, ws=True, t=True)), ep=(pm.xform(_end_bone, q=True, ws=True, t=True)))
    #         total_limb_dist = pm.rename(pm.listRelatives(total_limb_dist, parent=True), "%s_%s_distanceDimension" % (self.rig_name, _limb))
    #
    #         stretchMult = pm.createNode("multiplyDivide", name="%s_%s_stretchyIK_multDiv" % (self.rig_name, _limb))
    #         up_limb_stretchMult = pm.createNode("multiplyDivide", name="%s_%s_stretchyIK_uplimbMultDiv" % (self.rig_name, _limb))
    #         low_limb_stretchMult = pm.createNode("multiplyDivide", name="%s_%s_stretchyIK_lowlimbMultDiv" % (self.rig_name, _limb))
    #         up_limb_condition = pm.createNode("condition", name="%s_%s_stretchyIK_uplimbCondition" % (self.rig_name, _limb))
    #         low_limb_condition = pm.createNode("condition", name="%s_%s_stretchyIK_lowlimbCondition" % (self.rig_name, _limb))
    #
    #         _dist_startBone = pm.rename(pm.listConnections("%s.startPoint" % total_limb_dist, s=1), "%s_%s_stretchyDistLOC_startPoint" % (self.rig_name, _limb) )
    #         _dist_midbone = pm.rename(pm.listConnections("%s.endPoint" % up_limb_dist, s=1), "%s_%s_stretchyDistLOC_midPoint" % (self.rig_name, _limb) )
    #         _dist_ikhandle = pm.rename(pm.listConnections("%s.endPoint" % total_limb_dist, s=1), "%s_%s_stretchyDistLOC_endPoint" % (self.rig_name, _limb) )
    #
    #         pm.parent(_dist_startBone, _start_bone)
    #         _ik_end_cnst = pm.pointConstraint(ikcontrol, _dist_ikhandle, mo=True, weight=1)[0]
    #         _ik_end_cnst_attr = pm.listAttr(_ik_end_cnst)[-1]
    #
    #         up_limb_length = pm.getAttr("%s.tx" % _mid_bone.split('_control')[0])
    #         low_limb_length = pm.getAttr("%s.tx" % _end_bone.split('_control')[0])
    #         limb_length = up_limb_length + low_limb_length
    #
    #         pm.setAttr("%s.operation" % stretchMult, 2)
    #         pm.connectAttr("%s.distance" % total_limb_dist, "%s.input1X" % stretchMult, f=True)
    #         pm.setAttr("%s.input2X" % stretchMult, limb_length)
    #
    #         pm.setAttr("%s.operation" % up_limb_stretchMult, 1)
    #         pm.setAttr("%s.operation" % low_limb_stretchMult, 1)
    #         pm.connectAttr("%s.outputX" % stretchMult, "%s.input1X" % up_limb_stretchMult, f=True)
    #         pm.connectAttr("%s.outputX" % stretchMult, "%s.input1X" % low_limb_stretchMult, f=True)
    #         pm.setAttr("%s.input2X" % up_limb_stretchMult, up_limb_length)
    #         pm.setAttr("%s.input2X" % low_limb_stretchMult, low_limb_length)
    #
    #         pm.setAttr("%s.operation" % up_limb_condition, 2)
    #         pm.setAttr("%s.operation" % low_limb_condition, 2)
    #         pm.connectAttr("%s.outputX" % up_limb_stretchMult, "%s.colorIfTrueR" % up_limb_condition, f=True)
    #         pm.connectAttr("%s.outputX" % low_limb_stretchMult, "%s.colorIfTrueR" % low_limb_condition, f=True)
    #         pm.setAttr("%s.colorIfFalseR" % up_limb_condition, up_limb_length)
    #         pm.setAttr("%s.colorIfFalseR" % low_limb_condition, low_limb_length)
    #         pm.connectAttr("%s.distance" % total_limb_dist, "%s.firstTerm" % up_limb_condition, f=True)
    #         pm.setAttr("%s.secondTerm" % up_limb_condition, limb_length)
    #         pm.connectAttr("%s.distance" % total_limb_dist, "%s.firstTerm" % low_limb_condition, f=True)
    #         pm.setAttr("%s.secondTerm" % low_limb_condition, limb_length)
    #         pm.connectAttr("%s.outColorR" % up_limb_condition, "%s.translateX" % _mid_bone, f=True)
    #         pm.connectAttr("%s.outColorR" % low_limb_condition, "%s.translateX" % _end_bone, f=True)
    #
    #         # write stretchy attrib as bool list, and to work if not ikfkblended
    #         pm.addAttr(ikcontrol, ln="stretchy", at="bool", k=1, dv=0)
    #         pm.connectAttr(("%s.stretchy" % ikcontrol), ("%s.%s" % (_ik_end_cnst, _ik_end_cnst_attr)), f=True)
    #
    #         # if ikfkblended:
    #             # _reverse_node = pm.createNode("reverse", name  = "%s_%s_ikfk_reverseNode" % (self.rig_name, _limb))
    #             # pm.connectAttr( ("%s.stretchy" % ikcontrol), ("%s.inputX" % _reverse_node), f=True )
    #             # _mid_bone = pm.ls("%s_control" % _mid_bone)
    #             # _end_bone = pm.ls("%s_control" % _end_bone)
    #
    #             # pm.connectAttr( ("%s.outputX" % _reverse_node), ("%s.%s" %
    #                                             # (pm.listConnections( _mid_bone, t='pointConstraint', s=0, d=1 )[0],
    #                                              # pm.listAttr( pm.listConnections(_mid_bone, t='pointConstraint', s=0, d=1)[0] )[-1])), f=True )
    #             # pm.connectAttr( ("%s.outputX" % _reverse_node), ("%s.%s" %
    #                                             # (pm.listConnections( _end_bone, t='pointConstraint', s=0, d=1 )[0],
    #                                              # pm.listAttr( pm.listConnections(_end_bone, t='pointConstraint', s=0, d=1)[0] )[-1])), f=True )
    #
    #         pm.parent(up_limb_dist, low_limb_dist, total_limb_dist, _dist_midbone, _dist_ikhandle, _dist_startBone, stretchy_util_group)
    #         pm.hide(up_limb_dist, low_limb_dist, total_limb_dist, _dist_midbone, _dist_ikhandle, _dist_startBone, stretchy_util_group)
    #
    #     elif stretchAttr == 'scale':
    #         _condition = pm.createNode("condition", name="%s_%s_stretchyIK_condition" % (self.rig_name, _limb))
    #         _multiplyDivide = pm.createNode("multiplyDivide", name="%s_%s_stretchyIK_multDiv" % (self.rig_name, _limb))
    #         pm.setAttr("%s.operation" % _multiplyDivide, 2)
    #         _plusMinusAverage = pm.createNode("plusMinusAverage", name="%s_%s_stretchyIK_plusMinAvg1" % (self.rig_name, _limb))
    #
    #         _distance = pm.distanceDimension(sp=(pm.xform(_start_bone, q=True, ws=True, t=True)),
    #                                           ep=(pm.xform(_end_bone, q=True, ws=True, t=True)))
    #         _distance = pm.rename(pm.listRelatives(_distance, parent=True), "%s_%s_distanceDimension" % (self.rig_name, _limb))
    #         _dist_startBone = pm.rename(pm.listConnections("%s.startPoint" % _distance, s=1), "%s_%s_stretchyDistLOC_startPoint" % (self.rig_name, _limb) )
    #         _dist_ikhandle = pm.rename(pm.listConnections("%s.endPoint" % _distance, s=1), "%s_%s_stretchyDistLOC_endPoint" % (self.rig_name, _limb) )
    #         _limb_length = pm.getAttr("%s.tx" % _mid_bone.split('_control')[0]) + pm.getAttr("%s.tx" % _end_bone.split('_control')[0])
    #         pm.parent(_dist_startBone, _start_bone)
    #         _ik_end_cnst = pm.pointConstraint(ikcontrol, _dist_ikhandle, mo=True, weight=1)[0]
    #         _ik_end_cnst_attr = pm.listAttr(_ik_end_cnst)[-1]
    #
    #         pm.connectAttr("%s.distance" % _distance, "%s.firstTerm" % _condition, f=True)
    #         pm.setAttr("%s.secondTerm" % _condition, _limb_length)
    #         pm.setAttr("%s.operation" % _condition, 2)
    #
    #         pm.connectAttr("%s.distance" % _distance, "%s.input1X" % _multiplyDivide, f=True)
    #         pm.setAttr("%s.input2X" % _multiplyDivide, _limb_length)
    #         pm.setAttr("%s.operation" % _condition, 2)
    #         pm.connectAttr("%s.outputX" % _multiplyDivide, "%s.colorIfTrueR" % _condition, f=True)
    #         pm.setAttr("%s.operation" % _multiplyDivide, 2)
    #         pm.connectAttr("%s.outColorR" % _condition, "%s.scaleX" % _start_bone)
    #         pm.connectAttr("%s.outColorR" % _condition, "%s.scaleX" % _mid_bone)
    #         pm.parent(_distance, _dist_startBone, _dist_ikhandle, stretchy_util_group)
    #         pm.hide(_distance, _dist_startBone, _dist_ikhandle)
    #
    #         pm.addAttr(ikcontrol, ln="stretchy", at="bool", k=1, dv=0)
    #         pm.connectAttr(("%s.stretchy" % ikcontrol), ("%s.%s" % (_ik_end_cnst, _ik_end_cnst_attr)), f=True)
    #
    #         if ikfkblended:
    #             _reverse_node = pm.createNode("reverse", name  = "%s_%s_ikfk_reverseNode" % (self.rig_name, _limb))
    #             pm.connectAttr( ("%s.stretchy" % ikcontrol), ("%s.inputX" % _reverse_node), f=True )
    #             _mid_bone = pm.ls("%s_control" % _mid_bone)
    #             _end_bone = pm.ls("%s_control" % _end_bone)
    #
    #             pm.connectAttr( ("%s.outputX" % _reverse_node), ("%s.%s" %
    #                                             (pm.listConnections( _mid_bone, t='pointConstraint', s=0, d=1 )[0],
    #                                              pm.listAttr( pm.listConnections(_mid_bone, t='pointConstraint', s=0, d=1)[0] )[-1])), f=True )
    #             pm.connectAttr( ("%s.outputX" % _reverse_node), ("%s.%s" %
    #                                             (pm.listConnections( _end_bone, t='pointConstraint', s=0, d=1 )[0],
    #                                              pm.listAttr( pm.listConnections(_end_bone, t='pointConstraint', s=0, d=1)[0] )[-1])), f=True )
    #
    #     return stretchy_util_group
    #
    # def build_stretchy_chain(self, bone_chain, ikcontrol, curve=None):
    #     pass
    #
    # def build_reverse_foot(self, ankle, side="L"):
    #     # make group
    #     rfik_group = pm.group(empty=True, name="%s_%s_RFIK_group" % (self.rig_name, side))
    #     _parent = []
    #     # get ball, toe, toetip
    #     ball = pm.listRelatives(ankle, children=True)[0]
    #     toe = pm.listRelatives(ball, children=True)[0]
    #     toetip = pm.listRelatives(toe, children=True)[0]
    #
    #     # iksc handles from ankle->ball, ball->toe, toe->toetip,  prefix with RFIK_
    #     ball_ik = pm.ikHandle(sol="ikRPsolver", sj=ankle, ee=ball, name=("%s_%s_ball_RFIKhandle" % (self.rig_name, side)))
    #     ball_ik_group = pm.group(em=True, name="%s_%s_ball_ik_group" % (self.rig_name, side), world=True)
    #     pm.xform(ball_ik_group, ws=True, t=(pm.xform(ball, q=True, ws=True, t=True)))
    #     pm.makeIdentity(ball_ik_group, apply=True, t=1, r=1, s=1)
    #     pm.parent(ball_ik[0], ball_ik_group)
    #     _parent.append(ball_ik_group)
    #
    #     toe_ik = pm.ikHandle(sol="ikRPsolver", sj=ball, ee=toe, name=("%s_%s_toe_RFIKhandle" % (self.rig_name, side)))
    #     toe_ik_group = pm.group(em=True, name="%s_%s_toe_ik_group" % (self.rig_name, side), world=True)
    #     pm.xform(toe_ik_group, ws=True, t=(pm.xform(toe, q=True, ws=True, t=True)))
    #     pm.makeIdentity(toe_ik_group, apply=True, t=1, r=1, s=1)
    #     pm.parent(toe_ik[0], toe_ik_group)
    #     _parent.append(toe_ik_group)
    #
    #     toetip_ik = pm.ikHandle(sol="ikRPsolver", sj=toe, ee=toetip, name=("%s_%s_toetip_RFIKhandle" % (self.rig_name, side)))
    #     toetip_ik_group = pm.group(em=True, name="%s_%s_toetip_ik_group" % (self.rig_name, side), world=True)
    #     pm.xform(toetip_ik_group, ws=True, t=(pm.xform(toetip, q=True, ws=True, t=True)))
    #     pm.makeIdentity(toetip_ik_group, apply=True, t=1, r=1, s=1)
    #     pm.parent(toetip_ik[0], toetip_ik_group)
    #     _parent.append(toetip_ik_group)
    #
    #     # duplicate ankle, toe, ball bones
    #     pm.select(d=True)
    #     rfik_base = pm.joint(name=("%s_%s_RFIK_base" % (self.rig_name, side)))
    #     pm.xform(rfik_base, ws=True, t=(pm.xform(ankle, q=True, ws=True, t=True)[0], 0, pm.xform(ankle, q=True, ws=True, t=True)[2]))
    #
    #     rfik_toetip = pm.joint(name=("%s_%s_RFIK_toetip" % (self.rig_name, side)))
    #     pm.xform(rfik_toetip, ws=True, t=(pm.xform(toetip, q=True, ws=True, t=True)))
    #
    #     rfik_toe = pm.joint(name=("%s_%s_RFIK_toe" % (self.rig_name, side)))
    #     pm.xform(rfik_toe, ws=True, t=(pm.xform(toe, q=True, ws=True, t=True)))
    #
    #     rfik_ball = pm.joint(name=("%s_%s_RFIK_ball" % (self.rig_name, side)))
    #     pm.xform(rfik_ball, ws=True, t=(pm.xform(ball, q=True, ws=True, t=True)))
    #
    #     rfik_ankle = pm.joint(name=("%s_%s_RFIK_ankle" % (self.rig_name, side)))
    #     pm.xform(rfik_ankle, ws=True, t=(pm.xform(ankle, q=True, ws=True, t=True)))
    #
    #     pm.xform(rfik_group, ws=True, t=(pm.xform(rfik_base, q=True, ws=True, t=True)))
    #     pm.makeIdentity(rfik_group, apply=True, t=1, r=1, s=1)
    #     _parent.append(rfik_base)
    #     pm.parent(_parent, rfik_group)
    #     RFIK_control = pm.ls("%s_%s_RFIK_control_placer" % (self.rig_name, side))
    #     pm.xform(RFIK_control, ws=True, t=(pm.xform(rfik_ball, q=True, ws=True, t=True)[0], 0, pm.xform(rfik_ball, q=True, ws=True, t=True)[2]))
    #     RFIK_control = pm.rename(RFIK_control, RFIK_control[0].replace('_placer', ''))
    #     pm.makeIdentity(RFIK_control, apply=True, t=1, r=1, s=1)
    #     pm.parent(rfik_group, RFIK_control)
    #
    #     pm.select(d=True)
    #
    #     return RFIK_control, rfik_group
    #
    # def build_fk_controls(self, bone_chain, side="L", point=1, orient=1): #offset
    #     rig_offset = bone_chain[0]
    #     parent_control = None
    #     bone_chain = bone_chain[1:]
    #     controls = []
    #
    #     for bone in bone_chain:
    #         try:
    #             control = pm.ls("%s_control" % bone)[0]
    #             bone_offset = pm.createNode("transform", name="%s_offset" % bone, parent=rig_offset)
    #             _newpos = (pm.xform(bone, q=True, r=False, ws=True, t=True))
    #             pm.xform(bone_offset, r=False, ws=True, t=(_newpos))
    #
    #             # _tmp_cnst = pm.parentConstraint(bone, bone_offset, mo=0)
    #             # pm.delete(_tmp_cnst)
    #             pm.parent(control, bone_offset)
    #
    #             if side != "middle":    # originally written to only apply on R_ controls
    #                 pm.makeIdentity(control, apply=True, t=1, r=1, s=1, n=0)
    #
    #             _tmp_cnst = pm.orientConstraint(bone, bone_offset, mo=False)
    #             pm.delete(_tmp_cnst)
    #
    #             pm.xform(control, r=False, ws=True, t=(_newpos))
    #
    #             if point == 1:
    #                 pm.pointConstraint(control, bone, mo=True, weight=1, name="%s_pointConstraint" % control)
    #             if orient == 1:
    #                 pm.orientConstraint(control, bone, mo=True, weight=1, name="%s_orientConstraint" % control)
    #
    #             if parent_control:
    #                 pm.parent(bone_offset, parent_control)
    #                 parent_control = control
    #             else:
    #                 parent_control = control
    #
    #             pm.select(d=True)
    #             control_placer = ("%s_placer" % control)
    #             control_placer_shape =  pm.listRelatives(control_placer, type="shape")[0]
    #             control_shape = pm.listRelatives(control, type="shape")[0]
    #
    #             _num_of_cvs = (pm.getAttr("%s.spans" % control_shape) + pm.getAttr("%s.degree" % control_shape))
    #
    #             for cv in range (0, _num_of_cvs):
    #                 origpos = pm.xform("%s.cv[%s]" % (control_placer_shape, cv), q=True, ws=True, t=True)
    #                 pm.xform("%s.cv[%s]" % (control_shape, cv), ws=True, t=origpos)
    #
    #             self.lock_attrs(control, ['sx', 'sy', 'sz'])
    #             self.lock_attrs(control, ['v'], lock=0)
    #             controls.append(control)
    #
    #         except:
    #             pass
    #
    #     return controls
    #
    # def build_ik_fk_limb(self, side, limb, origin_bone):
    #     if not origin_bone:
    #         origin_bone = pm.ls(sl=True)[0]
    #     center_bone = pm.listRelatives(origin_bone, children=True)[0]
    #     end_bone = pm.listRelatives(center_bone, children=True)[0]
    #
    #     limb_IK_control = pm.ls("%s_%s_%s_IK_control" % (self.rig_name, side, limb))[0]
    #     limb_pole_control = pm.ls("%s_%s_%s_pole_vector" % (self.rig_name, side, limb))[0]
    #
    #     if pm.ls("%s_%s_%s_foot_control" % (self.rig_name, side, limb)):
    #         foot_control = pm.ls("%s_%s_%s_foot_control" % (self.rig_name, side, limb))[0]
    #
    #     # Create the IK handle.
    #     limb_IK = pm.ikHandle(sol="ikRPsolver", sj=origin_bone, ee=end_bone, name=("%s_%s_%s_IKhandle" % (self.rig_name, side, limb)))
    #
    #     pm.setAttr("%s.visibility" % limb_IK[0], 0)
    #
    #     # Set the limbIk control in world space (default values won't be 0, but we don't care).
    #     pm.move(0,0,0, limb_IK_control, rpr=True)
    #     pm.makeIdentity(limb_IK_control, a=1, r=1, t=1, s=1)
    #     end_bone_pos = pm.xform(end_bone, q=True, a=True, ws=True, rp=True)
    #     pm.move(end_bone_pos[0], end_bone_pos[1], end_bone_pos[2], limb_IK_control, ws=True, a=True)
    #     pm.makeIdentity(limb_IK_control, a=1, r=1, t=1, s=1)
    #     pm.pointConstraint(limb_IK_control, limb_IK[0], w=1, mo=False)
    #
    #     # Create the default position locator for the limb pole vector
    #     # (we'll use it to position the pole-vector when switching from FK to IK).
    #     limb_pole_default_LOC = pm.spaceLocator(name="%s_%s_%s_pole_default_LOC" % (self.rig_name, side, limb))[0]
    #     center_bone_pos = pm.xform(center_bone, q=True, a=True, ws=True, rp=True)
    #     pm.xform(limb_pole_default_LOC, ws=True, t=center_bone_pos)
    #     # pm.move(center_bone_pos[0], center_bone_pos[1], center_bone_pos[2], limb_pole_default_LOC, a=True)
    #
    #     # Parent the locator to the origin_bone joint and put the locator behind the center_bone.
    #     pm.parent(limb_pole_default_LOC, origin_bone)
    #
    #     if center_bone_pos[2] < end_bone_pos[2]:
    #         _pole_offset = -50
    #     elif center_bone_pos[2] > end_bone_pos[2]:
    #         _pole_offset = 50
    #
    #     pm.move(0, 0, _pole_offset, limb_pole_default_LOC, r=True, ws=True, wd=True)
    #     pm.setAttr("%s.visibility" % limb_pole_default_LOC, 0)
    #
    #     # Match the position between the pole vector and the locator.
    #     pm.pointConstraint(limb_pole_default_LOC, limb_pole_control, w=1, o=(0,0,0),name="_tmp_cnst")
    #     pm.delete("_tmp_cnst")
    #     pm.makeIdentity(limb_pole_control, apply=True, t=1, r=1, s=1, n=0)
    #
    #     # Pole-constraint the IK handle to the pole-vector control.
    #     pm.poleVectorConstraint(limb_pole_control, limb_IK[0], w=1)
    #
    #     # Connect the IK handle visibility to the end_bone IK enable attribute.
    #     pm.addAttr(limb_IK_control, ln="enableIk", at="bool", k=1, dv=0, h=1)
    #     pm.connectAttr("%s.enableIk" % limb_IK_control, "%s.ikBlend" % limb_IK[0], f=1)
    #     pm.connectAttr("%s.enableIk" % limb_IK_control, "%s.visibility" % limb_IK_control, f=1)
    #     pm.connectAttr("%s.enableIk" % limb_IK_control, "%s.visibility" % limb_pole_control, f=1)
    #
    #     # Put the limb in IK by default.
    #     pm.setAttr("%s.enableIk" % limb_IK_control, 0)
    #
    #     self.lock_attrs(limb_IK_control, ['sx', 'sy', 'sz'])
    #     pm.setAttr("%s.v" % limb_IK_control, keyable=0, channelBox=0)
    #
    #     self.lock_attrs(limb_pole_control, ['sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
    #     pm.setAttr("%s.v" % limb_pole_control, keyable=0, channelBox=0)
    #
    #     if pm.ls("%s_offset" % (end_bone)):
    #         pm.orientConstraint(limb_IK_control, "%s_offset" % (end_bone), mo=True)
    #
    #     return_controls = [ limb_IK, limb_IK_control, limb_pole_control ]
    #     if pm.ls("%s_%s_%s_foot_control" % (self.rig_name, side, limb)):
    #         pm.xform('%s.scalePivot' % foot_control, ws=True, t=(pm.xform(end_bone, q=True, t=True, ws=True)))
    #         pm.xform('%s.rotatePivot' % foot_control, ws=True, t=(pm.xform(end_bone, q=True, t=True, ws=True)))
    #         pm.makeIdentity(foot_control, apply=True, t=1, r=1, s=1, n=0)
    #         return_controls.append(foot_control)
    #
    #     return return_controls
    #
    #
    # # Final Rig build methods
    # def build_rig_ikfk_arm(self, arm_placer, stretchy):
    #     # build arms
    #     print("############## Now Building Arms... ##############")
    #     pm.select(d=True)
    #     _limb = arm_placer[0].split("_")[2]
    #
    #     L_arm_placer = arm_placer
    #     R_arm_placer = self.mirror_placer(L_arm_placer)   # mirror L arm placers to R arm placers
    #     L_arm_build_bones = self.build_bones("L", _limb, L_arm_placer[1:])        # build bones
    #     self.make_limb_planar("arm", L_arm_build_bones[4])
    #
    #     R_arm_build_bones = self.mirror_bones(L_arm_build_bones[3], R_arm_placer[1:])
    #     # self.make_limb_planar("arm", R_arm_build_bones[4])
    #
    #     print("############## Creating FK controls... ##############")
    #     _fkarm_list = L_arm_build_bones[3:-1]
    #     _fkarm_list.insert(0, L_arm_build_bones[1])
    #     L_fk_arm_controls = self.build_fk_controls(_fkarm_list, side="L", point=0)     # build fk controls
    #     self.lock_attrs(L_fk_arm_controls[2], ['rx', 'rz'])                                # lock rx, rz, on elbow
    #     self.lock_attrs(L_fk_arm_controls[1], ['sx'], 0)
    #     self.lock_attrs(L_fk_arm_controls[2], ['sx'], 0)
    #
    #     _fkarm_list = R_arm_build_bones[3:-1]
    #     _fkarm_list.insert(0, R_arm_build_bones[1])
    #     R_fk_arm_controls = self.build_fk_controls(_fkarm_list, side="R", point=0)     # build fk controls
    #     self.lock_attrs(R_fk_arm_controls[2], ['rx', 'rz'])                                # lock rx, rz, on elbow
    #     self.lock_attrs(R_fk_arm_controls[1], ['sx'], 0)
    #     self.lock_attrs(R_fk_arm_controls[2], ['sx'], 0)
    #
    #     for control in L_fk_arm_controls:
    #         self.lock_attrs(control, ['ty', 'tz'])
    #     for control in R_fk_arm_controls:
    #         self.lock_attrs(control, ['ty', 'tz'])
    #
    #     pm.delete(L_arm_build_bones[-1])            # delete pointer bones after they're oriented
    #     pm.delete(R_arm_build_bones[-1])
    #
    #     print("############## Creating IK controls... ##############")
    #     L_ik_arm_controls = self.build_ik_fk_limb("L", _limb, L_arm_build_bones[4])        # build IK controls
    #     pm.parent(L_ik_arm_controls[0][0], L_fk_arm_controls[0])    # parent L_arm_IK handle to L_ARM_RIG_OFFSET
    #     pm.parent(L_ik_arm_controls[2], L_ik_arm_controls[1])       # parent IK_hand_control to arm_pole_vector
    #     pm.parent(L_ik_arm_controls[1], L_arm_build_bones[0])
    #     self.ikfk_switch("L", _limb)
    #
    #     R_ik_arm_controls = self.build_ik_fk_limb("R", _limb, R_arm_build_bones[4])        # build IK controls
    #     pm.parent(R_ik_arm_controls[0][0], R_fk_arm_controls[0])    # parent R_arm_IK handle to R_ARM_RIG_OFFSET
    #     pm.parent(R_ik_arm_controls[2], R_ik_arm_controls[1])       # parent IK_hand_control to arm_pole_vector
    #     pm.parent(R_ik_arm_controls[1], R_arm_build_bones[0])
    #     self.ikfk_switch("R", _limb)
    #
    #     if stretchy:
    #        print("############## Making stretchy IK... ##############")
    #
    #        L_stretchy_limb_grp = self.build_stretchy_limb(L_arm_build_bones[4:7], L_ik_arm_controls[1], ikfkblended=True)
    #        R_stretchy_limb_grp = self.build_stretchy_limb(R_arm_build_bones[4:7], R_ik_arm_controls[1], ikfkblended=True)
    #
    #        pm.parent(L_stretchy_limb_grp, L_fk_arm_controls[1])
    #        pm.parent(R_stretchy_limb_grp, R_fk_arm_controls[1])
    #
    #     print("############## Making final connections... ##############")
    #     arm_connector = pm.getAttr("%s.connector" % L_arm_placer[0])
    #
    #     pm.delete(L_arm_placer[0])                # delete arm placers
    #     pm.delete(R_arm_placer[0])
    #
    #     L_arm_connection = L_arm_build_bones[1]
    #     R_arm_connection = R_arm_build_bones[1]
    #
    #     return L_arm_connection, R_arm_connection, arm_connector
    #
    # def build_rig_phalange(self, phalange_placer):
    #     print("############## Now Building Phalange... ##############")
    #     pm.select(d=True)
    #     L_phalange_placer = phalange_placer
    #     R_phalange_placer = self.mirror_placer(L_phalange_placer)   # mirror L phalange placers to R phalange placers
    #     _limb = "%s" % phalange_placer[0].split("_")[2]
    #     L_phalange_build_bones = self.build_bones("L", _limb, L_phalange_placer[1:])        # build bones
    #     R_phalange_build_bones = self.build_bones("R", _limb, R_phalange_placer[1:])        # build bones
    #
    #     print("############## Creating FK controls... ##############")
    #     # orient joints
    #     pm.joint(L_phalange_build_bones[3], e=True, oj="xzy", sao="zup", ch=True, zso=True)
    #     _fkphalange_list = L_phalange_build_bones[3:]
    #     _fkphalange_list.insert(0, L_phalange_build_bones[1])
    #     L_fk_phalange_controls = self.build_fk_controls(_fkphalange_list, side="L", point=0)     # build fk controls
    #     # self.lock_attrs(L_fk_phalange_controls[2], ['sx'], 0)
    #
    #     pm.joint(R_phalange_build_bones[3], e=True, oj="xzy", sao="zup", ch=True, zso=True)
    #     _fkphalange_list = R_phalange_build_bones[3:]
    #     _fkphalange_list.insert(0, R_phalange_build_bones[1])
    #     R_fk_phalange_controls = self.build_fk_controls(_fkphalange_list, side="R", point=0)     # build fk controls
    #     # self.lock_attrs(R_fk_phalange_controls[2], ['sx'], 0)
    #
    #     print("############## Making final connections... ##############")
    #     L_phalange_connector = pm.getAttr("%s.connector" % L_phalange_placer[0])
    #     R_phalange_connector = L_phalange_connector.replace('L_', 'R_')
    #
    #     for control in L_fk_phalange_controls:
    #         self.lock_attrs(control, ['ty', 'tz'])
    #     for control in R_fk_phalange_controls:
    #         self.lock_attrs(control, ['ty', 'tz'])
    #
    #     pm.delete(L_phalange_build_bones[-1])            # delete pointer bones after they're oriented
    #     pm.delete(R_phalange_build_bones[-1])
    #
    #     L_phalange_connection = L_phalange_build_bones[1]
    #     R_phalange_connection = R_phalange_build_bones[1]
    #
    #     pm.delete(L_phalange_placer)
    #     pm.delete(R_phalange_placer)
    #
    #     return L_phalange_connection, R_phalange_connection, L_phalange_connector, R_phalange_connector
    #
    # def build_rig_rfik_leg(self, leg_placer, stretchy):
    #     # build legs
    #     print("############## Building Legs... ##############")
    #     pm.select(d=True)
    #     _limb = leg_placer[0].split("_")[2]
    #
    #     L_leg_placer = leg_placer
    #     R_leg_placer = self.mirror_placer(L_leg_placer)   # mirror L leg placers to R leg placers
    #     L_leg_build_bones = self.build_bones("L", _limb, L_leg_placer[1:])        # build bones
    #     # R_leg_build_bones = self.build_bones("R", _limb, R_leg_placer[1:])        # build bones
    #     self.make_limb_planar("leg", L_leg_build_bones[3])
    #     R_leg_build_bones = self.mirror_bones(L_leg_build_bones[3], R_leg_placer[1:])
    #     pm.select(d=True)
    #
    #     # print("############## Creating FK controls... ##############") #
    #
    #     # _fkleg_list = L_leg_build_bones[3:8]
    #     # _fkleg_list.insert(0, L_leg_build_bones[1])
    #     # L_fk_leg_controls = self.build_fk_controls(_fkleg_list, side="L")     # build fk controls
    #     # pm.setAttr("%s.rx" % L_fk_leg_controls[1], lock=1, keyable=0, channelBox=0)      # lock rx, rz, on elbow
    #     # pm.setAttr("%s.rz" % L_fk_leg_controls[1], lock=1, keyable=0, channelBox=0)
    #
    #     # _fkleg_list = R_leg_build_bones[3:8]
    #     # _fkleg_list.insert(0, R_leg_build_bones[1])
    #     # R_fk_leg_controls = self.build_fk_controls(_fkleg_list, side="R")     # build fk controls
    #     # pm.setAttr("%s.rx" % R_fk_leg_controls[1], lock=1, keyable=0, channelBox=0)      # lock rx, rz, on elbow
    #     # pm.setAttr("%s.rz" % R_fk_leg_controls[1], lock=1, keyable=0, channelBox=0)
    #
    #     # pm.delete(L_fk_leg_controls[3:], R_fk_leg_controls[3:])
    #
    #     print("############## Creating leg IK controls ##############")
    #     L_ik_leg_controls = self.build_ik_fk_limb("L", _limb, L_leg_build_bones[3])        # build IK controls
    #     pm.parent(L_ik_leg_controls[0][0], L_leg_build_bones[1])    # parent L_leg_IK handle to L_leg_RIG_OFFSET
    #     pm.parent(L_ik_leg_controls[2], L_ik_leg_controls[1])       # parent IK_control to leg_pole_vector
    #     pm.parent(L_ik_leg_controls[1], L_ik_leg_controls[3])
    #     pm.parent(L_ik_leg_controls[3], L_leg_build_bones[0])
    #     self.ikfk_switch("L", _limb)
    #     # pm.setAttr("%s.v" % L_ik_leg_controls[2], 1)        # 1/7/15: started getting error here, not sure why it didn't err before
    #     R_ik_leg_controls = self.build_ik_fk_limb("R", _limb, R_leg_build_bones[3])        # build IK controls
    #     pm.parent(R_ik_leg_controls[0][0], R_leg_build_bones[1])    # parent R_leg_IK handle to R_leg_RIG_OFFSET
    #     pm.parent(R_ik_leg_controls[2], R_ik_leg_controls[1])       # parent IK_control to leg_pole_vector
    #     pm.parent(R_ik_leg_controls[1], R_ik_leg_controls[3])
    #     pm.parent(R_ik_leg_controls[3], R_leg_build_bones[0])
    #     self.ikfk_switch("R", _limb)
    #     # pm.setAttr("%s.v" % R_ik_leg_controls[2], 1)        # 1/7/15: started getting error here, not sure why it didn't err before
    #
    #     if stretchy:
    #         print("############## Building stretchy leg...##############")
    #         L_stretchy_limb_grp = self.build_stretchy_limb(L_leg_build_bones[3:6], L_ik_leg_controls[1])
    #         R_stretchy_limb_grp = self.build_stretchy_limb(R_leg_build_bones[3:6], R_ik_leg_controls[1])
    #
    #         pm.parent(L_stretchy_limb_grp, L_leg_build_bones[1])
    #         pm.parent(R_stretchy_limb_grp, R_leg_build_bones[1])
    #
    #     print("############## Creating RFIK and controls ##############")
    #     L_RFIK = self.build_reverse_foot(L_leg_build_bones[5], side="L_%s" % _limb)
    #     R_RFIK = self.build_reverse_foot(R_leg_build_bones[5], side="R_%s" % _limb)
    #     pm.setAttr("%s.visibility" % L_RFIK[1], 0)
    #     pm.setAttr("%s.visibility" % R_RFIK[1], 0)
    #     pm.parent(L_RFIK[1], L_leg_build_bones[0])
    #     pm.parent(R_RFIK[1], R_leg_build_bones[0])
    #     print ("%s: " % R_RFIK[0]) + str(pm.getAttr("%s.ry" % R_RFIK[0]))
    #     print ("%s: " % R_ik_leg_controls[3]) + str(pm.getAttr("%s.ry" % R_ik_leg_controls[3]))
    #     pm.parent(R_RFIK[0], R_ik_leg_controls[3])
    #     pm.makeIdentity(R_RFIK[0], a=1, t=1, r=1, s=1)
    #     pm.parent(L_RFIK[0], L_ik_leg_controls[3])
    #     print ("%s: " % R_RFIK[0]) + str(pm.getAttr("%s.ry" % R_RFIK[0]))
    #     print ("%s: " % R_ik_leg_controls[3]) + str(pm.getAttr("%s.ry" % R_ik_leg_controls[3]))
    #     pm.parent(L_RFIK[1],L_RFIK[0])
    #     pm.parent(R_RFIK[1],R_RFIK[0])
    #     leg_connector = pm.getAttr("%s.connector" % L_leg_placer[0])
    #
    #     pm.delete(L_leg_placer[0])            # delete leg placer
    #     pm.delete(R_leg_placer[0])
    #
    #     R_leg_connection = R_leg_build_bones[1]        # set hook-in connections
    #     L_leg_connection = L_leg_build_bones[1]
    #
    #     return L_leg_connection, R_leg_connection, leg_connector
    #
    # def build_rig_spline_spine(self, spine_placer, stretchy):
    #     print("############## Building Spine... ##############")
    #     ##### "BUILD BONES"
    #     spine_bones = self.build_bones("middle", "SPINE", spine_placer[0][1:])        # build bones
    #     pm.joint(spine_bones[4], e=True, oj="yzx", sao="yup", ch=True, zso=True)
    #
    #     ##### "PARENT BONES    "
    #     pm.parent(spine_bones[4], world=True)
    #     pm.parent(spine_bones[3], spine_bones[4])
    #     pm.parent(spine_bones[4], spine_bones[2])
    #
    #     ##### "CREATE FK CONTROLS"
    #     spineBody_fk_controls = self.build_fk_controls([spine_bones[1], spine_bones[4], spine_bones[3], spine_bones[-2], spine_bones[-1] ], side="middle")
    #     _rig_control_group = pm.group( (pm.listRelatives(spineBody_fk_controls[0], parent=True) ), name = "%s_SPINE_CONTROL" % self.rig_name)
    #
    #     for control in spineBody_fk_controls[1:]:
    #         self.lock_attrs(control, ['tx', 'ty', 'tz'])
    #
    #     ##### "MAKE SPLINE SPINE"
    #     spline_spine_ikhandle = pm.ikHandle(name="%s_splineSpine_ikHandle" % self.rig_name, sol = "ikSplineSolver",
    #                                         ns = int(self.spine_placer[2])-1, sj=spine_bones[5], ee=spine_bones[-3], scv=0)
    #     _curve = spline_spine_ikhandle[2]
    #     pm.parent(_curve, _rig_control_group)
    #     pm.setAttr("%s.inheritsTransform" % _curve, 0)
    #     _curve = pm.rename(_curve, "%s_splineSpine_curve" % self.rig_name)
    #
    #     # parent root and neck bone CV clusters to root and neck bone
    #     _curve_cvs = pm.ls("%s_splineSpine_curve.cv[*]" % self.rig_name, fl=True)
    #
    #     ##### "CLUSTER CVS"
    #     i=1
    #     _spineSplineClusters = []
    #     for cv in _curve_cvs:
    #         pm.select(cv, add=False)
    #         _new_clust = pm.cluster(name="%s_splineSpine_cluster_%s" % (self.rig_name, i))
    #         _spineSplineClusters.append(_new_clust)
    #         pm.parent(_new_clust[1], _rig_control_group)
    #         pm.hide(_new_clust)
    #         i += 1
    #
    #     ##### "MAKE SPLINE SPINE CONTROLS"
    #     pm.parent(spline_spine_ikhandle[0], _rig_control_group)
    #
    #     for i in range (1, int(spine_placer[2])+1):
    #         print ("%s and %s " % (self.rig_name, i) )
    #         _control = pm.ls("%s_spine%s_control" % (self.rig_name, i))[0]
    #         pm.makeIdentity(_control, apply=True, t=1, r=1, s=1, n=0)
    #         pm.select(_control, add=False)
    #         _new_grp = pm.group(_control, name = "%s_offset" % _control)
    #         pm.makeIdentity(_new_grp, apply=True, t=1, r=1, s=1, n=0)
    #         pm.parentConstraint(_control, _spineSplineClusters[i], mo=True, w=1)
    #         pm.parent(_new_grp, spine_bones[1])
    #         self.lock_attrs(_control, ['sx', 'sy', 'sz', 'v'])
    #
    #         if i == 1:
    #             pm.parent(pm.listRelatives(_control, parent=True), spineBody_fk_controls[0])
    #         else:
    #             pm.parent(pm.listRelatives(_control, parent=True), pm.ls("%s_spine%s_control" % (self.rig_name, i-1))[0])
    #             if i == int(spine_placer[2]):
    #                 pm.parent(pm.listRelatives(spineBody_fk_controls[2], parent=True), _control)
    #                 _spine_locator = pm.spaceLocator(name="%s_topSpine_locator" % self.rig_name,
    #                     p=( pm.getAttr("%s.t" % _control)[0]) )[0]
    #                 pm.setAttr("%s.visibility" % _spine_locator, 0)
    #                 pm.makeIdentity(_spine_locator, apply=True, t=1, r=1, s=1, n=0)
    #                 pm.parentConstraint(_spine_locator, spline_spine_ikhandle[0], mo=True)
    #                 pm.parentConstraint(spline_spine_ikhandle[0], _spineSplineClusters[-1], mo=True)
    #                 pm.parent(_spine_locator, _control)
    #
    #     _bones = spine_bones[5:-2]
    #
    #     if stretchy:
    #         _condition = pm.createNode("condition", name="%s_splineSpine_condition" % self.rig_name)
    #         _multiplyDivide = pm.createNode("multiplyDivide", name="%s_splineSpine_multDiv" % self.rig_name)
    #         _curvelen = pm.arclen(_curve, ch=1)
    #
    #         pm.connectAttr("%s.arcLength" % _curvelen, "%s.firstTerm" % _condition, f=True)
    #         pm.connectAttr("%s.arcLength" % _curvelen, "%s.input1X" % _multiplyDivide, f=True)
    #         pm.setAttr("%s.secondTerm" % _condition, pm.arclen(_curve))
    #         pm.setAttr("%s.input2X" % _multiplyDivide, pm.arclen(_curve))
    #         pm.setAttr("%s.operation" % _condition, 2)
    #         pm.connectAttr("%s.outputX" % _multiplyDivide, "%s.colorIfTrueR" % _condition, f=True)
    #         pm.setAttr("%s.colorIfFalseR" % _condition, 1)
    #         pm.setAttr("%s.operation" % _multiplyDivide, 2)
    #         pm.hide(_curve)
    #         i=1
    #
    #         for bone in _bones:
    #             # pm.connectAttr("%s.outColorR" % _condition, "%s.scaleY" % bone)
    #             #  stretch_factor = pm.getAttr("%s.outputX" % _multiplyDivide)
    #             _stretchMultiplyDivide = pm.createNode("multiplyDivide", name="%s_splineSpineStretch_multDiv%s" % (self.rig_name, i))
    #             pm.setAttr("%s.operation" % _stretchMultiplyDivide, 1)
    #             pm.setAttr("%s.input1X" % _stretchMultiplyDivide, pm.getAttr("%s.ty" % bone))
    #             pm.connectAttr("%s.outColorR" % _condition, "%s.input2X" % _stretchMultiplyDivide)
    #             pm.connectAttr("%s.outputX" % _stretchMultiplyDivide, "%s.ty" % bone, f=True)
    #             i += 1
    #
    #
    #     ##### "SPINE CONNECTIONS AND CLEANUP"
    #     pm.pointConstraint(spineBody_fk_controls[0], _spineSplineClusters[0], mo=True)
    #     pm.delete(pm.listRelatives(spine_bones[-2])[-2], pm.listRelatives(spine_bones[-1])[-2])
    #
    #     pm.pointConstraint(spine_bones[-2], pm.listRelatives(spineBody_fk_controls[-2], parent=True)[0], mo=True)
    #
    #     world_control = pm.rename( pm.ls("%s_world_control_placer" % self.rig_name)[0], "%s_world_control" % self.rig_name)
    #     pm.parent(world_control, w=1)
    #     pm.makeIdentity(world_control, a=1, r=1, t=1, s=1)
    #
    #     return world_control
    #
    #
    # # Rig Control methods
    #
    # # Final build method
    # def build_rig(self):
    #     print("#########################################################################################")
    #     print("###### NOW BUILDING RIG %s ###########################" % self.rig_name)
    #     print("#########################################################################################")
    #
    #     pm.select(d=True)
    #     # check for placers and reset group nodes in case they were moved
    #     for placer in self.placers:
    #         print placer
    #         self.reset_group_node(placer)
    #
    #     self.refresh_active_placers()
    #
    #     print("############ BUILDING SPLINEIK SPINE #######################")
    #     if not pm.ls("%s_SPINE_RIG_PLACER*" % self.rig_name):
    #         print "CANNOT BUILD RIG: NO SPINE PLACER DETECTED!"
    #         pm.promptDialog(message='CANNOT BUILD RIG: NO SPINE PLACER DETECTED!',
    #                         button=['OK', 'Cancel'],
    #                         defaultButton='OK',
    #                         cancelButton='Cancel',
    #                         dismissString='Cancel')
    #     world_control = self.build_rig_spline_spine(self.spine_placer, pm.getAttr("%s.stretchy" % self.spine_placer[0][0]) )
    #     pm.delete(self.spine_placer[0][0])
    #
    #     print("############ BUILDING %s IKFK ARMS #######" % self.arm_placers)
    #     j=0
    #     for placer in self.placers:
    #         if self.placers[placer] == "arm":
    #             j+=1
    #             # rebuild placer object
    #             _arm_placer = []
    #             for i in range(0, pm.getAttr("%s.placers" % placer, size=True)):
    #                 _arm_placer.append(pm.ls(pm.getAttr("%s.placers[%s]" % (placer, i)))[0])
    #             _arm_connections = self.build_rig_ikfk_arm(_arm_placer, pm.getAttr("%s.stretchy" % _arm_placer[0]))
    #             pm.parentConstraint(_arm_connections[2], _arm_connections[1], mo=True)
    #             pm.parentConstraint(_arm_connections[2], _arm_connections[0], mo=True)
    #             # pm.parent(_arm_connections[0], _arm_connections[2])
    #             # pm.parent(_arm_connections[1], _arm_connections[2])
    #
    #     pm.addAttr(self.RIG_ROOT_NODE, at="byte", ln="ikfkarms", dv=j)
    #
    #     print("############ BUILDING %s FINGERS #######" % self.arm_placers)
    #     j=0
    #     for placer in self.placers:
    #         if self.placers[placer] == "finger":
    #             j+=1
    #             # rebuild placer object
    #             _finger_placer = []
    #             for i in range(0, pm.getAttr("%s.placers" % placer, size=True)):
    #                 _finger_placer.append(pm.ls(pm.getAttr("%s.placers[%s]" % (placer, i)))[0])
    #             _finger_connections = self.build_rig_phalange(_finger_placer)
    #             pm.parentConstraint(_finger_connections[2], _finger_connections[0], mo=True)
    #             pm.parentConstraint(_finger_connections[3], _finger_connections[1], mo=True)
    #             # pm.parent(_finger_connections[0], _finger_connections[2])
    #             # pm.parent(_finger_connections[1], _finger_connections[3])
    #
    #     print("############ BUILDING %s RFIK LEGS #######" % self.leg_placers)
    #     for placer in self.placers:
    #         if self.placers[placer] == "leg":
    #             # rebuild placer object
    #             _leg_placer = []
    #             for i in range(0, pm.getAttr("%s.placers" % placer, size=True)):
    #                 _leg_placer.append(pm.ls(pm.getAttr("%s.placers[%s]" % (placer, i)))[0])
    #             _leg_connections = self.build_rig_rfik_leg(_leg_placer, pm.getAttr("%s.stretchy" % _leg_placer[0]))
    #             pm.parentConstraint(_leg_connections[2], _leg_connections[0], mo=True)
    #             pm.parentConstraint(_leg_connections[2], _leg_connections[1], mo=True)
    #             # pm.parent(_leg_connections[0], _leg_connections[2])
    #             # pm.parent(_leg_connections[1], _leg_connections[2])
    #
    #     print("############ BUILDING %s TOES #######" % self.leg_placers)
    #     j=0
    #     for placer in self.placers:
    #         if self.placers[placer] == "toe":
    #             j+=1
    #             # rebuild placer object
    #             _toe_placer = []
    #             for i in range(0, pm.getAttr("%s.placers" % placer, size=True)):
    #                 _toe_placer.append(pm.ls(pm.getAttr("%s.placers[%s]" % (placer, i)))[0])
    #             _toe_connections = self.build_rig_phalange(_toe_placer)
    #             pm.parentConstraint(_toe_connections[2], _toe_connections[0], mo=True)
    #             pm.parentConstraint(_toe_connections[3], _toe_connections[1], mo=True)
    #             # pm.parent(_toe_connections[0], _toe_connections[2])
    #             # pm.parent(_toe_connections[1], _toe_connections[3])
    #
    #
    #     # constrain world control last:
    #     pm.setAttr("%s.inheritsTransform" % world_control, 0)
    #     pm.parent(world_control, self.RIG_ROOT_NODE)
    #     pm.parentConstraint(world_control, self.RIG_ROOT_NODE, mo=True)
    #
    #     ### POST BUILD CLEANUP ###
    #     self.UImode = "control"
    #     pm.setAttr("%s.uimode" % self.RIG_ROOT_NODE, "control", type="string")
    #     if pm.window(self.rig_name, q=1, exists=1):
    #         pm.deleteUI(self.rig_name)
    #     self.rig_UI(self.UImode)
    #     pm.select(d=True)



a = Autorig()
a.build_arm_placer(side="L", stretchy=0, num=1)