# Samer Aldhaher @samerps 2024
#this class used BLF to display a HUD which shows the results   

import bpy #type: ignore
import gpu #type: ignore
import blf #type: ignore
import os
import numpy as np #type: ignore
import mathutils #type: ignore
from gpu_extras.batch import batch_for_shader #type: ignore
from ..functions import read_Zc, read_csv_data, reject_objects
    
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

# Function to get the evaluated edges (with modifiers applied)
def get_evaluated_edges(obj):
    if obj.type != 'MESH':
        return [], []

    # Get the evaluated object
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    # Transform vertex coordinates to world space
    vertices = [obj.matrix_world @ v.co for v in eval_mesh.vertices]

    # Extract edge indices
    edge_indices = [(edge.vertices[0], edge.vertices[1]) for edge in eval_mesh.edges]

    # Release the evaluated mesh
    eval_obj.to_mesh_clear()

    return vertices, edge_indices

# Function to get the evaluated mesh (with modifiers applied) and extract vertex and triangle data
def get_object_triangles(obj):

    # Get the evaluated object
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    # Transform vertex coordinates to world space
    vertices = [obj.matrix_world @ v.co for v in eval_mesh.vertices]

    # Extract triangle indices
    triangle_indices = []
    for poly in eval_mesh.polygons:
        if len(poly.vertices) == 3:
            triangle_indices.append((poly.vertices[0], poly.vertices[1], poly.vertices[2]))
        elif len(poly.vertices) == 4:  # Handle quads
            triangle_indices.append((poly.vertices[0], poly.vertices[1], poly.vertices[2]))
            triangle_indices.append((poly.vertices[2], poly.vertices[3], poly.vertices[0]))

    # Release the evaluated mesh
    eval_obj.to_mesh_clear()
    
    return vertices, triangle_indices


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
    
    my_properties = context.scene.BFH_properties
    font_id = 0 

    ### draw background
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": self.background_verts}, indices=((0, 1, 2), (2, 1, 3)))
    gpu.state.blend_set('ALPHA_PREMULT')
    shader.uniform_float("color", (0.12, 0.12, 0.12, .75))
    batch.draw(shader)

    ### draw text header
    blf.size(font_id, self.text_size)
    blf.shadow(font_id, 3, 0, 0, 0, 0.5)
    xpos = self.text_pos[0]
    ypos = self.text_pos[1]
    line_text = "FastHenry Result: "
    blf.color(font_id, 1, 1, 1, 1)
    blf.position(font_id, xpos, ypos, 0)
    text_width, text_height = blf.dimensions(font_id, line_text)
    blf.draw(font_id, line_text + " ")
    
    ### draw object name
    xpos = self.text_pos[0]
    ypos = self.text_pos[1]-text_height*1.25
    line_text = "Object: "
    blf.color(font_id, 1, 1, 1, 1) #white
    blf.position(font_id, xpos, ypos, 0)
    text_width, dummy = blf.dimensions(font_id, line_text)
    blf.draw(font_id, line_text + " ")

    xpos += text_width * 1.25
    line_text = self.obj_name_to_display
    blf.color(font_id, 1, 0.1, 0, 1) #orange
    blf.position(font_id, xpos, ypos, 0)
    text_width, dummy = blf.dimensions(font_id, line_text)
    blf.draw(font_id, line_text + " ")
    
    ### draw self-resistance and self-inductance texts for all frequencies 
    for i in range(len(self.frequency)):          
        xpos = self.text_pos[0]
        ypos = self.text_pos[1]-text_height*(i+2)*1.25
        blf.position(font_id, xpos, ypos, 0)
        
        try:
            line_text =  "Freq.: " + np.array2string(self.frequency_display[i], precision=3) + " Res.: " + np.array2string(self.resistance_display[i], precision=3) + " Ind.: " + np.array2string(self.inductance_display[i], precision=3)
            line_text_words = line_text.split()
        except AttributeError:
            return

        
        for word in line_text_words:
            text_width, dummy = blf.dimensions(font_id, word)
            if word in {'Freq.:', 'Res.:', 'Ind.:'}:
                blf.color(font_id, 1, 1, 1, 1) #white
            else:
                blf.color(font_id, 1, 0.1, 0, 1) #orange
            
            blf.draw(font_id, word + " ")
            xpos += text_width * 1.25
            blf.position(font_id, xpos, ypos, 0)

        xpos_store = xpos + text_width
    
    ### draw mutual inductance texts
    # if self.no_of_objs == 1  or self.mutual_obj_index == self.obj_index:
    #     return
    
    if self.no_of_objs > 1:

   
        ### draw mutual object name
        xpos += text_width
        xpos_store = xpos 
        #xpos_m += text_width 
        ypos = self.text_pos[1]-text_height*1.25
        line_text = "Mutual Curve: "
        blf.color(font_id, 1, 1, 1, 1) #white
        blf.position(font_id, xpos, ypos, 0)
        text_width, dummy = blf.dimensions(font_id, line_text)
        blf.draw(font_id, line_text + " ")

        xpos += text_width * 1.25
        line_text = self.mutual_obj_name_to_display
        blf.color(font_id, 1, 1, 0, 1) #yellow
        blf.position(font_id, xpos, ypos, 0)
        text_width, dummy = blf.dimensions(font_id, line_text)
        blf.draw(font_id, line_text + " ")

        for i in range(len(self.frequency)):          
            xpos = xpos_store
            ypos = self.text_pos[1]-text_height*(i+2)*1.25
            blf.position(font_id, xpos, ypos, 0)
            
            line_text =  "Mut_Ind.: " + np.array2string(self.mutual_inductance_display[i], precision=3)
            line_text_words = line_text.split()
            
            for word in line_text_words:
                text_width, dummy = blf.dimensions(font_id, word)
                if word in {'Mut_Ind.:'}:
                    blf.color(font_id, 1, 1, 1, 1) #white
                else:
                    blf.color(font_id, 1, 1, 0, 1) #yellow
                
                blf.draw(font_id, word + " ")
                xpos += text_width * 1.25
                blf.position(font_id, xpos, ypos, 0)

    ### draw plane texts
    #xpos += text_width
    xpos = xpos_store*1.5
    xpos_store = xpos 
    #xpos_m += text_width 
    ypos = self.text_pos[1]-text_height*1.25
    line_text = "No. of Planes: "
    blf.color(font_id, 1, 1, 1, 1) #white
    blf.position(font_id, xpos, ypos, 0)
    text_width, dummy = blf.dimensions(font_id, line_text)
    blf.draw(font_id, line_text + " ")

    xpos += text_width * 1
    line_text = str(self.plane_count)
    blf.color(font_id, 0, 0.5, 1, 1) #blue
    blf.position(font_id, xpos, ypos, 0)
    text_width, dummy = blf.dimensions(font_id, line_text)
    blf.draw(font_id, line_text + " ")


