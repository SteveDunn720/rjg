import maya.cmds as cmds

def get_mirror_name(name):
    if "_R_" in name:
        return name.replace("_R_", "_L_")
    elif "_L_" in name:
        return name.replace("_L_", "_R_")
    return None

def mirror_curve_shapes(source, target, axis='x'):
    src_shapes = cmds.listRelatives(source, shapes=True, type='nurbsCurve', fullPath=True) or []
    tgt_shapes = cmds.listRelatives(target, shapes=True, type='nurbsCurve', fullPath=True) or []

    if not src_shapes or not tgt_shapes:
        cmds.warning(f"Skipping {source} -> {target}: Missing curve shapes")
        return

    if len(src_shapes) != len(tgt_shapes):
        cmds.warning(f"Shape count mismatch: {source} ({len(src_shapes)}) vs {target} ({len(tgt_shapes)})")
        return

    for s_shape, t_shape in zip(src_shapes, tgt_shapes):
        src_cvs = cmds.ls(f"{s_shape}.cv[*]", fl=True)
        tgt_cvs = cmds.ls(f"{t_shape}.cv[*]", fl=True)

        if len(src_cvs) != len(tgt_cvs):
            cmds.warning(f"CV mismatch in shapes: {s_shape} vs {t_shape}")
            continue

        for i in range(len(src_cvs)):
            pos = cmds.pointPosition(src_cvs[i], world=True)

            # Mirror
            if axis == 'x':
                mirrored = (-pos[0], pos[1], pos[2])
            elif axis == 'y':
                mirrored = (pos[0], -pos[1], pos[2])
            elif axis == 'z':
                mirrored = (pos[0], pos[1], -pos[2])
            else:
                mirrored = pos

            cmds.xform(tgt_cvs[i], worldSpace=True, translation=mirrored)
    print(f"Mirrored {source} to {target}")

def mirror_selected_curves(axis='x'):
    selection = cmds.ls(selection=True, type='transform')

    if not selection:
        cmds.warning("No curves selected.")
        return

    for obj in selection:
        mirror_name = get_mirror_name(obj)

        if not mirror_name or not cmds.objExists(mirror_name):
            cmds.warning(f"No mirror found for {obj}")
            continue

        mirror_curve_shapes(obj, mirror_name, axis)

# Run
# mirror_selected_curves(axis='x')