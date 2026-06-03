import bpy


class CCG_OT_ImportFrontImage(bpy.types.Operator):
    bl_idname = "ccg.import_front_image"
    bl_label = "Import Front Image"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.ccg_front_image_path = self.filepath
        self.report({"INFO"}, f"Loaded image: {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}