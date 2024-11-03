# Samer Aldhaher @samerps 2024

import bpy # type: ignore
from bpy.types import Operator, AddonPreferences # type: ignore
from bpy.props import StringProperty, IntProperty, BoolProperty # type: ignore


class BFH_preferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    filepath: StringProperty(name="FastHenry Executable Path", subtype='FILE_PATH' ) # type: ignore

    timout: IntProperty(name="solver time out", default = 0) # type: ignore

    decimals: IntProperty(name="decimals", default =2 ) #type: ignore

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align = True)
        col.prop(self, "filepath")

        box = layout.box()
        
        col = box.column(align = True)
        row = col.row()
        row.prop(self, "timout")
        row.enabled = False

        col = box.column(align = True)
        row = col.row()
        row.prop(self, "decimals")
        row.enabled = False