def draw_callback_pv(self, context):   
    #draw bounding boxes 

    if len(self.trans_bound_coords) == 0:
        return
    
    # if not self.vertices or not self.edge_indices:
    #     return
    
    if not self.vertices or not self.triangle_indices:
        return

    # TRI draw shader
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)

    # Create the batch for drawing the triangles of the object
    batch = batch_for_shader(shader, 'TRIS', {"pos": self.vertices}, indices=self.triangle_indices)
    shader.uniform_float("color", (1.0, 0.1, 0.0, 0.25))  # Green with 50% transparency
    batch.draw(shader)

    # # Edge draw shader
    # shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    # gpu.state.blend_set('ALPHA')
    # gpu.state.line_width_set(2.0)

    # # Create the batch for drawing the edges of the object
    # batch = batch_for_shader(shader, 'LINES', {"pos": self.vertices}, indices=self.edge_indices)
    # shader.uniform_float("color", (0.0, 1.0, 0.0, 0.5))  # Green with 50% transparency
    # batch.draw(shader)
    

    if self.no_of_objs > 1 and self.mutual_obj_index != self.obj_index:
        # TRI draw shader
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)

        # Create the batch for drawing the triangles of the object
        batch = batch_for_shader(shader, 'TRIS', {"pos": self.vertices_mutual}, indices=self.triangle_indices_mutual)
        shader.uniform_float("color", (1.0, 1.0, 0.0, 0.25))  # Green with 50% transparency
        batch.draw(shader)

        #draw line from selected object to mutual object, this is done by getting average coordinates of the bounding box
        avg_obj_bound = np.average(np.array(self.trans_bound_coords), axis=0)
        avg_mutual_obj_bound = np.average(np.array(self.mutual_bound_coords), axis=0)
        obj_to_mutual_line = (tuple(avg_obj_bound.tolist()), tuple(avg_mutual_obj_bound.tolist()))
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": obj_to_mutual_line})  
        shader.uniform_float("color", (1, 1, 0, 0.25)) #yellow   
        batch.draw(shader)

    #draw boundboxes for planes
    if self.plane_count > 0:
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.uniform_float("color", (0, 0.5, 1, 0.25)) #blue
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        for obj in self.FastHenry_plane_col.objects:
            plane_bound_coords = obj_bounds(obj)
            plane_vertices, plane_triangle_indices = get_object_triangles(obj)
            # batch = batch_for_shader(shader, 'LINES', {"pos": plane_bound_coords}, indices=self.indices)
            batch = batch_for_shader(shader, 'TRIS', {"pos": plane_vertices}, indices=plane_triangle_indices)
            batch.draw(shader)

    # restore opengl defaults
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')

