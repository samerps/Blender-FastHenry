import bpy # type: ignore
from pathlib import Path 
import addon_utils # type: ignore
import os

class BFH_add_curve_modifier(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_add_curve_modifier"
    bl_label = "Add BFH curve modifier"

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        selected_obj = bpy.context.selected_objects[0]
        if selected_obj is None:
            return
        
        #check if object already has BFH_curve modifier

        if "BFH_curve" in selected_obj.modifiers:
            self.report({'WARNING'}, "Object already has BFH_curve modifier")
            return{'FINISHED'}
        
        #check if node group already exists 
        if "BFH_curve" not in bpy.data.node_groups:
            with bpy.data.libraries.load(my_properties.BFH_nodegroup_path) as (data_from, data_to):
                data_to.node_groups.append("BFH_curve")
                
        for nodegroup in bpy.data.node_groups:
            if nodegroup.name == "BFH_curve":
                selected_obj_mod = selected_obj.modifiers.new("BFH_curve", "NODES")
                selected_obj_mod.node_group = nodegroup
        
        return {'FINISHED'}
