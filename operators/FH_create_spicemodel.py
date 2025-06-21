# Samer Aldhaher @samerps 2025
#operator that create a SPICE subckt model from generated csv impedance data

import bpy #type: ignore
import numpy as np
import os
from ..functions import read_Zc, read_csv_data, reject_objects


def write_fasthenry_subckt(res_array, ind_array, subckt_name="BFH_inductor"):
    # Use only the first frequency point
    Rmat = res_array[0]
    Lmat = ind_array[0]
    n = Rmat.shape[0]

    # Build SPICE subcircuit lines
    lines = [f".SUBCKT {subckt_name} " + " ".join([f"P{i+1} N{i+1}" for i in range(n)])]

    for i in range(n):
        lines.append(f"R{i+1} P{i+1} n{i+1} {Rmat[i, i]:.6g}")
        lines.append(f"L{i+1} n{i+1} N{i+1} {Lmat[i, i]:.6g}")

    for i in range(n):
        for j in range(i + 1, n):
            Mij = (Lmat[i, j] + Lmat[j, i]) / 2
            k = Mij / np.sqrt(Lmat[i, i] * Lmat[j, j])
            lines.append(f"K{i+1}{j+1} L{i+1} L{j+1} {k:.6g}")

    lines.append(f".ENDS {subckt_name}")

    # Get Blender file directory
    blend_path = bpy.data.filepath
    folder_path = os.path.dirname(blend_path)

    # Create .subckt filename
    subckt_path = os.path.join(folder_path, f"{subckt_name}.subckt")

    # Write to file
    with open(subckt_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"SPICE subcircuit written to: {subckt_path}")

class BFH_OP_create_spicemodel(bpy.types.Operator):
    """BFH Create Spice Subckt Model"""
    bl_idname = "object.bfh_create_spicemodel"
    bl_label = "BFH Create Spice Subckt Model"

    #check if bpy.data.filepath exists, this indicate if the blend file actually exists in a directory
    @classmethod
    def poll(cls, context):
        my_properties = context.scene.BFH_properties
        FastHenry_col = my_properties.curve_collection
        return bpy.data.filepath != "" and FastHenry_col is not None

    def execute(self, context):

        my_properties = context.scene.BFH_properties

        self.FastHenry_col = my_properties.curve_collection
        if self.FastHenry_col is None:
            self.report({'WARNING'}, "Empty Collection")
            return {'CANCELLED'}
        elif not bpy.data.is_saved:
            self.report({'WARNING'}, "File must be saved first")
            return {'CANCELLED'}
        
        ### get data from csv files 
        self.frequency, self.resistance , self.inductance = read_csv_data.read_csv_data()

        #check if csv data is empty
        if len(self.frequency) == 0:
            self.report({'WARNING'}, "no CSV data")
            return {'CANCELLED'}
        
        #check if csv data matches the number of the objects in FastHenry collection, pick resistance or inductance, this needs to be rewritten once storing object name in CSV data is implemented, it is better then to compare objects names instead of using len
        self.no_of_objs = 0
        if my_properties.sim_selected:
            self.no_of_objs = len(bpy.context.selected_objects)
        else:
            for obj in self.FastHenry_col.objects:
                #count objects in collection excluding plane interconnect curves
                if not obj.modifiers["BFH_curve"]["Socket_11"]:
                    self.no_of_objs +=1

        if len(self.resistance[0][:]) != self.no_of_objs:
            self.report({'WARNING'}, "CSV data does not match number of objects, probably outdated")
            return {'CANCELLED'}

        write_fasthenry_subckt(self.resistance, self.inductance)

        self.report({'INFO'}, "SPICE .subckt file created in blend file directory")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(BFH_OP_create_spicemodel.bl_idname, text=BFH_OP_create_spicemodel.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(BFH_OP_create_spicemodel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(BFH_OP_create_spicemodel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()


