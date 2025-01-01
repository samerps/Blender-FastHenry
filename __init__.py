# Samer Aldhaher @samerps 2024

import bpy #type: ignore
from .operators import FH_result_draw
from .operators import FH_create_inp
from .operators import FH_run_FastHenry
from .operators import FH_run_all
from .operators import FH_add_BFH_curve_modifier
from .operators import FH_add_BFH_plane_object
from .operators import FH_add_BFH_varsegment_modifier
from .operators import FH_visualize_currents
from .UI import ui_side_panel
from .properties import property_group
from . import preferences

def menu_func(self, context):
    pass

# Registration

blender_classes = [FH_result_draw.BFH_OP_result_draw, 
                   FH_create_inp.BFH_OP_create_inp,
                   ui_side_panel.BFH_PT_sidebar,
                   property_group.BFH_property_group,
                   FH_run_FastHenry.BFH_OP_run_FastHenry,
                   FH_run_all.BFH_OP_result_draw,
                   preferences.BFH_preferences,
                   FH_add_BFH_curve_modifier.BFH_add_curve_modifier,
                   FH_add_BFH_plane_object.BFH_add_FHplane,
                   FH_add_BFH_varsegment_modifier.BFH_add_versegment_modifier,
                   FH_visualize_currents.BFH_visualize_currents]

def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    #bpy.types.WindowManager.BFH_properties = bpy.props.PointerProperty(type=property_group.BFH_property_group) #note using WndowManager will not save values in blend file
    bpy.types.Scene.BFH_properties = bpy.props.PointerProperty(type=property_group.BFH_property_group)

def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

    #del bpy.types.WindowManager.BFH_properties
    del bpy.types.Scene.BFH_properties

if __name__ == "__main__":
    register()
