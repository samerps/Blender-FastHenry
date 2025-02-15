# Samer Aldhaher @samerps 2024

import bpy # type: ignore
from pathlib import Path 

class BFH_add_curve_modifier(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_add_curve_modifier"
    bl_label = "Add BFH curve modifier"

    @classmethod
    def poll(cls, context):
        # Ensure we're in OBJECT mode
        return context.mode == 'OBJECT'

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        try:
            selected_obj = bpy.context.selected_objects[0]  # Attempt to get the first selected object
            if selected_obj is None or selected_obj.type != 'CURVE':  # Ensure it's a valid curve object
                self.report({'WARNING'}, "No valid curve object selected")
                return {'FINISHED'}
        except IndexError:
            # Handles the case where no objects are selected
            self.report({'WARNING'}, "No object selected")
            return {'FINISHED'}
        
        #check if object already has BFH_curve modifier

        if "BFH_curve" in selected_obj.modifiers:
            self.report({'WARNING'}, "Object already has BFH_curve modifier")
            return{'FINISHED'}
        
        if selected_obj.type != "CURVE":
            self.report({'WARNING'}, "Object is not a CURVE")
            return{'FINISHED'}

        #check if node group already exists 
        if "BFH_curve" not in bpy.data.node_groups:
            with bpy.data.libraries.load(my_properties.BFH_nodegroup_path) as (data_from, data_to):
                data_to.node_groups.append("BFH_curve")
                
        for nodegroup in bpy.data.node_groups:
            if nodegroup.name == "BFH_curve":
                selected_obj_mod = selected_obj.modifiers.new("BFH_curve", "NODES")
                selected_obj_mod.node_group = nodegroup
                selected_obj.show_wire = True
        
        return {'FINISHED'}
