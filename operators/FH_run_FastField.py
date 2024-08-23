import os
import sys 
import bpy #type: ignore
import numpy as np

import win32com.client
import win32api


class BFH_OP_run_FastHenry(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_run_fastfield"
    bl_label = "BFH run FastField"


    def execute(self, context):
        print("this is execute")

    def invoke(self, context, event):
        print("this is invoke")
        my_properties = context.scene.BFH_properties
        my_properties.FH_running = False
        my_properties.FH_finished = False

        #check if FastHenry inp file exist
        self.FH_client = win32com.client.Dispatch("FastHenry2.Document")
        print("Fast henry client set")
        basedir = os.path.dirname(bpy.data.filepath)
        os.chdir(basedir)
        if my_properties.show_fastfield_window:
                self.FH_client.ShowWindow()

        self.FH_client.Run(basedir + "\\" + my_properties.INP_file_name + ".inp")
        my_properties.FH_running = True
       
        context.window_manager.modal_handler_add(self)
        return{'RUNNING_MODAL'}

    def modal(self, context, event):
        
        # run_FastField(self, context)
        print("this is modal")
        
        my_properties = context.scene.BFH_properties

        if self.FH_client.IsRunning == True:
            #print("Fast Henry is running")
            my_properties.FH_running = True
        else:
            frequency = np.array(self.FH_client.GetFrequencies)
            resistance = np.array(self.FH_client.GetResistance)
            inductance = np.array(self.FH_client.getInductance)

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
        
            my_properties.FH_finished = True
            print("Fast Henry now finished")
      
        if my_properties.FH_finished:
            print("Fast henry modal finished")
            return{'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("Fast henry modal cancelled")
            return{'CANCELLED'}
        else:
            return {'PASS_THROUGH'}
    