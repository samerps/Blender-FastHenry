# Samer Aldhaher @samerps 2024

import bpy #type: ignore

def reject_objects(self, context, properties):

    collections = bpy.data.collections
    FH_curve_col = properties.curve_collection
    FH_plane_col = properties.plane_collection

    no_rejected_objects = 0


    #first, check if Rejected collection exist, otherwise create one
    col_names = []
    for col in collections:
        col_names.append(col.name)
    if 'Rejected' not in col_names:
        bpy.data.collections.new('Rejected')
        bpy.context.scene.collection.children.link(bpy.data.collections['Rejected'])
    
    reject_col = bpy.data.collections['Rejected']

    #check curves
    for obj in FH_curve_col.objects:
        #check if obj is not CURVE
        if (obj.type == 'CURVE' and 'BFH_curve' in obj.modifiers):
            pass
        elif  obj.type == 'MESH' and "BFH_var_segment" in obj.modifiers:
            processed_attribute = obj.data.attributes["processed"].data #check if processed attribute is set to False
            for i in range(len(processed_attribute)):
                if processed_attribute[i].value == False: 
                    obj.select_set(True)
                    FH_curve_col.objects.unlink(obj)
                    reject_col.objects.link(obj)
                    no_rejected_objects +=1
                    pass
            
            total_vertices = len(obj.data.vertices) #check if the there are mesh islands
            total_edges = len(obj.data.edges)
            if total_vertices - total_edges > 1:
                obj.select_set(True)
                FH_curve_col.objects.unlink(obj)
                reject_col.objects.link(obj)
                no_rejected_objects +=1
                pass
            
        else:
            obj.select_set(True)
            FH_curve_col.objects.unlink(obj)
            reject_col.objects.link(obj)
            no_rejected_objects +=1
        
    #next, plane, check if the plane collection has been set, otherwise no need to continue
    if not FH_plane_col:
        return no_rejected_objects
    
    for obj in FH_plane_col.objects:

        #check if obj has the correct modifier 
        if not 'BFH_plane' in obj.modifiers:
            FH_plane_col.objects.unlink(obj)
            reject_col.objects.link(obj)
            no_rejected_objects +=1

    return no_rejected_objects



            
        

