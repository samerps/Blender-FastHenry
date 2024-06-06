#JUNE 2024
#this class used BLF to display a HUD which shows the results   

import bpy #type: ignore
import gpu #type: ignore
import blf #type: ignore
import os
from gpu_extras.batch import batch_for_shader #type: ignore
from ..functions import read_Zc

def is_float(string): #function to check if string contains letters or float
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def init():
    font_info = {
    "font_id": 0,
    "handler": None,}

    # Create a new font object, use external ttf file.
    font_path = bpy.path.abspath('//Zeyada.ttf')
    # Store the font indice - to use later.
    if os.path.exists(font_path):
        font_info["font_id"] = blf.load(font_path)
        print("font path exist")
    else:
        # Default font.
        font_info["font_id"] = 0
    

def draw_callback_px(self, context):
    
    my_properties = context.window_manager.BFH_properties
    font_id = 0 

    # draw some text
    blf.size(font_id, 17.0)
    blf.color(font_id, self.WHITE[0], self.WHITE[1], self.WHITE[2], self.WHITE[3])
    blf.position(font_id, self.mouse_pos[0], self.mouse_pos[1], 0)
    blf.draw(font_id, "FastHenry Operator" )

    for i, row in enumerate(self.result_list):
        xpos = self.mouse_pos[0]
        ypos = self.mouse_pos[1]-25-25*i
        blf.position(font_id, xpos, ypos, 0)
        line_text = "Freq.: " + f"{row[0]:.2e}" + ", Res.: " + f"{row[1]:.3e}"+ ", Ind.: " + f"{row[2]:.3e}"
        line_text_words = line_text.split()
        for i, word in enumerate(line_text_words):
            text_width, text_height = blf.dimensions(font_id, word)
            if i % 2 == 0:
                blf.color(font_id, self.WHITE[0], self.WHITE[1], self.WHITE[2], self.WHITE[3])
            else:
                blf.color(font_id, self.RED[0], self.RED[1], self.RED[2], self.RED[3])
            blf.draw(font_id, word + " ")
            xpos += text_width * 1.25
            blf.position(font_id, xpos, ypos, 0)
    
    # restore opengl defaults
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')

class BFH_OP_result_draw(bpy.types.Operator):
    """Draw Fast Henry result"""
    bl_idname = "view3d.bfh_draw_operator"
    bl_label = "BFH Draw Operator"

    def modal(self, context, event):

        context.area.tag_redraw()
        if event.type == 'MOUSEMOVE':
            self.mouse_pos =  (event.mouse_region_x+25, event.mouse_region_y)

        if event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            my_properties = context.window_manager.BFH_properties
            # the arguments we pass the the callback
            args = (self, context)
            
            #read impedance output file and update property group values 
            read_status, frequency_list, inductance_list, resistance_list = read_Zc.read_Zc()
            if read_status == 'no Zc file':
                self.report()
                return {{'WARNING'}, "no Zc file"}
            if (len(frequency_list) == len(inductance_list)) and (len(frequency_list) == len(inductance_list)):
                pass
            else:
                self.report()
                return {{'WARNING'}, "results read from Zc file have different lengths"}
            
            #combine all results to single list
            self.result_list =[]
            for i, row in enumerate(frequency_list):
                self.result_list.append((frequency_list[i], resistance_list[i], inductance_list[i]))

            #initialise draw function
            init()

            #prepare text and colours for draw function
            self.RED = (1, 0, 0, 0.75)
            self.WHITE = (1, 1, 1, 0.75)
            
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
        

def menu_func(self, context):
    self.layout.operator(BFH_OP_result_draw.bl_idname, text="Modal Draw Operator2")


# Register and add to the "view" menu (required to also use F3 search "Modal Draw Operator" for quick access).
def register():
    bpy.utils.register_class(BFH_OP_result_draw)
    #bpy.types.VIEW3D_MT_view.append(menu_func)

def unregister():
    bpy.utils.unregister_class(BFH_OP_result_draw)
    #bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()
