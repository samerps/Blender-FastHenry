# Samer Aldhaher @samerps 2024

# this operator will import the "BFH_var_segment" modifier and the "BFH_change_segment" node tool if they are not already in the blend file  

import bpy # type: ignore
from pathlib import Path 

class BFH_add_versegment_modifier(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_add_varsegment_modifier"
    bl_label = "Add BFH variable segment modifier"

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        selected_obj = bpy.context.selected_objects[0]
        if selected_obj is None:
            return
        
        if selected_obj.type != "MESH":
            self.report({'WARNING'}, "Object is not a MESH")
            return{'FINISHED'}
        
        #check if object already has BFH_var_segment modifier

        if "BFH_var_segment" in selected_obj.modifiers:
            self.report({'WARNING'}, "Object already has BFH_var_segment modifier")
            return{'FINISHED'}
        
        #check if "BFH_var_segment" modifer already exists. If not, import it and assign to object 
        if "BFH_var_segment" not in bpy.data.node_groups:
            with bpy.data.libraries.load(my_properties.BFH_nodegroup_path) as (data_from, data_to):
                data_to.node_groups.append("BFH_var_segment")
                
        for nodegroup in bpy.data.node_groups:
            if nodegroup.name == "BFH_var_segment":
                selected_obj_mod = selected_obj.modifiers.new("BFH_var_segment", "NODES")
                selected_obj_mod.node_group = nodegroup

        #next check if "BFH_change_segment" node tool group already exists. If not, import it
        if "BFH_change_segment" not in bpy.data.node_groups:
            with bpy.data.libraries.load(my_properties.BFH_nodegroup_path) as (data_from, data_to):
                data_to.node_groups.append("BFH_change_segment")
        
        return {'FINISHED'}