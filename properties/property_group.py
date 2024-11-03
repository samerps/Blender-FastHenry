# Samer Aldhaher @samerps 2024

import os
import bpy #type: ignore
from bpy.props import FloatVectorProperty, FloatProperty, FloatVectorProperty, BoolProperty, IntProperty, StringProperty, PointerProperty #type: ignore

import bpy.utils.previews #type: ignore
from pathlib import Path 
import addon_utils # type: ignore

class BFH_property_group(bpy.types.PropertyGroup):
    inductance_result: FloatVectorProperty(name="inductance result", size = 5, default = [0,0,0,0,0]) #type: ignore
    resistance_result: FloatVectorProperty(name="resistance result", size = 5, default = [0,0,0,0,0])   #type: ignore
    frequency_list: FloatVectorProperty(name="frequency list", size = 5, default = [0,0,0,0,0])                      #type: ignore

    fmin: FloatProperty(name="min frequency", min = 0, default = 0.1)         #type: ignore
    fmax: FloatProperty(name="max frequency", min = 0, default = 10)         #type: ignore
    ndec: IntProperty(name="ndec", min = 1, max=4, default =1)                            #type: ignore
    fmultiplier: IntProperty(name="fmultiplier", min=0, max=4, default=0)          # type: ignore


    conductivity: FloatProperty(name="conductivity", min = 0, default =56)            #type: ignore

    nhinc: IntProperty(name="nhinc", min = 1, max = 7, default = 1)                           #type: ignore
    nwinc: IntProperty(name="nwinc", min = 1, max = 7, default = 1)                           #type: ignore
    rh: IntProperty(name="rh", min = 1, max = 7, default = 2)                                 #type: ignore
    rw: IntProperty(name="rw", min = 1, max = 7, default = 2)                                 #type: ignore

    INP_file_name: StringProperty(name=" INP File Name", default = "BFHoutput")   #type: ignore

    #overide_geonodes: BoolProperty(name="Overide Geonodes", default = False)  #type: ignore

    units_enum: bpy.props.EnumProperty(             #type: ignore
    name = " FH Units", 
    description = "Units",
    items = [('mm', "mm", "", "", 0),
            ('cm', "cm", "", "", 1),
            ('m', "m", "", "", 2)
    ],
    default = "cm")

    text_size: FloatProperty(name="text size", min = 0.1, max = 1, default = 0.5)         #type: ignore

    curve_collection: PointerProperty(type=bpy.types.Collection) #type: ignore
    plane_collection: PointerProperty(type=bpy.types.Collection) #type: ignore

    FH_running: BoolProperty(name= "FH running", default = False,  options={'SKIP_SAVE'}) #type: ignore
    FH_finished: BoolProperty(name= "FH finished", default = True, options={'SKIP_SAVE'}) #type: ignore

    # addon file path
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Blender FastHenry":
                p = Path(mod.__file__).resolve()
                BFH_nodegroup_path: StringProperty(name="BFH_nodegroup_path", subtype='FILE_PATH', default=str(p.parent.joinpath("data", "BFH_nodegroups.blend")))  # type: ignore

    


