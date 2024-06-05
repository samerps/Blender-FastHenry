import os
import bpy #type: ignore
from bpy.props import FloatVectorProperty, FloatProperty, FloatVectorProperty, BoolProperty, IntProperty, StringProperty #type: ignore

import bpy.utils.previews #type: ignore

class BFH_property_group(bpy.types.PropertyGroup):
    inductance_result: FloatVectorProperty(name="inductance result") #type: ignore
    resistance_result: FloatVectorProperty(name="resistance result")   #type: ignore
    frequency_list: FloatVectorProperty(name="frequency list")                      #type: ignore

    fmin: FloatProperty(name="min frequency", min = 0, default = 1e6)         #type: ignore
    fmax: FloatProperty(name="max frequency", min = 0, default = 1e6)         #type: ignore
    ndec: IntProperty(name="ndec", min = 1, default =1)                            #type: ignore

    conductivity: FloatProperty(name="conductivity", min = 0, default =56)            #type: ignore

    nhinc: IntProperty(name="nhinc", min = 1, default = 1)                           #type: ignore
    nwinc: IntProperty(name="nwinc", min = 1, default = 1)                           #type: ignore
    rh: IntProperty(name="rh", min = 1, default = 1)                                 #type: ignore
    rw: IntProperty(name="rw", min = 1, default = 1)                                 #type: ignore

    INP_file_name: StringProperty(name=" INP File Name", default = "BFHoutput")   #type: ignore

    show_fastfield_window: BoolProperty(name="show fastfield window", default = False)  #type: ignore

    


