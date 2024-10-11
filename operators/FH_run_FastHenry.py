import os
import subprocess
import bpy #type: ignore
import numpy as np  #type: ignore 
import gpu #type: ignore
import blf #type: ignore
from gpu_extras.batch import batch_for_shader #type: ignore


#preparing to include draw function to show status of FastHenry
def draw_callback_px(self, context):
    pass   
 

def run_FastHenry(self, context):
    my_properties = context.scene.BFH_properties
    #basedir = os.path.dirname(bpy.data.filepath)
    #os.chdir(basedir)
    

    exe_path = "D:\\GitHub\\FastHenry2-Sam\\bin\\fasthenry.exe"
    
    self.output_file = os.path.join(self.basedir, "Zc.csv")
    
    try:
        # Run the .exe file asynchronously
        self.process = subprocess.Popen([exe_path, self.input_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Print a message indicating that the process has started
        print("Executable is running in the background...")

    except FileNotFoundError:
        print("Error: Executable file not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    # my_properties.FH_finished = True



class BFH_OP_run_FastHenry(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.bfh_run_fasthenry"
    bl_label = "Run FastHenry"

    #check if FastHenry inp file exist

    basedir = ""
    input_file = ""
    output_file = ""
    process = 0
     
    def invoke(self, context, event):
        
        my_properties = context.scene.BFH_properties
        my_properties.FH_running = False
        my_properties.FH_finished = False

        self.basedir = os.path.dirname(bpy.data.filepath)
        self.input_file = os.path.join(self.basedir, my_properties.INP_file_name + ".inp")
        os.chdir(self.basedir)

        # Check if the input file exists and has .inp extension
        if not os.path.exists(self.input_file):
            self.report({'WARNING'}, "no FastHenry file, perhaps was not created")
            return{'CANCELLED'}

        run_FastHenry(self, context)
       
        my_properties.FH_running = True
       
        context.window_manager.modal_handler_add(self)             
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        
        my_properties = context.scene.BFH_properties
       
        # Poll the process to check if it is finished
        
        retcode = self.process.poll()  # Check if the process has terminated
        if retcode is not None:  # If return code is not None, the process has finished
            print("FastHenry has finished running.")

            # Capture the output
            stdout, stderr = self.process.communicate()

            # Print the captured output
            print(stdout)

            # Check the return code
            if self.process.returncode == 0:
                print("Executable ran successfully.")
                # Check if the output file exists
                if os.path.exists(self.output_file):
                    print(f"Output file '{self.output_file}' generated successfully.")
                else:
                    print(f"Output file '{self.output_file}' was not generated.")
            else:
                print(f"Executable finished with return code: {self.process.returncode}")
                if stderr:
                    print(f"Error details: {stderr}")
            
            
            my_properties.FH_finished = True
            my_properties.FH_running = False
            print("FastHenry now finished")
            return{'FINISHED'}
        
        else:
            print("FastHenry is still running...")
        
        return {'PASS_THROUGH'}



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
    