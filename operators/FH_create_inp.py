# Samer Aldhaher @samerps 2024
#this class only generates the FastHenry INP file from the selected object 

import bpy #type: ignore
import os 
from ..functions import reject_objects
import mathutils  #type: ignore 
from mathutils.noise import random_unit_vector  # type: ignore

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
    textfile.write('* Blender FastHenry Output' + '\n') #fasthenry format first line must contain a comment
    textfile.write('.units ' + units +  '\n')
    textfile.write('.default z={} sigma={} nhinc={} nwinc={} rh={} rw={} \n' .format(zdefault, sigma, nhinc, nwinc, rh, rw))
  
    node_index = 1
    element_index = 1

    sim_selected = my_properties.sim_selected

    ##planes

    #create two dictionaries with plane unique_id as key, one to hold plane connect coordinates and another to hold indecies of the curves that connect to the plane
    if self.plane_col:
        plane_points_dict = {}
        curve_indx_dict = {}
        for obj in self.plane_col.objects:
            obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            unique_id = obj.attributes['unique_id'].data[0].value 
            plane_points_dict[unique_id] = []
            curve_indx_dict[unique_id] = [] 
            

    for obj_idx, obj in enumerate(self.FastHenry_col.all_objects):
        if sim_selected:
            if obj in bpy.context.selected_objects:
                pass
            else:
                continue
        
        ### for each curve, if connected to a plane, get the coordinates of the connection and the unique_id of connected plane and add them to the dictionary
        # note that each curve (if connected to a plane) will have two connection points to a plane
        # the geo node attributes (4 in total) are "plane_point1/2" and "plane_unique_id_point1/2"
        # attributes "plane_point1" and "plane_unique_id_point1" are located in the last indices 3 and 4 indices of the BFH_curve modifier
        # attributes "plane_point2" and "plane_unique_id_point2" are located in the last 1 and 2 indices of the BFH_curve modifier        
        
        if (obj.modifiers["BFH_curve"]["Socket_7"]) and (obj.modifiers["BFH_curve"]["Socket_10"] is not None):
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            eval_mesh = eval_obj.to_mesh()
            mat_world = obj.matrix_world
            
            last_node_index = len(eval_mesh.vertices) - 1
            plane_unique_id_point1 =  eval_mesh.attributes["plane_unique_id_point1"].data[last_node_index-2].value
            print(plane_unique_id_point1)
            plane_pos1 = (mat_world @ eval_mesh.attributes["plane_point1"].data[last_node_index-2].vector) * scale

            plane_points_dict[plane_unique_id_point1].append(plane_pos1)
            curve_indx_dict[plane_unique_id_point1].append("nin"+str(obj_idx))

            plane_unique_id_point2 =  eval_mesh.attributes["plane_unique_id_point2"].data[last_node_index].value
            plane_pos2 = (mat_world @ eval_mesh.attributes["plane_point2"].data[last_node_index].vector) * scale
            plane_points_dict[plane_unique_id_point2].append(plane_pos2)
            curve_indx_dict[plane_unique_id_point2].append("nout"+str(obj_idx))


    textfile.write('* Planes \n')
    if self.plane_col:
        unique_id_key_list = list(plane_points_dict.keys())
        for j, obj in enumerate(self.plane_col.objects):
            
            #need a better way to get actual socket names instead of socket numbers, code will break if socket arrangement got changed
            seg1 = obj.modifiers["BFH_plane"]["Socket_8"]-1    
            seg2 = obj.modifiers["BFH_plane"]["Socket_10"]-1
            thickness = obj.modifiers["BFH_plane"]["Socket_9"] * scale

            mat_world = obj.matrix_world
            obj_eval = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            vert0 = obj_eval.attributes['vert0'].data[0].vector * scale
            vert1 = obj_eval.attributes['vert1'].data[0].vector * scale
            vert3 = obj_eval.attributes['vert3'].data[0].vector * scale
  
            textfile.write('GFHPlane{} \n' .format(j))
            textfile.write('+ x1={:.8f} y1={:.8f} z1={:.8f} \n' .format(vert0.x, vert0.y, vert0.z))
            textfile.write('+ x2={:.8f} y2={:.8f} z2={:.8f} \n' .format(vert1.x, vert1.y, vert1.z))
            textfile.write('+ x3={:.8f} y3={:.8f} z3={:.8f} \n' .format(vert3.x, vert3.y, vert3.z))
            textfile.write('+ thick = {:.8f} \n' .format(thickness))
            textfile.write('+ seg1 = {} seg2 = {} \n' .format(seg1, seg2))

            #get plane holes
            bool_max1 = (mat_world @ obj_eval.attributes['bool_max1'].data[0].vector) * scale
            bool_min1 = (mat_world @ obj_eval.attributes['bool_min1'].data[0].vector) * scale

            bool_max2 = (mat_world @ obj_eval.attributes['bool_max2'].data[0].vector) * scale
            bool_min2 = (mat_world @ obj_eval.attributes['bool_min2'].data[0].vector) * scale

            if obj.modifiers["BFH_plane_booleans"]["Socket_10"]:
                textfile.write('+ hole rect ({:.8f},{:.8f},{:.8f},{:.8f},{:.8f},{:.8f}) \n' .format(bool_max1.x, bool_max1.y, bool_max1.z, bool_min1.x, bool_min1.y, bool_min1.z))
            if obj.modifiers["BFH_plane_booleans"]["Socket_12"]:
                textfile.write('+ hole rect ({:.8f},{:.8f},{:.8f},{:.8f},{:.8f},{:.8f}) \n' .format(bool_max2.x, bool_max2.y, bool_max2.z, bool_min2.x, bool_min2.y, bool_min2.z))

            # write plane reference points from dictionaries
            textfile.write('* SAVE PLANE POINTS \n')
            unique_id = unique_id_key_list[j]
            for j, ref in enumerate(curve_indx_dict[unique_id]):
                plane_pos = plane_points_dict[unique_id][j]
                textfile.write('+ {} ({:.8f},{:.8f},{:.8f}) \n'.format(ref, plane_pos.x, plane_pos.y, plane_pos.z))
                
    
    for obj_idx, obj in enumerate(self.FastHenry_col.all_objects):
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
                vertex_co_global.append((mat_world @ vertex.co) * scale + random_unit_vector(size=3)*1e-5)

            first_node_index = node_index
            last_node_index = node_index + len(vertex_co_global)-1
            ###NODES
            textfile.write('* NODES \n')
            for co in vertex_co_global:
                textfile.write('N{} x={:.8f} y={:.8f} z={:.8f} \n' .format(node_index, co.x, co.y, co.z))
                node_index +=1
            
            ###ELEMENTS
            textfile.write('* SEGMENTS \n')

            # this implements minimum twist method to capture the tangent, normal and binormal of the curve, the binormal is used to define segment orientation
            # code from ChatGPT, not sure how the method works.
            # I found if I use the global coordinates, the normal and binormal vectors give wrong orientation, so using local coordinates first and then applying object global tranform when writing to file
            points = []
            for vertex in object_vertices:
                points.append((vertex.co) * scale )# + random_unit_vector(size=3)*1e-5)

            frames = []
            rotation_matrix = obj.rotation_euler.to_matrix().to_3x3()

            for i in range(len(points) - 1):
                p0 = points[i]
                p1 = points[i + 1]
                tangent = (p1 - p0).normalized()

                if i == 0:
                    # Choose an up vector not parallel to the tangent
                    up = mathutils.Vector((0, 0, 1))
                    if abs(tangent.dot(up)) > 0.99:
                        up = mathutils.Vector((0, 1, 0))
                    # Project up onto plane ⟂ tangent
                    projected = up - tangent * up.dot(tangent)
                    normal = projected.normalized()
                else:
                    prev_tangent, prev_normal, _ = frames[-1]
                    axis = prev_tangent.cross(tangent)
                    if axis.length < 1e-6:
                        normal = prev_normal
                    else:
                        angle = prev_tangent.angle(tangent)
                        rot = mathutils.Matrix.Rotation(angle, 3, axis)
                        normal = (rot @ prev_normal).normalized()

                binormal = tangent.cross(normal).normalized()
                frames.append((tangent, normal, binormal))

                rotated_binormal = rotation_matrix @ binormal


                textfile.write('E{} N{} N{} w={:.8f} h={:.8f} wx={:.4F} wy={:.4F} wz={:.4F} \n' .format(element_index, first_node_index+i, first_node_index+i+1, w, h, rotated_binormal.x, rotated_binormal.y, rotated_binormal.z))
                element_index +=1
           
            ## Check if connected to plane 
            ###PORT
            if (obj.modifiers["BFH_curve"]["Socket_7"]) and (obj.modifiers["BFH_curve"]["Socket_10"] is not None):
                textfile.write(".equiv nin{} N{} \n" .format(obj_idx, first_node_index))

                #check if plane interconect
                if (obj.modifiers["BFH_curve"]["Socket_11"]):
                    textfile.write(".equiv N{} nout{} \n" .format(last_node_index, obj_idx))
                else:
                    textfile.write('* PORTS \n')
                    textfile.write('.external N{} nout{} \n' .format(last_node_index, obj_idx))
            else:
                # Get the evaluated object
                textfile.write('* PORTS \n')
                textfile.write('.external N{} N{} \n' .format(first_node_index, last_node_index) ) 

            obj.to_mesh_clear()

        ### if object is a mesh with "BFH_var_segment" modifier
        elif obj.type == 'MESH' and "BFH_var_segment" in obj.modifiers:
            #get vertices of selected object
            object_vertices = obj.data.vertices
            mat_world = obj.matrix_world
            vertex_co_global = []

            for vertex in object_vertices:
                vertex_co_global.append((mat_world @ vertex.co) * scale + random_unit_vector(size=3)*1e-5)

            first_node_index = node_index
            last_node_index = node_index + len(vertex_co_global)-1
            ###NODES
            textfile.write('* NODES \n')
            for co in vertex_co_global:
                textfile.write('N{} x={:.8f} y={:.8f} z={:.8f} \n' .format(node_index, co.x, co.y, co.z))
                node_index +=1

            ###ELEMENTS
            textfile.write('* SEGMENTS \n')
            for i in range(len(vertex_co_global)-1):
                w = obj.data.attributes["width"].data[i].value * scale
                h = obj.data.attributes["thickness"].data[i].value * scale
                textfile.write('E{} N{} N{} w={:.8f} h={:.8f} \n' .format(element_index, first_node_index+i, first_node_index+i+1, w, h))
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

            #move plane interconnect curves to a new collection 
            #first create collection, if not already created
            collections = bpy.data.collections
            # curve_col = collections['curves']
            col_names = []
            for col in collections:
                col_names.append(col.name)
            if 'inter_curves' not in col_names:
                inter_curve_col = bpy.data.collections.new('inter_curves')
                self.FastHenry_col.children.link(inter_curve_col)
            else:
                inter_curve_col = bpy.data.collections['inter_curves']

            for obj in self.FastHenry_col.objects:
                if (obj.modifiers["BFH_curve"]["Socket_11"]):
                    obj.select_set(True)
                    self.FastHenry_col.objects.unlink(obj)
                    inter_curve_col.objects.link(obj)


            self.report({'INFO'}, "INP file created in blend file directory, rejected " + str(no_rejected_objects) + " objects")
            return {'FINISHED'}

