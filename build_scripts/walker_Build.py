import platform
import sys
from importlib import reload

from rjg.build_scripts.bettercontrols import apply_control_file
import maya.cmds as mc
import maya.mel as mel

groups = 'G:' if platform.system() == 'Windows' else '/groups'
mc.scriptEditorInfo(suppressWarnings=True,suppressInfo=True)

import rjg.build.buildPart as rBuild
import rjg.build.prop as rProp
import rjg.libs.file as rFile
import rjg.libs.util as rUtil
import rjg.post.dataIO.controls as rCtrlIO
import rjg.post.finalize as rFinal
import rjg.post.usd as rUSD
from rjg.build.parts.bipedLimb import BipedLimb
from rjg.build.parts.clavicle import Clavicle
from rjg.build.parts.hand import Hand
from rjg.libs.skin import auto_split_all_weights
from rjg.libs.profile import add_profiler_tag
import rjg.post.PoseInterpExtras as expi
import rjg.post.character_defaults as char_default
import rjg.post.smoothribbon as smooth_rib


reload(rUtil)
reload(rProp)
reload(rBuild)
reload(rFinal)
reload(rFile)
reload(rUSD)

import pipe.m.space_switch as spsw
from ngSkinTools2.api import plugin



def auto_apply_defaults():
    import os
    import maya.cmds as mc

    ubm_nodes = mc.ls("*_UBM")

    if not ubm_nodes:
        print("No *_UBM found, skipping defaults")
        return

    character = ubm_nodes[0].replace("_UBM", "")
    DEFAULT_DIR = rf"{groups}\dragonkisser\pipeline\pipeline\software\maya\scripts\rjg\build_scripts\character_defaults"

    json_path = os.path.join(
        DEFAULT_DIR,
        f"{character}_defaults.json"
    )

    if not os.path.exists(json_path):
        print(f"No defaults file found for {character}")
        return

    print(f"Applying stored defaults for {character}")

    tool = char_default.ControlDefaultsTool()

    tool.character = character
    tool.json_path = json_path

    tool.read_all()

def ensure_ng_initialized():
    if not plugin.is_plugin_loaded():
        plugin.load_plugin()



### Build Begins ###