class BFH_OP_result_draw(bpy.types.Operator):
    """Draw Fast Henry result"""
    bl_idname = "view3d.bfh_draw_operator"
    bl_label = "BFH Draw Operator"

    #check if bpy.data.filepath exists, this indicate if the blend file actually exists in a directory
    @classmethod
    def poll(cls, context):
        return bpy.data.filepath != ""

    def modal(self, context, event):

        context.area.tag_redraw()

        #### below are for scrolling through objects for  bound box drawing
        #first run for bound box drawing
        if self.first_run == True:
            self.obj_index = 0
            self.first_run = False

            if self.sim_selected:
                current_obj = bpy.context.selected_objects[self.obj_index]
            else:
                current_obj = self.FastHenry_col.objects[self.obj_index] 
            self.trans_bound_coords = obj_bounds(current_obj)
            self.obj_name_to_display = current_obj.name

            # Get the vertices and triangles of the active object
            self.vertices, self.triangle_indices = get_object_triangles(current_obj)
            
            # # Get the evaluated vertices and edges of the active object
            # self.vertices, self.edge_indices = get_evaluated_edges(current_obj)

            #check for mutual inductance
            if self.no_of_objs > 1 or len(bpy.context.selected_objects) > 1:
                if self.sim_selected:
                    mutual_obj = bpy.context.selected_objects[self.mutual_obj_index]
                else:
                    mutual_obj = self.FastHenry_col.objects[self.mutual_obj_index]

                self.mutual_bound_coords = obj_bounds(mutual_obj)
                self.mutual_obj_name_to_display = mutual_obj.name
                # Get the vertices and triangles of the mutual object
                self.vertices_mutual, self.triangle_indices_mutual = get_object_triangles(mutual_obj)

            ### planes
            if self.FastHenry_plane_col is None:
                self.plane_count = 0
            else:
                self.plane_count = len(self.FastHenry_plane_col.objects)

        ####
        #prepare self-resistance and self-inductance for displaying for each frequency 
        self.frequency_display = []
        self.resistance_display = []
        self.inductance_display = []
        j = self.obj_index
        for i in range(len(self.frequency)):
            self.frequency_display.append(self.frequency[i])
            self.resistance_display.append(self.resistance[i][j][j])
            self.inductance_display.append(self.inductance[i][j][j])

        ### prepare coupling (mutual inductance) data, check if we actually have more than one object 
        if self.no_of_objs > 1:
            self.mutual_inductance_display = []
            k = self.mutual_obj_index
            for i in range(len(self.frequency)):
                if self.mutual_obj_index != self.obj_index:
                    self.mutual_inductance_display.append(self.inductance[i][j][k])
                else:
                    self.mutual_inductance_display.append(np.int8(0))
                 
        np.set_printoptions(formatter={'float': lambda x: format(x, '.2E')})

        ###events

        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            self.obj_index += 1
            if self.obj_index == self.no_of_objs:
                self.obj_index = 0
            
            if self.sim_selected:
                current_obj = bpy.context.selected_objects[self.obj_index]
            else:
                current_obj = self.FastHenry_col.objects[self.obj_index]  
            
            self.trans_bound_coords = obj_bounds(current_obj)
            self.obj_name_to_display = current_obj.name

            # Get the vertices and triangles of the active object
            self.vertices, self.triangle_indices = get_object_triangles(current_obj)

            # # Get the evaluated vertices and edges of the active object
            # self.vertices, self.edge_indices = get_evaluated_edges(current_obj)
                                                                        
            return {'RUNNING_MODAL'}
            
        elif event.type == 'UP_ARROW' and event.value == 'PRESS':
            self.obj_index -=1
            if self.obj_index == -1:
                self.obj_index = self.no_of_objs -1

            if self.sim_selected:
                current_obj = bpy.context.selected_objects[self.obj_index]
            else:
                current_obj = self.FastHenry_col.objects[self.obj_index] 

            self.trans_bound_coords = obj_bounds(current_obj)
            self.obj_name_to_display = current_obj.name

            # Get the vertices and triangles of the active object
            self.vertices, self.triangle_indices = get_object_triangles(current_obj)

            # # Get the evaluated vertices and edges of the active object
            # self.vertices, self.edge_indices = get_evaluated_edges(current_obj)

            return {'RUNNING_MODAL'}

        elif event.type == 'LEFT_ARROW' and event.value == 'PRESS' and self.no_of_objs > 1: #only activate of there are more than one objects
            self.mutual_obj_index += 1
            if self.mutual_obj_index == self.obj_index:
                self.mutual_obj_index +=1
            if self.mutual_obj_index == self.no_of_objs:
                if  self.obj_index == 0:
                    self.mutual_obj_index = 1
                else:
                    self.mutual_obj_index = 0

            if self.sim_selected:
                mutual_obj = bpy.context.selected_objects[self.mutual_obj_index]
            else:
                mutual_obj = self.FastHenry_col.objects[self.mutual_obj_index] 

            self.mutual_bound_coords = obj_bounds(mutual_obj) #get world transformed coordinates of bounding box around mutual object
            self.mutual_obj_name_to_display = mutual_obj.name

            # Get the vertices and triangles of the mutual object
            self.vertices_mutual, self.triangle_indices_mutual = get_object_triangles(mutual_obj)

            return {'RUNNING_MODAL'}
        
        elif event.type == 'RIGHT_ARROW' and event.value == 'PRESS' and self.no_of_objs > 1: #only activate of there are more than one objects
            self.mutual_obj_index -=1
            if self.mutual_obj_index == self.obj_index:
                self.mutual_obj_index -=1
            if self.mutual_obj_index == -1:
                if self.obj_index == self.no_of_objs -1:
                    self.mutual_obj_index = self.no_of_objs - 2
                else:
                    self.mutual_obj_index = self.no_of_objs -1
                    
            if self.sim_selected:
                mutual_obj = bpy.context.selected_objects[self.mutual_obj_index]
            else:
                mutual_obj = self.FastHenry_col.objects[self.mutual_obj_index] 

            self.mutual_bound_coords = obj_bounds(mutual_obj) #get world transformed coordinates of bounding box around mutual object
            self.mutual_obj_name_to_display = mutual_obj.name

            # Get the vertices and triangles of the mutual object
            self.vertices_mutual, self.triangle_indices_mutual = get_object_triangles(mutual_obj)

            return {'RUNNING_MODAL'}
        
        if event.type in {'MIDDLEMOUSE', 'MOUSEMOVE'}:
            return {'PASS_THROUGH'}
        
        elif event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_pv, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):

        if context.area.type == 'VIEW_3D':
            my_properties = context.scene.BFH_properties
            # the arguments we pass the the callback
            args = (self, context)
            
            #initialise draw function for text
            init()

            #prepare text and colours for draw function,  based on viewport width and length
             
            self.text_pos = [context.area.width/10, context.area.height/4.5]
            self.text_size = my_properties.text_size * context.area.width/50

            background_vert0 = (0,0)
            background_vert1 = (context.area.width,0)
            background_vert2 = (0, context.area.height/4)
            background_vert3 = (context.area.width, context.area.height/4)
            self.background_verts = (background_vert0, background_vert1, background_vert2, background_vert3)
            
            self.first_run = True

            self.obj_name_to_display = " "  #had to define this here, was getting an error saying object has no obj_name_to_display
            # self.frequency_display = []
            # self.resistance_display = []
            # self.inductance_display = []

            self.trans_bound_coords = []
            self.indices = (
                (1, 0), (0, 3), (3, 2), (2, 1),
                (3, 7), (7, 6), (6, 2),
                (0, 4), (4, 5), (5, 1),
                (4, 7), (5, 6)
                )
             #check if curve collection is set, check for non-compatible objects in collection, check if length of CSV results match number of objects

            if my_properties.curve_collection is None:
                self.report({'WARNING'}, "Empty Collection")
                return {'CANCELLED'}
            else:
                self.FastHenry_col = my_properties.curve_collection
                self.FastHenry_plane_col = my_properties.plane_collection
                self.sim_selected = my_properties.sim_selected
                reject_objects.reject_objects(self, context, my_properties)

                # this needs to be rewritten once storing object name in CSV data is implemented, it is better then to compare objects names instead of using len
                if my_properties.sim_selected:
                    self.no_of_objs = len(bpy.context.selected_objects)
                else:
                    self.no_of_objs = len(self.FastHenry_col.objects)
                self.obj_index = 0
                self.mutual_obj_index = 1
            
            ### get data from csv files 
            self.frequency, self.resistance , self.inductance = read_csv_data.read_csv_data()

            #check if csv data is empty
            if len(self.frequency) == 0:
                self.report({'WARNING'}, "no CSV data")
                return {'CANCELLED'}
            
            #check if csv data matches the number of the objects in FastHenry collection, pick resistance or inductance
            if len(self.resistance[0][:]) != self.no_of_objs:
                self.report({'WARNING'}, "CSV data does not match number of objects, probably outdated")
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
    self.layout.operator(BFH_OP_result_draw.bl_idname, text="BFH Result Draw Operator")

# Register and add to the "view" menu (required to also use F3 search "Modal Draw Operator" for quick access).
def register():
    bpy.utils.register_class(BFH_OP_result_draw)
    #bpy.types.VIEW3D_MT_view.append(menu_func)

def unregister():
    bpy.utils.unregister_class(BFH_OP_result_draw)
    #bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()
