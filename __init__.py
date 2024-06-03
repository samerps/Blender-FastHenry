bl_info = {
    "name": "BlenderFH",
    "author": "Samer Aldhaher",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Blender Fast Henry interface",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy #type: ignore
from .operators import FH_result_draw
from .UI import ui_side_panel

if "bpy" in locals():
	# bring in reload library
    from importlib import reload
	# reload using function
    reload(FH_result_draw)
    reload(ui_side_panel)


def menu_func(self, context):
    pass

# Registration

blender_classes = [FH_result_draw.BFH_OP_result_draw, ui_side_panel.FH_sidebar]



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


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)


if __name__ == "__main__":
    register()
