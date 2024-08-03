import bpy #type: ignore

def reject_objects(self, context, properties):

    collections = bpy.data.collections
    FastHenry_col = properties.curve_collection
    col_names = []
    for col in collections:
        col_names.append(col.name)
    if 'Rejected' not in col_names:
        bpy.data.collections.new('Rejected')
        bpy.context.scene.collection.children.link(bpy.data.collections['Rejected'])
    
    reject_col = bpy.data.collections['Rejected']


    for obj in FastHenry_col.objects:
        #check if obj is CURVE
        if obj.type != 'CURVE':
            obj.select_set(True)
            FastHenry_col.objects.unlink(obj)
            reject_col.objects.link(obj)

        #check if obj has the correct modifer 
        mod_exist = False
        for mod in obj.modifiers:
            if mod.name == 'BFH_curve':
                mod_exist = True
        if not mod_exist:
            FastHenry_col.objects.unlink(obj)
            reject_col.objects.link(obj)


            
        

