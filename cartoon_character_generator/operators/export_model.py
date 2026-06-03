import bpy
import os


class CCG_OT_ExportGLB(bpy.types.Operator):
    bl_idname = "ccg.export_glb"
    bl_label = "Export GLB"

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        default="cartoon_character.glb"
    )

    def execute(self, context):
        bpy.ops.export_scene.gltf(
            filepath=self.filepath,
            export_format="GLB",
            use_selection=True
        )

        self.report({"INFO"}, f"Exported: {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}