#JUNE 2024
#this class only generates the FastHenry INP file from the selected object 

import bpy #type: ignore
import os 

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

    
    #selected_object = bpy.context.selected_objects[0]
    bpy.ops.object.duplicate() #duplicate object
    selected_object = bpy.context.selected_objects[0] #assign duplicated object
    

    if my_properties.overide_geonodes == False:
    #get width and height from geonode group of select object
        w = selected_object.modifiers["BFH_curve"]["Socket_2"] 
        h = selected_object.modifiers["BFH_curve"]["Socket_3"]
    else:
        w=0.1 #width
        h=0.1 #height

    #bpy.ops.object.delete_all_modifiers() #delete all modifiers
    bpy.ops.object.modifier_remove(modifier='BFH_curve')
    bpy.ops.object.convert(target='MESH') #convert to mesh

    #get vertices of selected object
    object_vertices = selected_object.data.vertices
    #object_vertices = bpy.ops.object.data.vertices
    vertex_coordinates = []

    for vertex in object_vertices:
        vertex_coordinates.append(vertex.co)


    textfile = open(my_properties.INP_file_name + ".inp", "w")
    textfile.write('* Blender Fast Henry Output' + '\n') #fast henry format first line must contain a comment
    textfile.write('.units ' + units +  '\n')
    textfile.write('.default' + ' z='+str(zdefault) + ' sigma='+str(sigma) + ' nhinc='+str(nhinc) + ' nwinc='+str(nwinc) + ' rh='+str(rh) + ' rw='+str(rw) + '\n')

    
    ###NODES
    textfile.write('* NODES \n')
    for indx, co in enumerate(vertex_coordinates):
        textfile.write('N' + str(indx+1) + ' x=' + str(co.x) + ' y=' + str(co.y) + ' z=' + str(co.z) + '\n' ) 

    ###ELEMENTS
    textfile.write('* SEGMENTS \n')
    for i in range(len(vertex_coordinates)-1):
        textfile.write('E' + str(i+1) + ' N' + str(i+1) + ' N' + str(i+2) + ' w=' + str(w) + ' h=' + str(h) + '\n') 

    
    ###PORT
    textfile.write('* PORTTS \n')
    textfile.write('.external ' + 'N1 ' + 'N' + str(len(vertex_coordinates)) + '\n')
    
    ###FREQUENCY RANGE
    textfile.write('.freq' + ' fmin=' + str(fmin) + ' fmax=' + str(fmax) + ' ndec=' + str(ndec) + '\n')
    textfile.write('.end')

    bpy.ops.object.delete(use_global=False)


class BFH_OP_create_inp(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_create_inp"
    bl_label = "BFH create INP"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        if bpy.context.selected_objects[0].type == 'CURVE':
            if len(bpy.context.selected_objects) != 0:
                create_inp(self, context)
                return {'FINISHED'}
        

        self.report({'WARNING'}, "Object must be curve")
        return {'CANCELLED'}
