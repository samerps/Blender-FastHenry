#operator that runs all other operators in order 

import bpy #type: ignore


class BFH_OP_result_draw(bpy.types.Operator):
    """BFH Run All"""
    bl_idname = "object.bfh_run_all"
    bl_label = "BFH Run All"

    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None

    def execute(self, context):
        
        #run create INP file operator
        bpy.ops.object.bfh_create_inp()

        #run Run FasHenry operator
        bpy.ops.object.bfh_run_fastfield('EXEC_DEFAULT')

        #run Display Results operator 
        bpy.ops.view3d.bfh_draw_operator('INVOKE_DEFAULT')

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
