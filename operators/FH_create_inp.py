#JUNE 2024
#this class only generates the FastHenry INP file from the selected object 

import bpy #type: ignore
import os 

def create_inp(self, context):
    my_properties = context.window_manager.BFH_properties
    #Fast Henry parameters#
    fmin = my_properties.fmin
    fmax = my_properties.fmax
    ndec = my_properties.ndec
    nhinc = my_properties.nhinc
    nwinc = my_properties.nwinc
    rh = my_properties.rh
    rw = my_properties.rw

    zdefault = 0
    sigma = my_properties.conductivity*1000 #fasthenry sigma units 1/(mm*Ohms)
    units ='mm'

    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)

    #filepath =basedir + '//' + 'FHoutput.txt'

    selected_object = bpy.context.selected_objects[0]
    #bpy.ops.object. convert (target='MESH')

    object_vertices = selected_object.data.vertices
    vertex_coordinates = []

    for vertex in object_vertices:
        vertex_coordinates.append(vertex.co)

    w=0.1 #width
    h=0.1 #height

    textfile = open(my_properties.INP_file_name + ".inp", "w")
    textfile.write('Blender Fast Henry Output' + '\n') #fast henry format first line must contain a comment
    textfile.write('.units ' + units +  '\n')
    textfile.write('.default' + ' z='+str(zdefault) + ' sigma='+str(sigma) + ' nhinc='+str(nhinc) + ' nwinc='+str(nwinc) + ' rh='+str(rh) + ' rw='+str(rw) + '\n')

    for indx, co in enumerate(vertex_coordinates):
        textfile.write('N' + str(indx+1) + ' x=' + str(co.x) + ' y=' + str(co.y) + ' z=' + str(co.z) + '\n' ) 


    for i in range(len(vertex_coordinates)-1):
        textfile.write('E' + str(i+1) + ' N' + str(i+1) + ' N' + str(i+2) + ' w=' + str(w) + ' h=' + str(h) + '\n') 

    textfile.write('.external ' + 'N1 ' + 'N' + str(len(vertex_coordinates)) + '\n')
    textfile.write('.freq' + ' fmin=' + str(fmin) + ' fmax=' + str(fmax) + ' ndec=' + str(ndec) + '\n')
    textfile.write('.end')


class BFH_OP_create_inp(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_create_inp"
    bl_label = "BFH create INP"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        create_inp(self, context)
        return {'FINISHED'}
