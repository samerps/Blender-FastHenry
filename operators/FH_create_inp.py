#JUNE 2024
#this class only generates the FastHenry INP file from the selected object 

import bpy #type: ignore
import os 
from ..functions import reject_objects

def create_inp(self, context):
    my_properties = context.window_manager.BFH_properties
    #Fast Henry parameters#
    fmin = my_properties.fmin*1e6
    fmax = my_properties.fmax*1e6
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
        if obj.type == 'CURVE':
            obj_mesh = obj.to_mesh()

            if my_properties.overide_geonodes == False:
            #get width and height from geonode group of select object
                w = obj.modifiers["BFH_curve"]["Socket_2"] 
                h = obj.modifiers["BFH_curve"]["Socket_3"]
            else:
                w=0.1 #width
                h=0.1 #height

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


    ##planes
    textfile.write('* Planes \n')
    if self.plane_col:
        for j, obj in enumerate(self.plane_col.objects):
            obj = bpy.context.object.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            vert0 = obj.attributes['vert0'].data[0].vector
            vert1 = obj.attributes['vert1'].data[0].vector
            vert3 = obj.attributes['vert3'].data[0].vector

            print(vert0, vert1, vert3)
            
            textfile.write('GFHPlane{} \n' .format(j))
            textfile.write('+ x1={} y1={} z1={} \n' .format(vert0.x, vert0.y, vert0.z))
            textfile.write('+ x2={} y2={} z2={} \n' .format(vert1.x, vert1.y, vert1.z))
            textfile.write('+ x3={} y3={} z3={} \n' .format(vert3.x, vert3.y, vert3.z))
            textfile.write('+ thick = 0.05 \n')
            textfile.write('+ seg1 = 20 seg2 = 20 \n')
            


            # if obj.type == 'MESH' and len(obj.data.vertices) == 4:
            #     obj_vertices = obj.data.vertices
            #     mat_world = obj.matrix_world
            #     mat_world @ vertex.co
                
            #     textfile.write('GFHPlane{} \n' .format(j))
            #     for i in [0, 1, 3]:
            #         co_global = mat_world @ obj_vertices[i].co
            #         textfile.write('+ x{}={} y{}={} z{}={} \n' .format(i+1 if i!=3 else 3, co_global.x, i+1 if i!=3 else 3, co_global.y, i+1 if i!=3 else 3, co_global.z ))
                
            #     textfile.write('+ thick = 0.05 \n')
            #     textfile.write('+ seg1 = 20 seg2 = 20 \n')


    
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
        my_properties = context.window_manager.BFH_properties
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

        else:
            reject_objects.reject_objects(self, context, my_properties)
            create_inp(self, context)
            return {'FINISHED'}

