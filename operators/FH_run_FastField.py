import os
import sys 
import bpy #type: ignore

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

    running = FastHenry2.IsRunning
    while FastHenry2.IsRunning:
        win32api.Sleep(100)

    Frequencies = FastHenry2.GetFrequencies
    R = FastHenry2.GetResistance
    L = FastHenry2.getInductance

    print(R)
    print(L)

    #set all values to zero
    for i in range(5):
        my_properties.frequency_list[i] = 0
        my_properties.resistance_result[i] = 0
        my_properties.inductance_result[i] = 0

    #now insert new results
    for i in range(len(Frequencies)):
        my_properties.frequency_list[i] = Frequencies[i]
        my_properties.resistance_result[i] = R[i][0][0]
        my_properties.inductance_result[i] = L[i][0][0]

class BFH_OP_run_FastHenry(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_run_fastfield"
    bl_label = "BFH run FastField"

    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None

    def execute(self, context):
        run_FastField(self, context)
        return {'FINISHED'}