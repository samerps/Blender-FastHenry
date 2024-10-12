import bpy # type: ignore
from bpy.types import Operator, AddonPreferences # type: ignore
from bpy.props import StringProperty, IntProperty, BoolProperty # type: ignore


class BFH_preferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    filepath: StringProperty(
        name="FastHenry exe File Path",
        subtype='FILE_PATH',
    ) # type: ignore

    timout: IntProperty(
        name="simulation time out",
        default = 0
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        #layout.label(text="preferences")
        layout.prop(self, "filepath")
        layout.prop(self, "timout")
