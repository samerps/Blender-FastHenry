# Samer Aldhaher @samerps 2024
#this class only generates the FastHenry INP file from the selected object 

import bpy #type: ignore
import os 
from ..functions import reject_objects

def create_inp(self, context):
    my_properties = context.scene.BFH_properties
    #Fast Henry parameters#
    fmin = my_properties.fmin*1e6
    #fmax = my_properties.fmax*1e6
    fmax = fmin * (10**my_properties.fmultiplier)
    ndec = my_properties.ndec
    nhinc = my_properties.nhinc
    nwinc = my_properties.nwinc
    rh = my_properties.rh
    rw = my_properties.rw

    zdefault = 0
    sigma = my_properties.conductivity*1000 #fasthenry sigma units 1/(mm*Ohms)
    units = my_properties.units_enum
    scale = my_properties.mesh_scale

    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)

    textfile = open(my_properties.INP_file_name + ".inp", "w")
    textfile.write('* Blender Fast Henry Output' + '\n') #fasthenry format first line must contain a comment
    textfile.write('.units ' + units +  '\n')
    textfile.write('.default z={} sigma={} nhinc={} nwinc={} rh={} rw={} \n' .format(zdefault, sigma, nhinc, nwinc, rh, rw))
  
    node_index = 1
    element_index = 1

    sim_selected = my_properties.sim_selected

    ##planes
    textfile.write('* Planes \n')
    if self.plane_col:
        for j, obj in enumerate(self.plane_col.objects):
            
            #need a better way to get actual socket names instead of socket numbers, code will break if socket arrangement got changed
            seg1 = obj.modifiers["BFH_plane"]["Socket_8"]-1    
            seg2 = obj.modifiers["BFH_plane"]["Socket_10"]-1
            thickness = obj.modifiers["BFH_plane"]["Socket_9"] * scale

            obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            vert0 = obj.attributes['vert0'].data[0].vector * scale
            vert1 = obj.attributes['vert1'].data[0].vector * scale
            vert3 = obj.attributes['vert3'].data[0].vector * scale
  
            textfile.write('GFHPlane{} \n' .format(j))
            textfile.write('+ x1={} y1={} z1={} \n' .format(vert0.x, vert0.y, vert0.z))
            textfile.write('+ x2={} y2={} z2={} \n' .format(vert1.x, vert1.y, vert1.z))
            textfile.write('+ x3={} y3={} z3={} \n' .format(vert3.x, vert3.y, vert3.z))
            textfile.write('+ thick = {} \n' .format(thickness))
            textfile.write('+ seg1 = {} seg2 = {} \n' .format(seg1, seg2))

    for obj_idx, obj in enumerate(self.FastHenry_col.objects):
        if sim_selected:
            if obj in bpy.context.selected_objects:
                pass
            else:
                continue
        
        ### Save reference points if connected to plane
        if obj.modifiers["BFH_curve"]["Socket_7"]:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            eval_mesh = eval_obj.to_mesh()
            mat_world = obj.matrix_world

            plane_pos1 = mat_world @ eval_mesh.attributes["plane_point1"].data[0].vector
            plane_pos2 = mat_world @ eval_mesh.attributes["plane_point2"].data[0].vector

            ### SAVE REFERENCE TO PLANE POINTS  
            textfile.write('* SAVE PLANE POINTS \n')
            textfile.write('+ nin{} ({},{},{}) \n' .format(obj_idx, plane_pos1.x*scale, plane_pos1.y*scale,  plane_pos1.z*scale))
            textfile.write('+ nout{} ({},{},{}) \n' .format(obj_idx, plane_pos2.x*scale, plane_pos2.y*scale,  plane_pos2.z*scale))
    
    for obj_idx, obj in enumerate(self.FastHenry_col.objects):
        if sim_selected:
            if obj in bpy.context.selected_objects:
                pass
            else:
                continue

        ### if object is a curve with FH_Curve modifier
        if obj.type == 'CURVE' and 'BFH_curve' in obj.modifiers:           
            obj_mesh = obj.to_mesh()

            w = obj.modifiers["BFH_curve"]["Socket_2"]*scale 
            h = obj.modifiers["BFH_curve"]["Socket_3"]*scale

            #get vertices of selected object
            object_vertices = obj_mesh.vertices
            mat_world = obj.matrix_world
            vertex_co_global = []

            for vertex in object_vertices:
                vertex_co_global.append((mat_world @ vertex.co) * scale)

            first_node_index = node_index
            last_node_index = node_index + len(vertex_co_global)-1
            ###NODES
            textfile.write('* NODES \n')
            for co in vertex_co_global:
                textfile.write('N{} x={} y={} z={} \n' .format(node_index, co.x, co.y, co.z))
                node_index +=1
            
            ###ELEMENTS
            textfile.write('* SEGMENTS \n')
            for i in range(len(vertex_co_global)-1):
                textfile.write('E{} N{} N{} w={} h={} \n' .format(element_index, first_node_index+i, first_node_index+i+1, w, h))
                element_index +=1
           
            ## Check if connected to plane 
            ###PORT
            if not obj.modifiers["BFH_curve"]["Socket_7"]:
                textfile.write('* PORTS \n')
                textfile.write('.external N{} N{} \n' .format(first_node_index, last_node_index) ) 
            else:
                # Get the evaluated object
                textfile.write(".equiv nin{} N{} \n" .format(obj_idx, first_node_index))
                textfile.write('.external N{} nout{} \n' .format(last_node_index, obj_idx))

            obj.to_mesh_clear()

        ### if object is a mesh with "BFH_var_segment" modifier
        elif obj.type == 'MESH' and "BFH_var_segment" in obj.modifiers:
            #get vertices of selected object
            object_vertices = obj.data.vertices
            mat_world = obj.matrix_world
            vertex_co_global = []

            for vertex in object_vertices:
                vertex_co_global.append((mat_world @ vertex.co) * scale)

            first_node_index = node_index
            last_node_index = node_index + len(vertex_co_global)-1
            ###NODES
            textfile.write('* NODES \n')
            for co in vertex_co_global:
                textfile.write('N{} x={} y={} z={} \n' .format(node_index, co.x, co.y, co.z))
                node_index +=1

            ###ELEMENTS
            textfile.write('* SEGMENTS \n')
            for i in range(len(vertex_co_global)-1):
                w = obj.data.attributes["width"].data[i].value * scale
                h = obj.data.attributes["thickness"].data[i].value * scale
                textfile.write('E{} N{} N{} w={} h={} \n' .format(element_index, first_node_index+i, first_node_index+i+1, w, h))
                element_index +=1
            
            ###PORT
            textfile.write('* PORTS \n')
            textfile.write('.external N{} N{} \n' .format(first_node_index, last_node_index) ) 
    
    ###FREQUENCY RANGE
    textfile.write('.freq' + ' fmin=' + str(int(fmin)) + ' fmax=' + str(int(fmax)) + ' ndec=' + str(ndec) + '\n')
    textfile.write('.end')

