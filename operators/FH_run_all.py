# Samer Aldhaher @samerps 2024
#operator that runs all other operators in order 

import bpy #type: ignore


class BFH_OP_result_draw(bpy.types.Operator):
    """BFH Run All"""
    bl_idname = "object.bfh_run_all"
    bl_label = "BFH Run All"

    #check if bpy.data.filepath exists, this indicate if the blend file actually exists in a directory
    @classmethod
    def poll(cls, context):
        return bpy.data.filepath != ""

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        self.FastHenry_col = my_properties.curve_collection
        if self.FastHenry_col is None:
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}
        elif not bpy.data.is_saved:
            self.report({'WARNING'}, "File must be saved first")
            return {'CANCELLED'}
        else:       
            #run create INP file operator
            bpy.ops.object.bfh_create_inp()

            #run Run FasHenry operator
            bpy.ops.object.bfh_run_fasthenry('INVOKE_DEFAULT')

            # #run Display Results operator 
            # bpy.ops.view3d.bfh_draw_operator('INVOKE_DEFAULT')

            return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(BFH_OP_result_draw.bl_idname, text=BFH_OP_result_draw.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(BFH_OP_result_draw)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(BFH_OP_result_draw)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.bfh_run_all()