def run(character, mp=None, gp=None, ep=None, cp=None, sp=None, pp=None, face=True, previs=False):
    import rjg.build_scripts
    reload(rjg.build_scripts)
    
    import rjg.libs.util as rUtil
    import rjg.post.dataIO.controls as rCtrlIO
    import rjg.post.dataIO.ng_weights as rWeightNgIO
    import rjg.post.dataIO.weights as rWeightIO
    from rjg.build.parts.driverjoints import create_driver_joints
    from rjg.build_scripts import Bobo_Build_Scripts
    from rjg.build_scripts.SteveUtils import CurveNetAtHome
    from rjg.build_scripts.SteveUtils.importskins import import_weights
    from rjg.build_scripts.UnrealCorrectives import BuildCorrectives, build_parents
    from rjg.libs.metadata import create_versioning_script
    reload(rUtil)
    reload(rWeightNgIO)
    reload(rWeightIO)
    reload(rCtrlIO)
    
    ## Setting parameters for individual Characters (splitting off groups)
    not_previs = False if previs or character in ['DungeonMonster', 'Jett', 'Blitz', 'Susaka', 'NPC', 'Fisherman'] else True
    bony = False 

    body_mesh = f'{character}_UBM'

    ensure_ng_initialized()
    mc.file(new=True, f=True)

    #Production
    if character in ['Bobo', 'Gretchen']:
        production = 'HB'
    elif character in ['Domingo', 'Luciana', 'CrowdA', 'CrowdB', 'CrowdC']:
        production = 'DK'
    elif character in ['Robin', 'Rayden', 'DungeonMonster']:
        production = 'LG'
    elif character in ['Jett', 'Blitz']:
        production = 'SG'
    elif character in ['Mech', 'Walker']:
        production = 'WF'
    else:
        production = None

    addmusc = True


    ### BUILD SCRIPT
    root = rBuild.build_module(module_type='root', side='M', part='root', model_path=mp, guide_path=gp, base=production, muscle_ctrl=True)
    if ep:
        extras = rFile.import_hierarchy(ep, parent='MODEL')[0]
    #Fun Camera Thing
    mc.viewFit('perspShape', fitFactor=1, all=True, animate=True)

    # Versioning
    create_versioning_script(rig_name=character, rig_version=7.2)
    
    #Fixing Names

    neckList = ['Neck', 'Neck1', 'Neck2', 'Head']

    # Building Parts // setting up the diffrent changes per character

    split_weights = True
    hipshape = 'hips'

    hip = rBuild.build_module(
        module_type="hip",
        side="M",
        part="COG",
        guide_list=["Hips"],
        ctrl_scale=50,
        cog_shape=hipshape,
        waist_shape="circle",
        generate_waist=False,
    )
    spine = rBuild.HybridSpine(
        side="M",
        part="spine",
        base_guide="Hips",
        hip_pivot_guide="HipPivot",
        mid_guide="Spine",
        chest_pivot_guide="Spine",
        upper_chest_pivot_guide="Spine1",
        spine_end_guide="Spine2",
        ctrl_scale=1.5,
        joint_num=7,
        split_weights = split_weights
    )
        


    #Mirrored Base Rig Parts
    fing_shape = 'circle' 
    curlaxis = 'Z' 
    clavshape = 'Arch'
    Clavmo=True
    Clavaim=False
    FootMus=True
    footshp = "shoe"
    curlshape = "sims"
    chest_control=True
    scap_control=True



    for fs in ["Left", "Right"]:

        leg = rBuild.build_module(module_type='dragonleg', side=fs[0], part='dragonleg', guide_list=[fs + piece for piece in ['UpLeg', 'Leg', 'Knee', 'Foot', 'ToeBase', 'MiddleToe_Root', 'MiddleToe_Mid', 'MiddleToe_EE', 'IndexToe_Root', 'IndexToe_Mid', 'IndexToe_EE', 'RingToe_Root', 'RingToe_Mid', 'RingToe_EE', 'PinkyToe_Root', 'PinkyToe_Mid', 'PinkyToe_EE', 'ThumbToe_Root', 'ThumbToe_Mid', 'ThumbToe_EE']])

    ##Pistons 
    for side in ['L', 'R']:
        from rjg.build.parts.walkerpistons import Build_Correctives

        Build_Correctives(side)

        sidelong = 'Left' if side in ['L'] else 'Right'

        lever = rBuild.build_module(module_type='arbitrary2', side=side, part='Flap01', guide_list=f'{sidelong}Flap01', ctrl_scale=10, par_ctrl='chest_M_JNT' , par_jnt='chest_M_JNT' ,shape='circle', scale=True)

        #guns = rBuild.build_module(module_type='arbitrary2', side=side, part='gun', guide_list=f'{sidelong}_guns', ctrl_scale=20, par_ctrl=f'hand_{side}_JNT' , par_jnt=f'hand_{side}_JNT' ,shape='circle', scale=True)

        #Left_guns


    GUN = rBuild.build_module(module_type='arbitrary', side='M', part='GUN', guide_list=['GUN'], ctrl_scale=10, par_ctrl='chest_M_JNT' , par_jnt='chest_M_JNT' ,shape='circle', scale=True)

    import rjg.build.parts.spline_from_curve as spline_module

    reload(spline_module)

    splinepart = spline_module.spline()

    result = splinepart.build_spline_from_curve(
        curve_name="polyToCurve1",
        driver_count=4,
        driven_count=10,
        prefix="L_Tube_A",
        par_list=["Leg_L_02_bindJNT_seg_03_JNT", "Leg_L_02_bindJNT_seg_03_JNT", "chest_M_JNT", "chest_M_JNT","chest_M_JNT", "chest_M_JNT",],
        par_jnt="chest_M_JNT",
        side="L"
    )


    result = splinepart.build_spline_from_curve(
        curve_name="polyToCurve2",
        driver_count=4,
        driven_count=10,
        prefix="R_Tube_A",
        par_list=[ "Leg_R_02_bindJNT_seg_03_JNT", "Leg_R_02_bindJNT_seg_03_JNT", "chest_M_JNT", "chest_M_JNT","chest_M_JNT", "chest_M_JNT",],
        par_jnt="chest_M_JNT",
        side="R"
    )

    

    
    mc.delete('Guides')


    

    ### DEFAULT SKIN
    if not bony:
        bind_joints = [jnt.split('.')[0] for jnt in mc.ls('*.bindJoint')]
        geo = mc.ls(body_mesh)
        for g in geo:
            skc = mc.skinCluster(bind_joints, g, tsb=True, skinMethod=1, bindMethod=0)[0]
            mc.setAttr(skc + '.dqsSupportNonRigid', 1)


    ### SKIN/CURVE IO
    try:
        import ngSkinTools2; ngSkinTools2.workspace_control_main_window(); ngSkinTools2.open_ui()
    except Exception as e:
        print(e)

    # read skin data
    if sp:
        if not not_previs and character != 'Jett' and character != 'Blitz' and character !='Susaka' and character !='Drummer' and character !='Luciana' and character != 'Domingo' and character !='Fisherman':
            sp = sp[:-5]
            sp += '_pvis.json'
        sp_div = sp.split('/')
        dir = '/'.join(sp_div[:-1])
        rWeightNgIO.read_skin(body_mesh, dir, sp_div[-1][:-5])

    import rjg.build_scripts.base_misc as rc
    reload(rc)
    if not_previs:
        try: 
            rc.base_extras(body_mesh, extras, character)
        except Exception as e:
            mc.warning(e)

    # initialize skin clusters as ngST layers
    if not bony:
        for s in mc.ls(type='skinCluster'):
            try:
                rWeightNgIO.init_skc(s)
            except Exception as e:
                print(e)

    rFinal.final(utX=90, utY=0, DutZ=15, utScale=3, polish=False, character=character)


    ##### IMPORT POSE INTERPOLATORS
    if pp and not_previs and not bony:
        import rjg.libs.util as rUtil
        rUtil.import_poseInterpolator(pp)

    # clean up scene
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    # set up textures
    import rjg.post.textures as rTex
    reload(rTex)
    for item in mc.ls('*_MT1'):
        mc.rename(item, item[:-1])
    rTex.set_textures(character)

    rUSD.connectUSDAttr()




    try:
        skin_clusters = mc.ls(type="skinCluster") or []
        if not skin_clusters:
            print("No skinClusters found in the scene.")
            return
        
        for sc in skin_clusters:
            attr = f"{sc}.dqsSupportNonRigid"
            if mc.objExists(attr):
                try:
                    mc.setAttr(attr, 1)
                except Exception as e:
                    print(f"Failed to set {attr}: {e}")
            else:
                print(f"{attr} does not exist on {sc}")
            mc.setAttr(f'{sc}.skinningMethod', 0)
    except Exception as e:
        print(f"Failed")

    # set up control shapes
    if character in []:
        apply_control_file(cp)
        #fix the root ones
        cp_div = cp.split('/')
        dir = '/'.join(cp_div[:-1])
        rCtrlIO.read_ctrls(dir, curve_file=cp_div[-1][:-5])
    
    else:
        if cp:
            cp_div = cp.split('/')
            dir = '/'.join(cp_div[:-1])
            rCtrlIO.read_ctrls(dir, curve_file=cp_div[-1][:-5]) 

    auto_split_all_weights('MODEL')


    apply_control_file(f"{groups}/bobo/character/Rigs/{character}/Controls/controls.json")


    print(f"\n{character} rig build complete.")


    #run('Walker', mp=r'G:\bobo\character\Rigs\Walker\Walker_Model.mb', gp=r'G:\bobo\character\Rigs\Walker\Walker_Guides.mb', ep=r'G:\bobo\character\Rigs\Walker\Walker_Extras.mb', cp=r"G:/bobo/character/Rigs/Walker/Controls/Walker_control_curves.json", sp=r"G:/bobo/character/Rigs/Mech/SkinFiles/Walker_Skins.json", pp=None, face=False, previs=False)

run('Walker', mp=r'G:\bobo\character\Rigs\Walker\Walker_Model.mb', gp=r'G:\bobo\character\Rigs\Walker\Walker_Guides.mb', ep=r'G:\bobo\character\Rigs\Walker\Walker_Extras.mb', cp=None, sp=None, pp=None, face=False, previs=False)