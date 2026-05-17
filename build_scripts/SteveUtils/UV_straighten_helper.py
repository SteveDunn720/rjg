import maya.cmds as cmds

def straighten_uvs_scale():
    sel = cmds.ls(sl=True, fl=True)

    if not sel:
        cmds.warning("Select edges or UVs.")
        return

    # Detect selection type
    if ".e[" in sel[0]:
        # Convert edges → UVs
        uvs = cmds.polyListComponentConversion(sel, toUV=True)
        uvs = cmds.ls(uvs, fl=True)
    elif ".map[" in sel[0]:
        uvs = sel
    else:
        cmds.warning("Please select edges or UVs.")
        return

    if not uvs:
        cmds.warning("No UVs found.")
        return

    # Deduplicate
    uvs = list(set(uvs))

    # Select UVs (important for polyEditUV scaling)
    cmds.select(uvs)

    # Get positions
    u_vals = []
    v_vals = []

    uv_pos = {}

    for uv in uvs:
        u, v = cmds.polyEditUV(uv, q=True)
        uv_pos[uv] = (u, v)
        u_vals.append(u)
        v_vals.append(v)

    # Compute ranges
    u_range = max(u_vals) - min(u_vals)
    v_range = max(v_vals) - min(v_vals)

    # Compute pivot (center)
    pivot_u = sum(u_vals) / len(u_vals)
    pivot_v = sum(v_vals) / len(v_vals)

    # Decide axis and scale
    if u_range > v_range:
        # Horizontal → flatten V
        cmds.polyEditUV(pu=pivot_u, pv=pivot_v, su=1, sv=0)
    else:
        # Vertical → flatten U
        cmds.polyEditUV(pu=pivot_u, pv=pivot_v, su=0, sv=1)

    print("UVs straightened via scaling.")