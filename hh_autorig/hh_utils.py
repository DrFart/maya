import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.OpenMayaUI as omu
import maya.api.OpenMaya as api

import math

RAD2DEG = (180/math.pi)
DEG2RAD = (math.pi/180)

# Get the component object from the given string of a node name
def getMObjectFromName(node_name):
    depNode = om.MObject()
    selectionList = om.MSelectionList()
    selectionList.add(node_name)
    selectionList.getDependNode(0, depNode)
    return depNode


# Get the MDagPath from the given string of a node name
def getMDagPathFromName(node_name):
    dagPath = om.MDagPath()
    selectionList = om.MSelectionList()
    selectionList.add(node_name)
    selectionList.getDagPath(0, dagPath)
    return dagPath


# Get the MDagPath from index 0 of the currently selected transform or components
def getMDagPathFromSelected():
    dagPath = om.MDagPath()
    selectList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selectList)
    if selectList.isEmpty():
        pm.error("Nothing Selected.")
    else:
        selectList.getDagPath(0, dagPath)
        return dagPath


# Get the components from index 0 of the currently selected transform or components
def getMObjectFromSelected():
    depNode = om.MObject()
    selectList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selectList)
    if selectList.isEmpty():
        pm.error("Nothing Selected")
    else:
        selectList.getDependNode(0, depNode)
        return depNode


# Unlock and delete given string or object
def unlockAndDelete(node):
    node = pm.PyNode(node)
    pm.lockNode(node.name(), lock=False)
    pm.delete(node)


# Unlock and delete selected objects
def unlockAndDeleteSelected():
    allSelected = pm.ls(selection=True)
    for item in allSelected:
        unlockAndDelete(item)


def close_all_windows():
    exceptions = ['MayaWindow', 'havokDummyWindow', 'nexFloatWindow']
    for window in cmds.lsUI(type='window'):
       if window not in exceptions:
           cmds.deleteUI(window)

   
def delete_all_layers():
    for layer in cmds.ls(type='displayLayer'):
        if layer != 'defaultLayer':
            cmds.delete(layer)
        
        
def rename_file_nodes():
    for node in cmds.ls(type="file"):
        nuname = cmds.getAttr(node + '.fileTextureName').split('/')[-1].replace('.png','')
        cmds.rename(node, nuname)
    
    
def set_frame_range():
    allcurves = cmds.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])
    endframe = 1
    for curve in allcurves:
        keys = pm.keyframe(curve, q=1)
        if max(keys) > endframe:
            endframe = max(keys) 
    cmds.playbackOptions(max=endframe, fps=30, aet=endframe, ast=1, min=1 )
    
    return int(endframe)
    

def remove_references():
    refs = []
    for sel in cmds.ls(sl=1):
        if cmds.referenceQuery( sel, f=1 ) not in refs:
            refs.append( cmds.referenceQuery(sel, f=1) )

    for refFile in refs:
        try:
            cmds.file(refFile, rr=1)
        except:
            refParentFile = cmds.referenceQuery( cmds.file(refFile, q=1, rfn=1), p=1, f=1 )
            cmds.file(refParentFile, rr=1)
        
        
def lock_all_skin_weights():
    bones = cmds.ls(type = 'joint')

    for bone in bones:
        if cmds.objExists('%s.liw' % bone):
            cmds.setAttr('%s.liw' % bone, 1)
        
        
def unlock_all_skin_weights():
    bones = cmds.ls(type = 'joint')

    for bone in bones:
        if cmds.objExists('%s.liw' % bone):
            cmds.setAttr('%s.liw' % bone, 0)
        
        
def bind_multi_meshes():
    jnts = []
    meshes = []
    for sel in pm.ls(sl=1):
        if sel.type() == 'joint':
            jnts.append(sel)
        if sel.type() == 'transform':
            meshes.append(sel)

    for mesh in meshes:
        pm.skinCluster( jnts, mesh, n='newSkinCluster', tsb=1, bm=1, sm=0, nw=1, wd=1, mi=4, omi=1, dr=4.0, fnw=1, rui=0 )


def copy_paste_vert_norms( source=None, dest=None ):
    try:
        if (source, dest == None):
            source = cmds.ls(os=1)[0]
            dest = cmds.ls(os=1)[1]
        source_norm = cmds.polyNormalPerVertex(source, q=1, xyz=1)
        dest_norm = cmds.polyNormalPerVertex(dest, q=1, xyz=1)
        cmds.polyNormalPerVertex(dest, xyz=source_norm[:3], e=1)
    except:
        print("Source and Destination vert not selected!")


