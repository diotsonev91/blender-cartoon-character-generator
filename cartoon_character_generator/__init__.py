bl_info = {
    "name": "Cartoon Character Generator",
    "author": "Deyan + ChatGPT",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Cartoon Gen",
    "description": "Generate simple low-poly cartoon character mesh from image silhouette",
    "category": "Object",
}

import bpy

from .ui.panel import CCG_PT_MainPanel
from .operators.import_image import CCG_OT_ImportFrontImage
from .operators.generate_mesh import CCG_OT_GenerateMesh
from .operators.export_model import CCG_OT_ExportGLB
from .operators.install_dependencies import CCG_OT_InstallDependencies


classes = (
    CCG_OT_InstallDependencies,
    CCG_OT_ImportFrontImage,
    CCG_OT_GenerateMesh,
    CCG_OT_ExportGLB,
    CCG_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ccg_front_image_path = bpy.props.StringProperty(
        name="Front Image",
        subtype="FILE_PATH",
        default=""
    )

    bpy.types.Scene.ccg_depth = bpy.props.FloatProperty(
        name="Depth",
        default=0.5,
        min=0.05,
        max=5.0
    )

    bpy.types.Scene.ccg_simplify_epsilon = bpy.props.FloatProperty(
        name="Simplify",
        default=4.0,
        min=1.0,
        max=30.0
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ccg_front_image_path
    del bpy.types.Scene.ccg_depth
    del bpy.types.Scene.ccg_simplify_epsilon


if __name__ == "__main__":
    register()