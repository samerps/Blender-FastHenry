# Samer Aldhaher @samerps 2024
#class to object to scene and apply BFH_plane modifier to it. The code first checks if the nodgroup "BFH_plane" is already in the current blend file, if not it would append it from the blend file in the addon location

import bpy  # type: ignore

class BFH_add_FHplane(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_add_plane"
    bl_label = "Add BFH plane object"

    @classmethod
    def poll(cls, context):
        # Ensure we're in OBJECT mode
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        my_properties = context.scene.BFH_properties

        bpy.ops.mesh.primitive_cube_add(size=2)

        selected_obj = bpy.context.selected_objects[0]
        selected_obj.scale.z = 0.02
        selected_obj.data.name = "BFH_plane"
        selected_obj.name = "BFH_plane"
        selected_obj.lock_rotation = [True, True, True]

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        #check if node group already exists 
        if "BFH_plane" not in bpy.data.node_groups:
            with bpy.data.libraries.load(my_properties.BFH_nodegroup_path) as (data_from, data_to):
                data_to.node_groups.append("BFH_plane")
        
        for nodegroup in bpy.data.node_groups:
            if nodegroup.name == "BFH_plane":
                selected_obj_mod = selected_obj.modifiers.new("BFH_plane", "NODES")
                selected_obj_mod.node_group = nodegroup

        return {'FINISHED'}