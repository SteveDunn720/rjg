import maya.cmds as cmds
import os


def export_rig(
    export_dir,
    file_name=None,
    set_name="unreal_SET",
    file_type="fbx"
):
    """
    Generic rig exporter for Unreal (or similar pipelines)

    Args:
        export_dir (str): Directory to export into
        file_name (str): Name of the file (no extension). Defaults to scene name.
        set_name (str): Object set to export
        file_type (str): Export format (default: fbx)
    """

    # ----------------------------------------------------------
    # Validate export directory
    # ----------------------------------------------------------
    if not os.path.isdir(export_dir):
        try:
            os.makedirs(export_dir)
            print(f"[Rig Export] Created directory: {export_dir}")
        except Exception as e:
            raise RuntimeError(f"Failed to create directory: {export_dir}\n{e}")

    # ----------------------------------------------------------
    # Resolve file name
    # ----------------------------------------------------------
    if not file_name:
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        file_name = os.path.splitext(scene_name)[0] or "rig_export"

    export_path = os.path.join(export_dir, f"{file_name}.{file_type}")

    # ----------------------------------------------------------
    # Validate set
    # ----------------------------------------------------------
    if not cmds.objExists(set_name):
        raise RuntimeError(f'Set "{set_name}" does not exist.')

    members = cmds.sets(set_name, q=True)
    if not members:
        raise RuntimeError(f'Set "{set_name}" is empty.')

    cmds.select(members, replace=True)

    # ----------------------------------------------------------
    # FBX Export options
    # ----------------------------------------------------------
    options = (
        "FBXExportFileVersion=FBX2020;"
        "FBXExportInAscii=False;"
        "FBXExportUpAxis=y;"
        "FBXExportUseSceneName=0;"
        "FBXExportEmbeddedTextures=0;"
        "FBXExportCameras=0;"
        "FBXExportLights=0;"
        "FBXExportAudio=0;"
        "FBXExportGenerateLog=1;"
        "FBXExportChannels=0;"
        "FBXExportExpressions=0;"
        "FBXExportConstraints=0;"
        "FBXExportSkeletonDefinitions=0;"
        "FBXExportReferencedAssetsContent=1;"
        "FBXExportSmoothingGroups=1;"
        "FBXExportSmoothMesh=1;"
        "FBXExportAnimationOnly=1;"
        "FBXExportBakeComplexAnimation=0;"
        "FBXExportSkins=0;"
        "FBXExportShapes=1;"
        "FBXExportShapeAttributes=1;"
        "FBXExportIncludeChildren=1;"
        "FBXExportInputConnections=0;"
        "FBXExportApplyConstantKeyReducer=0;"
    )

    # ----------------------------------------------------------
    # Export
    # ----------------------------------------------------------
    cmds.file(
        export_path,
        force=True,
        options=options,
        type="FBX export",
        pr=True,
        es=True
    )

    print(f"[Rig Export] Success → {export_path}")
    return export_path