def round_off_xforms(decimals):
    sel = pm.selected() 

    for jnt in sel:
        jnt.rx.set( round( jnt.rx.get(), decimals))
        jnt.ry.set( round( jnt.ry.get(), decimals))
        jnt.rz.set( round( jnt.rz.get(), decimals))

        jnt.tx.set( round( jnt.tx.get(), decimals))
        jnt.ty.set( round( jnt.ty.get(), decimals))
        jnt.tz.set( round( jnt.tz.get(), decimals))


def label_joint(bonelist=None):
    try:
        bonelist = pm.ls(sl=1)
        for jnt in bonelist:
            if jnt.split('_')[-1] == "l":
                side = 1
            elif jnt.split('_')[-1] == "r":
                side = 2
            else:
                side = 0

            if side != 0:
                boneName = jnt.split('_')[:-1]
                boneName = '_'.join(str(elem) for elem in boneName)
            else:
                boneName = jnt.name()

            # set joint label side and name to other and fill in boneName
            jnt.setAttr("side", side)
            jnt.setAttr("type", 18)
            jnt.setAttr("otherType", boneName, type="string")
    except:
        print("Did not label!")


def mirror_left_side_skel():
# assumes all left side joints have 'L_' prefix
    for jnt in jnts:
        if jnt[:2] == "L_":
            pm.select( jnt)
            pm.mirrorJoint( mirrorYZ=1, mirrorBehavior=1, searchReplace=("L_","R_") )


def fileinfo_to_clipboard( req_info="scene" ):  # copy file info: scene, drive, dir, file
    try:
        scene_name = pm.sceneName()
        from PySide2 import QtWidgets
        clipboard = QtWidgets.QApplication.clipboard()    
        
        if req_info == "scene":
            copied = scene_name
        elif req_info == "drive":
            copied = scene_name.drive
        elif req_info == "dir":
            copied = scene_name.dirname().truepath()     # .truepath() uses backslashes "\" in paths
        elif req_info == "file":
            copied = scene_name.basename()

        clipboard.setText(copied)
        return copied
    except:
        print("failed! make sure a scene file is open in Maya.")


def toggle_cm_m():
    if cmds.currentUnit(q=1) == 'm':
        # go to cm
        cmds.currentUnit(l='cm', time='ntsc')
        cmds.grid(s=100, sp=100)
        cmds.setAttr("perspShape.nearClipPlane", 0.5)
        cmds.setAttr("perspShape.farClipPlane", 150000)
    elif cmds.currentUnit(q=1) == 'cm':
        # go to m
        cmds.currentUnit(l='m', time='ntsc')
        cmds.setAttr("perspShape.nearClipPlane", 0.005)
        cmds.setAttr("perspShape.farClipPlane", 1500)
        cmds.grid(s=1, sp=1)
    cmds.setAttr("perspShape.focalLength", 100)
    objs = [ 'miDefaultFramebuffer', 'miDefaultOptions', 'vectorRenderGlobals' ]
    for object in objs:
        if cmds.objExists( object ):
            cmds.delete( object )
    pm.playbackOptions( min=1, ast=1, max=60, aet=60 )


def delete_all_namespaces():
    ns_ignore = [ 'UI', 'shared' ]
    for ns in pm.namespaceInfo( lon=1 ):
        if ns not in ns_ignore:
            pm.namespace( rm=ns, mnr=1 )


def cleanup_skeleton_hierarchy():
    remove = []
    for i in pm.ls(sl=1):
        if (i.type() != 'joint'):
            remove.append(i)
            
    for node in remove:
        if node.objExists():
            try:
                pm.delete(node)
            except:
                pass 


def shift_keyframes( time_change=1 ):
    result = pm.promptDialog( t="Shift frames", m="Shift frames by how much:", text = "Number", b="OK", ds="cancelled" )
    if result == 'OK':
        time_change = pm.promptDialog( q=1, text = 1 )
    anim_curves = cmds.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])  
    for each in anim_curves:  
        cmds.keyframe(each, edit=True, relative=True, timeChange=time_change)


def break_out_anims( clipname, sourcefile, framerange ):
    clipname = os.path.join( output_folder, clipname )
    sourcefile = os.path.join( working_folder, sourcefile )
    
    pm.newFile( f=1 )
    pm.importFile( sourcefile, f=1 )
    
    clip_startframe = framerange[0]
    clip_endframe = framerange[1]

    startframe = 1
    endframe = 100

    anim_curves = pm.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])  

    for curve in anim_curves:
        keys = pm.keyframe(curve, q=1)
        if max(keys) > endframe:
            endframe = int( max(keys) )

    for i in range ( clip_endframe, endframe+1 ):    
        for c in anim_curves:
            c.remove( clip_endframe-1 )
            i += 1
            
    for i in range (0, clip_startframe):    
        for c in anim_curves:
            c.remove( 0 )
            i += 1
    shift_keyframes( -(clip_startframe+1) )
    pm.saveAs( clipname, f=1 )


