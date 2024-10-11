import os
import subprocess

import sys 
import bpy #type: ignore
import numpy as np  #type: ignore 
import gpu #type: ignore
import blf #type: ignore
from gpu_extras.batch import batch_for_shader #type: ignore


# import win32com.client
# import win32api

#preparing to include draw function to show status of FastHenry
def draw_callback_px(self, context):
    pass   

 

def run_FastHenry(self, context):
    my_properties = context.scene.BFH_properties
    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)
    exe_path = "D:\\GitHub\\FastHenry2-Sam\\bin\\fasthenry.exe"
    input_file = os.path.join(basedir, "BFHoutput.inp")
    output_file = os.path.join(basedir, "Zc.csv")

    try:
        # Run the .exe file with the input argument and capture the output
        result = subprocess.run([exe_path, input_file], check=True, text=True, capture_output=True)
        
        # Print the captured output
        print(result.stdout)
        
        # Check the return code
        if result.returncode == 0:
            print("Executable ran successfully.")
            # Check if the output file exists
            if os.path.exists(output_file):
                print(f"Output file '{output_file}' generated successfully.")
            else:
                print(f"Output file '{output_file}' was not generated.")
        else:
            print(f"Executable finished with return code: {result.returncode}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.output}")
    except FileNotFoundError:
        print("Error: Executable file not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")   
    
    my_properties.FH_finished = True



class BFH_OP_run_FastHenry(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_run_fasthenry"
    bl_label = "Run FastHenry"


    def execute(self, context):
        print("this is execute")
        my_properties = context.scene.BFH_properties
        my_properties.FH_running = False
        my_properties.FH_finished = False

        #check if FastHenry inp file exist
        
        basedir = os.path.dirname(bpy.data.filepath)
        os.chdir(basedir)

        run_FastHenry(self, context)


        my_properties.FH_running = True
       
        # context.window_manager.modal_handler_add(self)
        print("finished")
        return{'FINISHED'}

    # def invoke(self, context, event):
    #     #print("this is invoke")
    #     my_properties = context.scene.BFH_properties
    #     my_properties.FH_running = False
    #     my_properties.FH_finished = False

    #     #check if FastHenry inp file exist
        
    #     basedir = os.path.dirname(bpy.data.filepath)
    #     os.chdir(basedir)

    #     run_FastHenry(self, context)


    #     my_properties.FH_running = True
       
    #     context.window_manager.modal_handler_add(self)
    #     # return{'RUNNING_MODAL'}
    #     return{'FINISHED'}


    # def modal(self, context, event):
        
        # run_FastField(self, context)
        #print("this is modal")
        
        my_properties = context.scene.BFH_properties

        # if self.FH_client.IsRunning == True:
        #     #print("Fast Henry is running")
        #     my_properties.FH_running = True
        # else:
        #     frequency = np.array(self.FH_client.GetFrequencies)
        #     resistance = np.array(self.FH_client.GetResistance)
        #     inductance = np.array(self.FH_client.getInductance)

        #     if os.path.exists("frequency.csv"):
        #         os.remove("frequency.csv")

        #     if os.path.exists("resistance.csv"):
        #         os.remove("resistance.csv")

        #     if os.path.exists("inductance.csv"):
        #         os.remove("inductance.csv")

        #     with open("frequency.csv", "ab") as f:
        #         np.savetxt(f, frequency, delimiter=",")

        #     with open("resistance.csv", "ab") as f:
        #         for i in range(len(frequency)):
        #             np.savetxt(f, resistance[i], delimiter=",",  header=str(frequency[i]))

        #     with open("inductance.csv", "ab") as f:
        #         for i in range(len(frequency)):
        #             np.savetxt(f, inductance[i], delimiter=",",  header=str(frequency[i]))
        
        #     my_properties.FH_finished = True
        #     my_properties.FH_running = False
        #     print("Fast Henry now finished")

        
        # if my_properties.FH_finished:
        #     my_properties.FH_finished = False
        #     my_properties.FH_running = False
            
        #     #run Display Results operator 
        #     bpy.ops.view3d.bfh_draw_operator('INVOKE_DEFAULT')

        #     print("Fast henry modal finished")
        #     return{'FINISHED'}
        # elif event.type in {'ESC'}:
        #     my_properties.FH_finished = False
        #     my_properties.FH_running = False
        #     print("Fast henry modal cancelled")
        #     return{'CANCELLED'}
        # else:
        #     return {'PASS_THROUGH'}
    