class BFH_OP_create_inp(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_create_inp"
    bl_label = "BFH create INP"

    @classmethod
    def poll(cls, context):
        my_properties = context.scene.BFH_properties
        FastHenry_col = my_properties.curve_collection
        return FastHenry_col is not None

        # return context.active_object is not None

    def execute(self, context):
        
        my_properties = context.scene.BFH_properties
        
        self.FastHenry_col = my_properties.curve_collection
        self.plane_col = my_properties.plane_collection

        #check if FastHenry collection exist
        if self.FastHenry_col is None:
            self.report({'WARNING'}, "FastHenry collection not set")
            return {'CANCELLED'}
        
        #check if FastHenry collection has no objects in it
        elif len(self.FastHenry_col.objects) == 0:
            self.report({'WARNING'}, "Empty collection")
            return {'CANCELLED'}

        elif not bpy.data.is_saved:
            self.report({'WARNING'}, "File must be saved first")
            return {'CANCELLED'}
            
        else:
            no_rejected_objects = reject_objects.reject_objects(self, context, my_properties)

            #check again if the FastHenry collection has no objects, it could be that all the objects were rejected
            if len(self.FastHenry_col.objects) == 0:
                self.report({'WARNING'}, "Empty collection, all objects rejected")
                return {'CANCELLED'}
            
            create_inp(self, context)
            self.report({'INFO'}, "INP file created in blend file directory, rejected " + str(no_rejected_objects) + " objects")
            return {'FINISHED'}

