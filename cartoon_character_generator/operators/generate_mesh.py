import bpy


class CCG_OT_GenerateMesh(bpy.types.Operator):
    bl_idname = "ccg.generate_mesh"
    bl_label = "Generate Mesh"

    def execute(self, context):
        image_path = context.scene.ccg_front_image_path

        print("=== CCG DEBUG ===")
        print("Image path:", image_path)

        if not image_path:
            self.report({"ERROR"}, "No front image selected")
            return {"CANCELLED"}

        try:
            from ..core.silhouette import extract_mask
            from ..core.contour import find_largest_contour, simplify_contour
            from ..core.mesh_builder import create_extruded_mesh_from_contour
            from ..core.body_analyzer import find_body_landmarks, split_body_masks

            mask = extract_mask(image_path)
            print("Mask shape:", mask.shape)
            print("Mask white pixels:", mask.sum() / 255)

            landmarks = find_body_landmarks(mask)
            print("Detected landmarks:", landmarks)

            parts = split_body_masks(mask, landmarks)

            created_objects = []

            ys, xs = mask.nonzero()
            global_center = (
                (xs.min() + xs.max()) / 2,
                (ys.min() + ys.max()) / 2,
            )

            for part_name, part_mask in parts.items():
                print("Generating part:", part_name)

                contour = find_largest_contour(part_mask)

                simplified = simplify_contour(
                    contour,
                    context.scene.ccg_simplify_epsilon
                )

                obj = create_extruded_mesh_from_contour(
                    simplified,
                    depth=context.scene.ccg_depth,
                    center=global_center
                )

                obj.name = f"CCG_{part_name}"
                created_objects.append(obj)

                print("Created object:", obj.name)
                print("Vertices:", len(obj.data.vertices))
                print("Faces:", len(obj.data.polygons))

            print("Total created objects:", len(created_objects))
            print("=================")

        except Exception as e:
            print("CCG ERROR:", e)
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        self.report({"INFO"}, "Mesh generated")
        return {"FINISHED"}