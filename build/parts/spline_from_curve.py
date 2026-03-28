from turtle import position
import maya.cmds as mc
from importlib import reload
import re

import rjg.libs.attribute as rAttr
import rjg.build.chain as rChain
import rjg.libs.control.ctrl as rCtrl
import rjg.build.guide as rGuide
import rjg.libs.transform as rXform
from rjg.build.UEface import UEface
from rjg.libs.profile import auto_profiler_tag
import rjg.build.rigModule as rModule
from rjg.libs.spline.matrix_spline import matrix_spline_from_transforms, closest_point_on_matrix_spline, pin_to_matrix_spline
reload(rAttr)
reload(rModule)
reload(rChain)
reload(rCtrl)
reload(rGuide)
reload(rXform)


class spline():
    def __init__(self):
        pass

    def build_spline_from_curve(self, curve_name=None, driver_count=5, driven_count=10, prefix="spline", par_list=[], par_jnt=None, side=None):
        rig_module = rModule.RigModule(side=None, part="Spline")
        
        if not curve_name or not mc.objExists(curve_name):
            raise RuntimeError("Valid curve_name required")

        def build_joints_from_curve(curve, count, label, parent):
            """
            Duplicate, rebuild, and create joints at CV positions
            """
            # Duplicate curve
            dup_curve = mc.duplicate(curve, name=f"{prefix}_{label}_CRV")[0]

            # Rebuild curve to desired CV count
            mc.rebuildCurve(
                dup_curve,
                ch=False,
                rpo=True,
                rt=0,
                end=1,
                kr=0,
                kcp=False,
                kep=True,
                kt=False,
                s=count - 1,  # spans = cvs - 1
                d=3
            )

            joints = []

            # Get CV positions
            cvs = mc.ls(f"{dup_curve}.cv[*]", fl=True)

            for i, cv in enumerate(cvs):
                pos = mc.pointPosition(cv, w=True)
                if parent == False:
                    mc.select(clear=True)
                jnt = mc.joint(
                    p=pos,
                    name=f"{prefix}_{label}_{str(i+1).zfill(2)}_JNT"
                )
                if parent:
                    rig_module.tag_bind_joints(jnt)
                joints.append(jnt)

            return joints, dup_curve

        # -----------------------------------
        # Build driver joints
        # -----------------------------------
        driver_jnts, driver_curve = build_joints_from_curve(curve_name, driver_count, "driver", False)

        # -----------------------------------
        # Build driven joints
        # -----------------------------------
        driven_jnts, driven_curve = build_joints_from_curve(curve_name, driven_count, "driven", True)

        upper_spline = matrix_spline_from_transforms(
                transforms=driver_jnts,
                transforms_to_pin=driven_jnts,
                name=f"{prefix}_Spline",
                create_curve=False
            )

        master_grp = mc.group(empty=True, name = f'{prefix}_grp')
        mc.parent(master_grp, 'RIG')


        for i, jnt in enumerate(driver_jnts):
            driver_control = rCtrl.Control(parent=None, shape="sphere", side=side, suffix='CTRL', name=f'{jnt}', axis='y', group_type='main', rig_type='primary', translate=jnt, rotate=jnt, ctrl_scale=5)
            mc.parentConstraint(driver_control.ctrl, jnt, mo=True)
            if par_list and i < len(par_list):
                mc.parentConstraint(par_list[i], driver_control.top, mo=True)
            else:
                mc.parentConstraint(par_list[-1], driver_control.top, mo=True)
            mc.parent(jnt, driver_control.top, master_grp)
            mc.hide(jnt)

        mc.parent(driven_jnts[0], par_jnt)

        split_joint = driven_jnts[0]
        split_joints: list[str] = driven_jnts
        mc.addAttr(split_joint, longName="split_joints", dataType="string")
        mc.setAttr(f'{split_joint}.split_joints', repr(split_joints), type="string")
    


        return {
            "driver_joints": driver_jnts,
            "driven_joints": driven_jnts,
            "driver_curve": driver_curve,
            "driven_curve": driven_curve
        }

