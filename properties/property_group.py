import os
import bpy #type: ignore
from bpy.props import FloatVectorProperty, FloatProperty, BoolProperty, IntProperty, StringProperty #type: ignore

import bpy.utils.previews #type: ignore

class BFH_property_group(bpy.types.PropertyGroup):
    inductance_result: FloatProperty(name="inductance result", default = 0) #type: ignore
    resistance_result: IntProperty(name="resistance result", default = 0)   #type: ignore

    fmin: FloatProperty(name="min frequency", min = 0, default = 1e6)         #type: ignore
    fmax: FloatProperty(name="max frequency", min = 0, default = 1e6)         #type: ignore
    ndec: IntProperty(name="ndec", min = 1, default =1)                            #type: ignore

    conductivity: FloatProperty(name="conductivity", min = 0, default =56e6)            #type: ignore

    nhinc: IntProperty(name="nhinc", min = 1, default = 1)                           #type: ignore
    nwinc: IntProperty(name="nwinc", min = 1, default = 1)                           #type: ignore
    rh: IntProperty(name="rh", min = 1, default = 1)                                 #type: ignore
    rw: IntProperty(name="rw", min = 1, default = 1)                                 #type: ignore

    INP_file_name: StringProperty(name=" INP File Name", default = "BFHoutput")   #type: ignore

    show_fastfield_window: BoolProperty(name="show fastfield window", default = False)  #type: ignore

    


