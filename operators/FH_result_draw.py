#JUNE 2024
#this class used BLF to display a HUD which shows the results   

import bpy #type: ignore
import gpu #type: ignore
import blf #type: ignore
import os
import mathutils #type: ignore
from gpu_extras.batch import batch_for_shader #type: ignore
from ..functions import read_Zc
    
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
    
def obj_bounds(obj):
    #get bounding box vertices of object with transform 
    mat_world = obj.matrix_world
    bound_coords = obj.bound_box
    trans_bound_coords = []
    
    for co in bound_coords:
        trans_co_vec = []
        co_vec = mathutils.Vector(co[:])
        trans_co_vec = mat_world @ co_vec
        trans_bound_coords.append(trans_co_vec)      
    return trans_bound_coords


def draw_callback_px(self, context):
    
    my_properties = context.window_manager.BFH_properties
    font_id = 0 

    # draw some text
    blf.size(font_id, 40.0)
    blf.shadow(font_id, 3, 0, 0, 0, 0.5)
    blf.color(font_id, self.WHITE[0], self.WHITE[1], self.WHITE[2], self.WHITE[3])
    blf.position(font_id, self.text_pos[0], self.text_pos[1], 0)
    word = "FastHenry Result: "
    blf.draw(font_id, word)
    text_width, text_height = blf.dimensions(font_id, word)
    
    for i in range(len(my_properties.frequency_list)):          
        xpos = self.text_pos[0]
        ypos = self.text_pos[1]-text_height*(i+1)*1.25
        blf.position(font_id, xpos, ypos, 0)
        if my_properties.frequency_list[i] == 0:
            line_text = ""
        else:
            line_text =  "Freq.: " + f"{my_properties.frequency_list[i]:.2e}" + ", Res.: " + f"{my_properties.resistance_result[i]:.3e}" + ", Ind.: " + f"{my_properties.inductance_result[i]:.3e}"
        line_text_words = line_text.split()
        for i, word in enumerate(line_text_words):
            text_width, dummy = blf.dimensions(font_id, word)
            if i % 2 == 0:
                blf.color(font_id, self.WHITE[0], self.WHITE[1], self.WHITE[2], self.WHITE[3])
            else:
                blf.color(font_id, self.RED[0], self.RED[1], self.RED[2], self.RED[3])
            blf.draw(font_id, word + " ")
            xpos += text_width * 1.25
            blf.position(font_id, xpos, ypos, 0)

def draw_callback_pv(self, context):   
    #draw bounding boxes 

    if len(self.trans_bound_coords) == 0:
        print("returned")
        return
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": self.trans_bound_coords}, indices=self.indices)
    
    shader.uniform_float("color", (1, 0, 0, 1))
    batch.draw(shader)

    # restore opengl defaults
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')

class BFH_OP_result_draw(bpy.types.Operator):
    """Draw Fast Henry result"""
    bl_idname = "view3d.bfh_draw_operator"
    bl_label = "BFH Draw Operator"

    def modal(self, context, event):

        context.area.tag_redraw()

        #first run
        if self.first_run == True:
            self.obj_index = 0
            self.first_run = False
            current_obj = self.FastHenry_col.objects[self.obj_index] 
            self.trans_bound_coords = obj_bounds(current_obj)
                            
        if event.type == 'WHEELUPMOUSE':
            self.obj_index += 1
            if self.obj_index == self.no_of_objs:
                self.obj_index = 0

            current_obj = self.FastHenry_col.objects[self.obj_index]  
            self.trans_bound_coords = obj_bounds(current_obj)
            return {'RUNNING_MODAL'}
            
        elif event.type == 'WHEELDOWNMOUSE':
            self.obj_index -=1
            if self.obj_index == -1:
                self.obj_index = self.no_of_objs -1
            current_obj = self.FastHenry_col.objects[self.obj_index]  
            self.trans_bound_coords = obj_bounds(current_obj)
            return {'RUNNING_MODAL'}    
            
        elif event.type in {'MIDDLEMOUSE', 'MOUSEMOVE'}:
            return {'PASS_THROUGH'}
        
        elif event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_pv, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            my_properties = context.window_manager.BFH_properties
            # the arguments we pass the the callback
            args = (self, context)
            
            #initialise draw function
            init()

            #prepare text and colours for draw function
            self.text_pos = [200,300]
            self.RED = (1, 1, 0, 1)
            self.WHITE = (1, 1, 1, 1)

            #check if "FastHenry" collection exist, then define parameters related to drawing bounding box around objects in the collection
            FastHenry_col_found = False
            
            self.first_run = True
            self.trans_bound_coords = []
            self.indices = (
                (1, 0), (0, 3), (3, 2), (2, 1),
                (3, 7), (7, 6), (6, 2),
                (0, 4), (4, 5), (5, 1),
                (4, 7), (5, 6)
                )
            for col in bpy.data.collections:
                if col.name == 'FastHenry':
                    FastHenry_col_found = True
                    #print(FastHenry_col_found)
                    self.FastHenry_col = col
                    self.no_of_objs = len(col.objects)
                    #print(self.no_of_objs)
                    self.obj_index = 0
                    
            if FastHenry_col_found == False:
                print("no FastHenry Collection")
                #bpy.types.SpaceView3D.draw_handler_remove(self._handle_px 'WINDOW')
                #bpy.types.SpaceView3D.draw_handler_remove(self._handle_pv 'WINDOW')
                self.report({'WARNING'}, "Active space must be a View3d")
                return {'CANCELLED'}
            
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            self._handle_pv = bpy.types.SpaceView3D.draw_handler_add(draw_callback_pv, args, 'WINDOW', 'POST_VIEW')
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
