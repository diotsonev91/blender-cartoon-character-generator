import bpy


class CCG_PT_MainPanel(bpy.types.Panel):
    bl_label = "Cartoon Generator MVP"
    bl_idname = "CCG_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Cartoon Gen"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Setup")
        layout.operator("ccg.install_dependencies", text="Install OpenCV + NumPy")

        layout.separator()

        layout.label(text="Input")
        layout.prop(scene, "ccg_front_image_path")

        layout.operator("ccg.import_front_image", text="Load Front Image")

        layout.separator()

        layout.label(text="Mesh Settings")
        layout.prop(scene, "ccg_depth")
        layout.prop(scene, "ccg_simplify_epsilon")

        layout.operator("ccg.generate_mesh", text="Generate Mesh")

        layout.separator()

        layout.operator("ccg.export_glb", text="Export GLB")