def createLocatorAtComponentAABB(sel, locname="loc"):
    try:
        sel = cmds.ls(sl=True)
    except:
        "No components (verts/edges/faces) selected!"
    bb = cmds.exactWorldBoundingBox(sel)
    pos = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
    loc = pm.createNode('locator', n=locname)
    loc.setPosition(pos)
    pm.select(sel)


# Create new locators at selected objects' pivot location.
def createLocatorAtObject():
    newLocatorList = list()
    node_list = pm.ls(sl=True, long=True)
    pm.select(clear=True)
    for node in node_list:
        locShape = pm.createNode('locator', n='{0}Shape'.format(node.name()))
        locTransform = locShape.listRelatives(parent=True, fullPath=True)[0]
        locTransform.rename(node.name())
        nodeMatrix = node.getMatrix(worldSpace=True)
        locTransform.setMatrix(nodeMatrix, worldSpace=True)

        # locTransform.scaleZ.set(1)
        # locTransform.scaleX.set(1)
        # locTransform.scaleY.set(1)

        newLocatorList.append(locTransform)

    pm.select(newLocatorList)

def moveJointOrientToRotate(joint_name):
    joint_depth = getMDagPathFromName(joint_name)
    if not joint_depth.hasFn(om.MFn.kJoint):
        raise(RuntimeError, "Cannot edit joint orients on non-joint!!")

    rotation = om.MEulerRotation()
    orient = om.MEulerRotation()
    node_MFnTfm = oma.MFnIkJoint(joint_depth)
    node_MFnTfm.getOrientation(orient)
    node_MFnTfm.getRotation(rotation)
    out = om.MEulerRotation.decompose((rotation.asMatrix() * orient.asMatrix()), rotation.order)

    cmds.setAttr('%s.jointOrientX' % joint_name, 0.0)
    cmds.setAttr('%s.jointOrientY' % joint_name, 0.0)
    cmds.setAttr('%s.jointOrientZ' % joint_name, 0.0)
    cmds.setAttr('%s.rotateX' % joint_name, out.x * RAD2DEG)
    cmds.setAttr('%s.rotateY' % joint_name, out.y * RAD2DEG)
    cmds.setAttr('%s.rotateZ' % joint_name, out.z * RAD2DEG)

def moveRotateToJointOrient(joint_name):
    joint_depth = getMDagPathFromName(joint_name)
    if not joint_depth.hasFn(om.MFn.kJoint):
        raise(RuntimeError, "Cannot edit joint orients on non-joint!!")

    rotation = om.MEulerRotation()
    orient = om.MEulerRotation()
    node_MFnTfm = oma.MFnIkJoint(joint_depth)
    node_MFnTfm.getOrientation(orient)
    node_MFnTfm.getRotation(rotation)
    out = om.MEulerRotation.decompose((rotation.asMatrix() * orient.asMatrix()), orient.order)

    cmds.setAttr('%s.jointOrientX' % joint_name, out.x * RAD2DEG)
    cmds.setAttr('%s.jointOrientY' % joint_name, out.y * RAD2DEG)
    cmds.setAttr('%s.jointOrientZ' % joint_name, out.z * RAD2DEG)
    cmds.setAttr('%s.rotateX' % joint_name, 0.0)
    cmds.setAttr('%s.rotateY' % joint_name, 0.0)
    cmds.setAttr('%s.rotateZ' % joint_name, 0.0)

def moveSelectedJointOrientToRotate():
    for joint_name in cmds.ls(sl=True, type='joint', long=True):
        moveJointOrientToRotate(joint_name)

def moveSelectedRotateToJointOrient():
    for joint_name in cmds.ls(sl=True, type='joint', long=True):
        moveRotateToJointOrient(joint_name)

def createJointAtObject():
    newJointList = list()
    node_list = pm.ls(selection=True, long=True)
    pm.select(clear=True)
    for node in node_list:
        newJoint = pm.createNode('joint', n='{0}'.format(node.name()))
        newGroup = pm.group()
        nodeMatrix = cmds.xform(node.name(), worldSpace=True, matrix=True, query=True)

        # Grouping shenanigans to work around an issue with Maya 2018 xform not working well with joints
        newGroup.setMatrix(nodeMatrix, worldSpace=True)
        newGroup.scaleX.set(1)
        newGroup.scaleY.set(1)
        newGroup.scaleZ.set(1)
        newJoint.setParent(world=True)
        pm.delete(newGroup)

        newJointList.append(newJoint)

    pm.select(newJointList)

# Create joint at selected components pivot location
def createJointAtComponentAABB(sel, jntname="newJoint"):
    try:
        sel = cmds.ls(sl=True)
    except:
        "No components (verts/edges/faces) selected!"
    bb = cmds.exactWorldBoundingBox(sel)
    pos = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
    jnt = pm.createNode('joint', n=jntname)
    jnt.setTranslation(pos, ws=1)
    pm.select(sel)


