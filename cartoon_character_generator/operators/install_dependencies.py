import bpy
import subprocess
import sys
import ensurepip


class CCG_OT_InstallDependencies(bpy.types.Operator):
    bl_idname = "ccg.install_dependencies"
    bl_label = "Install Dependencies"
    bl_description = "Install NumPy and OpenCV into Blender Python"

    def execute(self, context):
        packages = [
            "numpy",
            "opencv-python"
        ]

        try:
            ensurepip.bootstrap()

            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip"
            ])

            for package in packages:
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    package
                ])

        except Exception as e:
            self.report({"ERROR"}, f"Failed: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, "Dependencies installed successfully")
        return {"FINISHED"}