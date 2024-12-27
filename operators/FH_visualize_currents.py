# Samer Aldhaher @samerps 2024
#operator that visualizes currents in planes

import bpy #type: ignore
from ..functions import read_jmag


class BFH_visualize_currents(bpy.types.Operator):
    """BFH Run All"""
    bl_idname = "view3d.bfh_visualize_currents"
    bl_label = "BFH visualize currents"

    #check if bpy.data.filepath exists, this indicate if the blend file actually exists in a directory
    @classmethod
    def poll(cls, context):
        my_properties = context.scene.BFH_properties
        FastHenry_col = my_properties.curve_collection
        return bpy.data.filepath != "" and FastHenry_col is not None

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        self.FastHenry_col = my_properties.curve_collection
        if self.FastHenry_col is None:
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}
        elif not bpy.data.is_saved:
            self.report({'WARNING'}, "File must be saved first")
            return {'CANCELLED'}

        read_jmag.read_jmag

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(BFH_visualize_currents.bl_idname, text=BFH_visualize_currents.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(BFH_visualize_currents)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(BFH_visualize_currents)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.bfh_run_all()
