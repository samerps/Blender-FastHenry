bl_info = {
    "name": "Blender Fast Henry",
    "author": "Samer Aldhaher",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "N Panel",
    "description": "Blender Fast Henry interface",
    "warning": "",
    "doc_url": ""
}

import bpy #type: ignore
from .operators import FH_result_draw
from .operators import FH_create_inp
from .operators import FH_run_FastField
from .UI import ui_side_panel
from .properties import property_group

def menu_func(self, context):
    pass

# Registration

blender_classes = [FH_result_draw.BFH_OP_result_draw, 
                   FH_create_inp.BFH_OP_create_inp,
                   ui_side_panel.BFH_PT_sidebar,
                   property_group.BFH_property_group,
                   FH_run_FastField.BFH_OP_run_FastHenry]

# This allows you to right click on a button and link to documentation
#def add_object_manual_map():
#    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
#    url_manual_mapping = (
#        ("bpy.ops.mesh.add_object", "scene_layout/object/types.html"),
#    )
#    return url_manual_prefix, url_manual_mapping

def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    bpy.types.WindowManager.BFH_properties = bpy.props.PointerProperty(type=property_group.BFH_property_group)

def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

    del bpy.types.WindowManager.BFH_properties

if __name__ == "__main__":
    register()
