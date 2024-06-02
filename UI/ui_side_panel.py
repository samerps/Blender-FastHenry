import bpy #type: ignore

class FH_sidebar(bpy.types.Panel):
    """Display test button"""
    bl_label = "Blender Fast Henry"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender FH"

    def draw(self, context):
        col = self.layout.column(align=True)


 
