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

    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)

    textfile = open(my_properties.INP_file_name + ".inp", "w")
    textfile.write('* Blender Fast Henry Output' + '\n') #fast henry format first line must contain a comment
    textfile.write('.units ' + units +  '\n')
    textfile.write('.default z={} sigma={} nhinc={} nwinc={} rh={} rw={} \n' .format(zdefault, sigma, nhinc, nwinc, rh, rw))
  
    node_index = 1
    element_index = 1
    
    for obj in self.FastHenry_col.objects:
        ### if object is a curve with FH_Curve modifier
        if obj.type == 'CURVE':
            obj_mesh = obj.to_mesh()

            w = obj.modifiers["BFH_curve"]["Socket_2"] 
            h = obj.modifiers["BFH_curve"]["Socket_3"]

            #get vertices of selected object
            object_vertices = obj_mesh.vertices
            mat_world = obj.matrix_world
            vertex_co_global = []

            for vertex in object_vertices:
                vertex_co_global.append(mat_world @ vertex.co)

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
            
            ###PORT
            textfile.write('* PORTS \n')
            textfile.write('.external N{} N{} \n' .format(first_node_index, last_node_index) ) 

            obj.to_mesh_clear()

        ### if object is a mesh with "FH_var_segment" custom property
        elif "FH_var_segment" in obj:
            #get vertices of selected object
            object_vertices = obj.data.vertices
            mat_world = obj.matrix_world
            vertex_co_global = []

            for vertex in object_vertices:
                vertex_co_global.append(mat_world @ vertex.co)

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
                w = obj.data.attributes["width"].data[i].value
                h = obj.data.attributes["thickness"].data[i].value
                textfile.write('E{} N{} N{} w={} h={} \n' .format(element_index, first_node_index+i, first_node_index+i+1, w, h))
                element_index +=1
            
            ###PORT
            textfile.write('* PORTS \n')
            textfile.write('.external N{} N{} \n' .format(first_node_index, last_node_index) ) 


    ##planes
    textfile.write('* Planes \n')
    if self.plane_col:
        for j, obj in enumerate(self.plane_col.objects):
            
            #need a better way to get actual socket names instead of socket numbers, code will break if socket arrangement got changed
            seg1 = obj.modifiers["BFH_plane"]["Socket_8"]    
            seg2 = obj.modifiers["BFH_plane"]["Socket_10"]
            thickness = obj.modifiers["BFH_plane"]["Socket_9"]

            obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            vert0 = obj.attributes['vert0'].data[0].vector
            vert1 = obj.attributes['vert1'].data[0].vector
            vert3 = obj.attributes['vert3'].data[0].vector
  
            textfile.write('GFHPlane{} \n' .format(j))
            textfile.write('+ x1={} y1={} z1={} \n' .format(vert0.x, vert0.y, vert0.z))
            textfile.write('+ x2={} y2={} z2={} \n' .format(vert1.x, vert1.y, vert1.z))
            textfile.write('+ x3={} y3={} z3={} \n' .format(vert3.x, vert3.y, vert3.z))
            textfile.write('+ thick = {} \n' .format(thickness))
            textfile.write('+ seg1 = {} seg2 = {} \n' .format(seg1, seg2))
            
    
    ###FREQUENCY RANGE
    textfile.write('.freq' + ' fmin=' + str(int(fmin)) + ' fmax=' + str(int(fmax)) + ' ndec=' + str(ndec) + '\n')
    textfile.write('.end')

class BFH_OP_create_inp(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_create_inp"
    bl_label = "BFH create INP"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        #check if FastHenry collection exist
        my_properties = context.scene.BFH_properties
        # FastHenry_col_found = False
        # for col in bpy.data.collections:
        #     if col.name == 'FastHenry':
        #         FastHenry_col_found = True
        #         self.FastHenry_col = col
        
        self.FastHenry_col = my_properties.curve_collection
        self.plane_col = my_properties.plane_collection

        if self.FastHenry_col is None:
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}

        elif not bpy.data.is_saved:
            self.report({'WARNING'}, "File must be saved first")
            return {'CANCELLED'}
            
        else:
            reject_objects.reject_objects(self, context, my_properties)
            create_inp(self, context)
            self.report({'INFO'}, "INP file created in blend file directory")
            return {'FINISHED'}

