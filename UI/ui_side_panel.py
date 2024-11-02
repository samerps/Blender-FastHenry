import bpy #type: ignore


class BFH_PT_sidebar(bpy.types.Panel):
    """Display test button"""
    bl_label = "Blender Fast Henry"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender FH"
    bl_ui_units_x = 12

    def draw(self, context):
        my_properties = context.scene.BFH_properties

        layout = self.layout
        layout.use_property_split = True

        ###title and version
        box = layout.box()
        col = box.column(align = True)
        col.label(text="Blender FastHenry")
        col.label(text="V 1.0.0")
        col.operator("wm.url_open", text ="FastHenry Guide", icon='URL').url='https://www.fastfieldsolvers.com/Download/FastHenry_User_Guide.pdf'
        #col.label(text="FastHenry User Guide", icon='URL')

        ####add modifier panel
        box = layout.box()
        col = box.column(align = True)
        col.label(text="Operators")
        col.separator()
        col.operator("object.bfh_add_curve_modifier", text ="Add BFH_Curve modifier")
        col.separator()
        col.operator("object.bfh_add_plane", text = "Add BFH_plane object")
        
        ####collections
        box = layout.box()
        col = box.column(align = True)
        col.label(text="Collections")
        col.separator()
        col.prop(my_properties, 'curve_collection', text ="Curves")
        col.prop(my_properties, 'plane_collection', text ="Planes")

        ####setup
        box = layout.box()
        col = box.column(align = True)
        col.label(text="FastHenry setup")
        col.separator()

        col.prop(my_properties, 'INP_file_name', text = "INP File Name")
        col.prop(my_properties, 'units_enum', text = "units")
        col.prop(my_properties, 'fmin', text ="fmin (MHz)")
        col.prop(my_properties, 'fmultiplier', text ="decades")
        #col.prop(my_properties, 'fmax', text ="fmax (MHz)")
        row = col.row()
        row.prop(my_properties, 'ndec', text ="samples/dec")
        row.enabled = False
        #col.prop(my_properties, 'ndec', text ="samples/dec")
        col.prop(my_properties, 'conductivity', text = "cond. (MS/mm)")
        col.prop(my_properties, 'nhinc', text = "nhinc")
        col.prop(my_properties, 'nwinc', text = "nwinc")
        col.prop(my_properties, 'rh', text = "rh")
        col.prop(my_properties, 'rw', text = "rw")

        # col = box.column()
        # icon = 'CHECKBOX_HLT' if my_properties.overide_geonodes else 'CHECKBOX_DEHLT'
        # col.prop(my_properties, 'overide_geonodes',  text = "overide geonodes", icon = icon)

        ###Simulation
        box = layout.box()
        col = box.column(align = True)
        col.label(text="Simulation")
        col.separator()
       
        col.operator("object.bfh_create_inp", text = "Create INP file")
        col.separator()

        #enable/disable box if FastHenry is running
        if my_properties.FH_running is False:
            box.enabled = True
            text = "Run FastHenry"
        else:
            box.enabled = False
            text = "FastHenry running..."
    
        col.operator("object.bfh_run_fasthenry", text = text)
        col.separator()
        col.operator("view3d.bfh_draw_operator", text ="Display Results")
        col.separator()
        col.operator("object.bfh_run_all", text ="Run All")

        ###settings
        box = layout.box()
        col = box.column(align = True)
        col.label(text="Settings")
        
        col.prop(my_properties, 'text_size', text = "Text Size")


       
