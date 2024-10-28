import bpy #type: ignore

def reject_objects(self, context, properties):

    collections = bpy.data.collections
    FH_curve_col = properties.curve_collection
    FH_plane_col = properties.plane_collection


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
        #check if obj is CURVE
        if obj.type != 'CURVE':
            obj.select_set(True)
            FH_curve_col.objects.unlink(obj)
            reject_col.objects.link(obj)

        #check if obj has the correct modifer 
        if not 'BFH_curve' in obj.modifiers:
            FH_curve_col.objects.unlink(obj)
            reject_col.objects.link(obj)
        
    #next, plane, check if the plane collection has been set, otherwise no need to continue
    if not FH_plane_col:
        return
    
    for obj in FH_plane_col.objects:

        #check if obj has the correct modifer 
        if not 'BFH_plane' in obj.modifiers:
            FH_plane_col.objects.unlink(obj)
            reject_col.objects.link(obj)



            
        

