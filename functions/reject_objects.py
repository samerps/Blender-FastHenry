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
        if obj.type != 'CURVE':
            obj.select_set(True)
            FastHenry_col.objects.unlink(obj)
            reject_col.objects.link(obj)
            #bpy.context.view_layer.objects.active = obj
            #bpy.ops.object.move_to_collection(collection_index=1)
            #bpy.ops.object.move_to_collection(collection_index=0, is_new = True, new_collection_name='Rejected')

            
        