def createCurveAtObject():
    newLocatorList = list()
    node_list = pm.ls(sl=True, long=0)
    pm.select(clear=True)
    for node in node_list:
        # locShape = pm.createNode('nurbsCurve', n='C{0}Shape'.format(node.name()))
        # locTransform = locShape.listRelatives(parent=True, fullPath=True)[0]
        locTransform = pm.circle(name='C_{0}'.format(node.name()))[0]
        # locTransform.rename('C_{0}'.format(node.name()))
        nodeMatrix = node.getMatrix(worldSpace=True)
        locTransform.setMatrix(nodeMatrix, worldSpace=True)

        # locTransform.scaleZ.set(1)
        # locTransform.scaleX.set(1)
        # locTransform.scaleY.set(1)

        newLocatorList.append(locTransform)

    pm.select(newLocatorList)


def getSkinningInfo():
    sel = pm.ls(sl=1)[0]
    selSkin = sel.getShape().listConnections(t='skinCluster')
    bonez = pm.skinCluster(selSkin, q=1, inf=1)
    return selSkin, bonez

def resave_bind_pose():
    try:
        rootjoint = pm.ls(sl=1)[0]
        pm.delete(pm.ls(type='dagPose'))
        pm.select(rootjoint)
        cmds.select(hi=1)
        jnts = cmds.ls(sl=1, type='joint')
        cmds.select(jnts)
        pm.dagPose(bp=1, s=1)
        print("Bind pose resaved!")
        pm.select(d=1)
    except:
        print("ERROR: Bind pose not resaved!")

def openFileDialogInSceneDir():
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    fileOpen = pm.fileDialog2(fileFilter=multipleFilters, dialogStyle=2, okc="Open", fileMode=1, caption="Open",
                              dir=pm.sceneName().dirname().truepath())

    if fileOpen:
        try:
            pm.newFile()
            pm.openFile(fileOpen, f=0)
        except:
            s = pm.confirmDialog(title='Save changes', message='Save changes to {0} ?'.format(pm.sceneName().truepath()),
                                 button=['Save', "Don't Save", 'Cancel'], defaultButton='Save', cancelButton='Cancel',
                                 dismissString='No')
            if s == 'Save':
                pm.saveFile(f=1)
                pm.openFile(fileOpen, f=0)
            elif s == "Don't Save":
                pm.openFile(fileOpen, f=1)
    else:
        pass


def saveAsDialogInSceneDir():
    multipleFilters = "Maya ASCII (*.ma);;Maya Binary (*.mb)"
    fileSave = pm.fileDialog2(fileFilter=multipleFilters, dialogStyle=2, okc="Save As", fileMode=0, caption="Save As",
                              dir=pm.sceneName().dirname().truepath())
    if fileSave:
        try:
            pm.saveAs(fileSave[0], f=1)
            print("Saved as {0}".format(fileSave[0]))
        except:
            print("Nothing saved")


def filedialog_dec(f):
    def use_maya_dialog():
        print("Check if using Maya file dialog; switch to it if so and set var")
        f()
        print("set back to OS file dialog if var is set")
    return use_maya_dialog

@filedialog_dec
def import_fbx(fbxfile):
    print("Import fbx file")


def vectors_are_coplanar(shoulder, elbow, wrist):
    should_mat = shoulder.getMatrix(ws=1)
    should_x_axis = api.MVector(should_mat[0][0:3])
    # y_axis = should_mat[4:7]
    # z_axis = should_mat[8:11]
    elbow_mat = elbow.getMatrix(ws=1)
    elbow_x_axis = api.MVector(elbow_mat[0][0:3])

    wrist_mat = wrist.getMatrix(ws=1)
    wrist_x_axis = api.MVector(wrist_mat[0][0:3])

    should_elbow_cross_product = should_x_axis ^ elbow_x_axis
    dot_prod_of_wrist_and_shouldElbowCross = wrist_x_axis * should_elbow_cross_product

    print('shoulder: {0}\nelbow: {1}\nwrist: {2}\n'.format(should_x_axis, elbow_x_axis, wrist_x_axis ))
    print(should_elbow_cross_product)
    print(dot_prod_of_wrist_and_shouldElbowCross)

    if dot_prod_of_wrist_and_shouldElbowCross == 0:
        return ("Vectors are coplanar")
    else:
        return ("Vectors are not coplanar")

def create_offset_group(sel):
    # put selected node under a group and move transforms
    # to the group
    pm.createNode(n='group')


def snap_t(sel1, sel2):
    sel1.setTranslation(sel2.getTranslation(ws=True), ws=True )

def snap_r(sel1, sel2):
    sel1.setRotation(sel2.getRotation( ws=True ), ws=True )