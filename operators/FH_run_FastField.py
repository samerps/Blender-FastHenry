import os
import sys 
import bpy #type: ignore
import numpy as np

import win32com.client
import win32api

def run_FastField(self, context):
    my_properties = context.window_manager.BFH_properties
    FastHenry2 = win32com.client.Dispatch("FastHenry2.Document")
    #pathStr = os.getcwd()
    #pathStr = "C:\\Users\\samer\\Downloads\\FastHenry"
    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)
    
    if my_properties.show_fastfield_window:
        FastHenry2.ShowWindow()

    FastHenry2.Run(basedir + "\\" + my_properties.INP_file_name + ".inp")

    #running = FastHenry2.IsRunning
    while FastHenry2.IsRunning:
        win32api.Sleep(100)

    frequency = np.array(FastHenry2.GetFrequencies)
    resistance = np.array(FastHenry2.GetResistance)
    inductance = np.array(FastHenry2.getInductance)

    #write results in a text file, this is so that when opening a Blender FastHenry scene we can display results (if the simulation was done previously) without having to rerun the simultion

    if os.path.exists("frequency.csv"):
        os.remove("frequency.csv")

    if os.path.exists("resistance.csv"):
        os.remove("resistance.csv")

    if os.path.exists("inductance.csv"):
        os.remove("inductance.csv")

    with open("frequency.csv", "ab") as f:
        np.savetxt(f, frequency, delimiter=",")

    with open("resistance.csv", "ab") as f:
        for i in range(len(frequency)):
            np.savetxt(f, resistance[i], delimiter=",",  header=str(frequency[i]))

    with open("inductance.csv", "ab") as f:
        for i in range(len(frequency)):
            np.savetxt(f, inductance[i], delimiter=",",  header=str(frequency[i]))


class BFH_OP_run_FastHenry(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_run_fastfield"
    bl_label = "BFH run FastField"

    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None

    def execute(self, context):
        #check if FastHenry collection exist
        FastHenry_col_found = False
        for col in bpy.data.collections:
            if col.name == 'FastHenry':
                FastHenry_col_found = True
                self.FastHenry_col = col
        
        if FastHenry_col_found == False:
            print("No FastHenry Collection")
            self.report({'WARNING'}, "No FastHenry Collection")
            return {'CANCELLED'}
        else:
            run_FastField(self, context)
        return {'FINISHED'}