import bpy #type: ignore


class BFH_PT_sidebar(bpy.types.Panel):
    """Display test button"""
    bl_label = "Blender Fast Henry"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender FH"

    def draw(self, context):
        my_properties = context.window_manager.BFH_properties
        col = self.layout.column(align=True)
        col.prop(my_properties, 'INP_file_name', text = "INP File Name")
        col.prop(my_properties, 'fmin', text ="fmin")
        col.prop(my_properties, 'fmax', text ="fmax")
        col.prop(my_properties, 'ndec', text ="ndec")
        col.prop(my_properties, 'conductivity', text = "conductivity")
        col.prop(my_properties, 'nhinc', text = "nhinc")
        col.prop(my_properties, 'nwinc', text = "nwinc")
        col.prop(my_properties, 'rh', text = "rh")
        col.prop(my_properties, 'rw', text = "rw")

        col.prop(my_properties, 'show_fastfield_window',  text = "show FFS window")
        
        col.operator("object.bfh_create_inp", text = "Create INP file")
        col.operator("object.bfh_run_fastfield", text ="Run FastHenry")
        col.operator("view3d.bfh_draw_operator", text ="Display Results")
        col.operator("object.bfh_run_all", text ="Run All")
       
