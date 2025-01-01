# Samer Aldhaher @samerps 2024
#operator that visualizes currents in planes

import bpy #type: ignore
from ..functions import read_jmag


class BFH_visualize_currents(bpy.types.Operator):
    """BFH Run All"""
    bl_idname = "view3d.bfh_visualize_currents"
    bl_label = "BFH visualize currents"

    #check if number of planes is no more than one
    @classmethod
    def poll(cls, context):
        my_properties = context.scene.BFH_properties
        FastHenry_plane_col = my_properties.plane_collection
        return len(FastHenry_plane_col.objects) == 1

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        self.FastHenry_col = my_properties.curve_collection
        if self.FastHenry_col is None:
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}
        elif not bpy.data.is_saved:
            self.report({'WARNING'}, "File must be saved first")
            return {'CANCELLED'}
       
        # read Jmag files and create two objects "Current_X/Y_direction" in a new "Visualize Currents" collection,
        Jmag_exist, obj_Current_X_Direction, obj_Current_Y_Direction = read_jmag.read_jmag()
        if Jmag_exist == False:
            self.report({'WARNING'}, "No Jmag file")
            return {'CANCELLED'}
        
        # change object scale based on units set in properties
        units_enum = my_properties.units_enum
        if units_enum == 'mm':
            scale_mul = 1000
        elif units_enum == 'cm':
            scale_mul = 100
        elif units_enum == 'm':
            scale_mul = 1

        obj_Current_X_Direction.scale *= scale_mul/my_properties.mesh_scale
        obj_Current_Y_Direction.scale *= scale_mul/my_properties.mesh_scale
        obj_Current_X_Direction.hide_viewport = True
        obj_Current_Y_Direction.hide_viewport = True
        obj_Current_X_Direction.hide_render = True
        obj_Current_Y_Direction.hide_render = True

        visualize_currents_col = bpy.data.collections['Visualize Currents']
        
        # check if "BFH_visualize_currents" node group exist. If not, append it
        if "BFH_Visualize_Currents" not in bpy.data.node_groups:
            with bpy.data.libraries.load(my_properties.BFH_nodegroup_path) as (data_from, data_to):
                data_to.node_groups.append("BFH_Visualize_Currents")
        
        # check if "Visualize Currents" object exist. If not, create it and assign nodegroup to it 
        for obj in visualize_currents_col.objects:
            if obj.name == "Visualize Currents":
                bpy.data.meshes.remove(obj.data)

        mesh = bpy.data.meshes.new("Visualize Currents")
        obj = bpy.data.objects.new("Visualize Currents", mesh)
        visualize_currents_col.objects.link(obj)

        for nodegroup in bpy.data.node_groups:
            if nodegroup.name == "BFH_Visualize_Currents":
                obj_mod = obj.modifiers.new("BFH_Visualize_Currents", "NODES")
                obj_mod.node_group = nodegroup

        obj.modifiers["BFH_Visualize_Currents"]["Socket_2"] = obj_Current_X_Direction
        obj.modifiers["BFH_Visualize_Currents"]["Socket_3"] = obj_Current_Y_Direction
        obj.modifiers["BFH_Visualize_Currents"]["Socket_4"] = my_properties.plane_collection

        return {'FINISHED'}

        


def menu_func(self, context):
    self.layout.operator(BFH_visualize_currents.bl_idname, text=BFH_visualize_currents.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(BFH_visualize_currents)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(BFH_visualize_currents)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.bfh_run_all()
