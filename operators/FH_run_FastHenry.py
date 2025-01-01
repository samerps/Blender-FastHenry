# Samer Aldhaher @samerps 2024

import os
import sys
import subprocess
import bpy #type: ignore
import numpy as np  #type: ignore 
import gpu #type: ignore
import blf #type: ignore
from gpu_extras.batch import batch_for_shader #type: ignore
from .. import preferences

#preparing to include draw function to show status of FastHenry
def draw_callback_px(self, context):

    ### draw text header
    font_id = 0 
    blf.size(font_id, self.text_size)
    blf.shadow(font_id, 3, 0, 0, 0, 0.5)
    xpos = self.text_pos[0]
    ypos = self.text_pos[1]
    line_text = "FastHenry running..."
    blf.color(font_id, 1, 1, 1, 1)
    blf.position(font_id, xpos, ypos, 0)
    text_width, text_height = blf.dimensions(font_id, line_text)
    blf.draw(font_id, line_text + " ")

 

def run_FastHenry(self, context):
    my_properties = context.scene.BFH_properties
    
    self.output_file = os.path.join(self.basedir, "Zc.csv")
    
    try:
        # Run the .exe file asynchronously
        self.process = subprocess.Popen([self.exe_path, self.input_file, "-d", "grids"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # for line in iter(self.process.stdout.readline, ''):
        #     print(f"[Output]: {line.strip()}")

        # for err_line in iter(self.process.stderr.readline, ''):
        #     print(f"[Error]: {err_line.strip()}")

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

    #check if bpy.data.filepath exists, this indicate if the blend file actually exists in a directory
    @classmethod
    def poll(cls, context):
        my_properties = context.scene.BFH_properties
        FastHenry_col = my_properties.curve_collection
        return bpy.data.filepath != "" and FastHenry_col is not None

    basedir = ""
    input_file = ""
    output_file = ""
    process = 0
    exe_path = ""
     
    def invoke(self, context, event):
        
        my_properties = context.scene.BFH_properties
        my_properties.FH_running = False
        my_properties.FH_finished = False

        args = (self, context)

        self.exe_path =  bpy.context.preferences.addons[preferences.__package__].preferences.filepath

        # check exe path defined correctly and file exist
        if 'fasthenry' not in self.exe_path or not os.path.isfile(self.exe_path):
            self.report({'WARNING'},'FastHenry executable path not defined or incorrect file')
            return{'CANCELLED'}

        self.basedir = os.path.dirname(bpy.data.filepath)
        self.input_file = os.path.join(self.basedir, my_properties.INP_file_name + ".inp")

        # Check if the input file exists and has .inp extension
        if not os.path.exists(self.input_file):
            self.report({'WARNING'}, "no FastHenry file, perhaps was not created")
            return{'CANCELLED'}

        os.chdir(self.basedir)

        run_FastHenry(self, context)
       
        my_properties.FH_running = True


        #prepare text and colours for draw function,  based on viewport width and length
        self.text_pos = [context.area.width/2, 10]
        self.text_size = my_properties.text_size * context.area.width/50
        # Add the region OpenGL drawing callback
        # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
        self._handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
      
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        
        context.area.tag_redraw() 
        
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

            # remove draw operator
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')

            #run display result operator
            bpy.ops.view3d.bfh_draw_operator('INVOKE_DEFAULT')

 

            return{'FINISHED'}
        
        else:
           #print("FastHenry is still running...")
           pass
        
        return {'PASS_THROUGH'}

