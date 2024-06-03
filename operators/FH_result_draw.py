import bpy
import gpu
from gpu_extras.batch import batch_for_shader

def draw_callback_px(self, context):
    
    font_id = 0  # XXX, need to find out how best to get this.

    # draw some text
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20.0)
    #blf.draw(font_id, "FastHenry Operator " + str(len(self.mouse_path)))
    blf.draw(font_id, "FastHenry Operator " + self.FH_result)


    # restore opengl defaults
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')

class FH_result_draw_OP(bpy.types.Operator):
    """Draw Fast Henry result"""
    bl_idname = "view3d.modal_draw_operator"
    bl_label = "Simple Modal View3D Operator"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            self.FH_result = 0

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
        

def menu_func(self, context):
    self.layout.operator(FH_result_draw_OP.bl_idname, text="Modal Draw Operator")


# Register and add to the "view" menu (required to also use F3 search "Modal Draw Operator" for quick access).
def register():
    bpy.utils.register_class(FH_result_draw_OP)
    #bpy.types.VIEW3D_MT_view.append(menu_func)

def unregister():
    bpy.utils.unregister_class(FH_result_draw_OP)
    #bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()
