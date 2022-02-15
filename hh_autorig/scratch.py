# write distance formula function

# get vectors between two objects

# get vectors of verts and find closest

def build_arm_placer(self, side, stretchy, num=1):
    _arm_pieces = []
    side = "%s_%s_ARM%s" % (self.rig_name, side, num)
    arm_placer_group = cmds.group(name="%s_RIG_PLACER" % side, empty=True)

    # create clavicle, shoulder, elbow, wrist, palm, pointer proxy bones
    clavicle_bone_placer = widgets.create_circle_control("%s_clavicle_bone_placer" % side, scale=[3, 3, 3])
    cmds.xform(clavicle_bone_placer, r=False, ws=True, t=(20, 100, -1))
    cmds.xform(arm_placer_group, ws=1, t=(cmds.xform(clavicle_bone_placer, ws=1, q=1, t=1)))
    _arm_pieces.append(clavicle_bone_placer)

    shoulder_bone_placer = widgets.create_circle_control("%s_shoulder_bone_placer" % side, scale=[3, 3, 3])
    cmds.xform(shoulder_bone_placer, r=False, ws=True, t=(30, 100, -2))
    _arm_pieces.append(shoulder_bone_placer)

    elbow_bone_placer = widgets.create_circle_control("%s_elbow_bone_placer" % side, scale=[3, 3, 3])
    cmds.xform(elbow_bone_placer, r=False, ws=True, t=(40, 80, -10))
    _arm_pieces.append(elbow_bone_placer)

    wrist_bone_placer = widgets.create_circle_control("%s_wrist_bone_placer" % side, scale=[3, 3, 3])
    cmds.xform(wrist_bone_placer, r=False, ws=True, t=(50, 60, -2))
    _arm_pieces.append(wrist_bone_placer)

    wrist_bone_pointer_placer = widgets.create_circle_control("%s_wristpointer_bone_placer" % side, scale=[3, 3, 3])
    cmds.xform(wrist_bone_pointer_placer, r=False, ws=True, t=(51, 55, -1))
    _arm_pieces.append(wrist_bone_pointer_placer)

    # palm_bone_placer = widgets.create_circle_control("%s_palm_bone_placer" % side, scale=[3,3,3])
    # cmds.xform(palm_bone_placer, r=False, ws=True, t=(51, 55, -1))
    # _arm_pieces.append(palm_bone_placer)

    # palm_bone_pointer_placer = widgets.create_circle_control("%s_palmpointer_bone_placer" % side, scale=[3,3,3])
    # cmds.xform(palm_bone_pointer_placer, r=False, ws=True, t=(54, 52, 0.25))
    # _arm_pieces.append(palm_bone_pointer_placer)

    _arm_proxy_curve = cmds.curve(d=1,
                                  p=[(1, 0, 1),
                                     (3, 0, 1),
                                     (5, 0, 1),
                                     (7, 0, 1),
                                     (9, 0, 1)],
                                  # (11, 0, 1)],
                                  k=[0, 1, 2, 3, 4],
                                  name="_%s_arm_proxy_curve" % side)

    # make cluster at each CV
    _number_of_cvs = cmds.getAttr("%s.degree" % _arm_proxy_curve) + cmds.getAttr("%s.spans" % _arm_proxy_curve)
    for i in range(0, _number_of_cvs):
        cmds.select("%s.cv[%s]" % (_arm_proxy_curve, i))
        _cluster = cmds.cluster(name="_%s_placer_cluster_%s" % (side, i))
        cmds.pointConstraint(_arm_pieces[i], _cluster)
        cmds.hide(_cluster)

    cmds.setAttr("%s.overrideEnabled" % _arm_proxy_curve, 1)
    cmds.setAttr("%s.overrideDisplayType" % _arm_proxy_curve, 2)
    cmds.setAttr("%s.inheritsTransform" % _arm_proxy_curve, 0)

    # create cube control at clav, shoulder, elbow, wrist
    clavicle_control_placer = widgets.create_cube_control("%s_clavicle_control_placer" % side, scale=[3, 3, 3])
    shoulder_control_placer = widgets.create_cube_control("%s_shoulder_control_placer" % side, scale=[3, 3, 3])
    elbow_control_placer = widgets.create_cube_control("%s_elbow_control_placer" % side, scale=[3, 3, 3])
    wrist_control_placer = widgets.create_cube_control("%s_wrist_control_placer" % side, scale=[3, 3, 3])
    # palm_control_placer = widgets.create_cube_control("%s_palm_control_placer" % side, scale=[3,3,3])

    # create cube control for hand IK, cone control for pole vector  IK_hand_control_placer
    IK_hand_control_placer = widgets.create_cube_control(("%s_IK_control_placer" % side), [5, 2, 5])
    # arm_pole_vector = widgets.create_cone_control("%s_arm_pole_vector" % self.side)
    arm_pole_vector_placer = widgets.create_cube_control("%s_pole_vector_placer" % side, scale=[3, 3, 3])
    cmds.xform(IK_hand_control_placer, ws=True, t=(80, 50, 0))
    cmds.xform(arm_pole_vector_placer, ws=True, t=(80, 50, 0))

    # parent constrain to respective bone
    cmds.parentConstraint(clavicle_bone_placer, clavicle_control_placer, name="_tmp_cnst")
    cmds.delete("_tmp_cnst")
    cmds.parentConstraint(clavicle_bone_placer, clavicle_control_placer)

    cmds.parentConstraint(shoulder_bone_placer, shoulder_control_placer, name="_tmp_cnst")
    cmds.delete("_tmp_cnst")
    cmds.parentConstraint(shoulder_bone_placer, shoulder_control_placer)

    cmds.parentConstraint(elbow_bone_placer, elbow_control_placer, name="_tmp_cnst")
    cmds.delete("_tmp_cnst")
    cmds.parentConstraint(elbow_bone_placer, elbow_control_placer)

    cmds.parentConstraint(wrist_bone_placer, wrist_control_placer, name="_tmp_cnst")
    cmds.delete("_tmp_cnst")
    cmds.parentConstraint(wrist_bone_placer, wrist_control_placer)

    # cmds.parentConstraint(palm_bone_placer, palm_control_placer, name="_tmp_cnst")
    # cmds.delete("_tmp_cnst")
    # cmds.parentConstraint(palm_bone_placer, palm_control_placer)

    cmds.parent(cmds.ls("_%s_placer_cluster*Handle" % side), clavicle_bone_placer, shoulder_bone_placer,
                elbow_bone_placer,
                wrist_bone_placer, wrist_bone_pointer_placer, clavicle_control_placer, shoulder_control_placer,
                elbow_control_placer, wrist_control_placer, _arm_proxy_curve, IK_hand_control_placer,
                arm_pole_vector_placer, arm_placer_group)
    cmds.select(d=True)
    cmds.setAttr("%s.t" % _arm_proxy_curve, 0, 0, 0)
    cmds.setAttr("%s.r" % _arm_proxy_curve, 0, 0, 0)
    _arm_pieces.insert(0, arm_placer_group)

    # store placer metadata in placer root node
    cmds.addAttr(arm_placer_group, ln="placers", dt="string", m=True)
    i = 0
    for _piece in _arm_pieces:
        cmds.setAttr("%s.placers[%s]" % (arm_placer_group, i), _piece, type="string")
        i += 1

    cmds.addAttr(arm_placer_group, ln="placertype", dt="string")  # type of placer (arm, leg, etc.)
    cmds.setAttr("%s.placertype" % arm_placer_group, "arm", type="string")

    cmds.addAttr(arm_placer_group, ln="connector", dt="string")  # where placer connects (spine, etc.)
    cmds.setAttr("%s.connector" % arm_placer_group, "%s_spine3" % self.rig_name, type="string")
    # cmds.setAttr("%s.connector" % arm_placer_group, "%s_spine3" % self.rig_name, type="string")

    cmds.addAttr(arm_placer_group, ln="stretchy", at="bool")  # stretchiness flag
    cmds.setAttr("%s.stretchy" % arm_placer_group, stretchy)

    self.placers[arm_placer_group] = cmds.getAttr("%s.placertype" % arm_placer_group)  # add placer to dict

    return _arm_pieces


build_arm_placer()