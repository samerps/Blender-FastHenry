import bpy # type: ignore
import os
import csv
import struct
from mathutils import Vector # type: ignore
import numpy as np

# Path to the CSV file
def read_jmag():

    # Define the structure format (12 doubles)
    # 12 doubles: x, y, z, real_xv, real_yv, real_zv, imag_xv, imag_yv, imag_zv, mag_xv, mag_yv, mag_zv
    struct_format = '<12d'  # Little-endian, 12 doubles (8 bytes each)
    struct_size = struct.calcsize(struct_format)

    rows = []
    
    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)
    file_path = basedir + "//" + "Jcurrents.bin"

    if os.path.isfile(file_path):
        Jmag_exist = True
    else:
        Jmag_exist = False
        return Jmag_exist, None, None

    # Read the CSV file
    with open(file_path, "rb") as f:
        while True:
            data = f.read(struct_size)
            if not data:
                break  # End of file

            # Unpack the binary data
            unpacked_data = struct.unpack(struct_format, data)
            x, y, z = unpacked_data[0:3]
            mag_xv, mag_yv, mag_zv = unpacked_data[9:12]

            # Write to CSV
            rows.append([x, y, z, mag_xv, mag_yv, mag_zv])

    # Filter valid rows
    valid_rows = filter_valid_rows(rows)

    # Determine grid spacing
    dx, dy, dz = determine_grid_size(valid_rows)
    #print(f"Grid spacing: dx = {dx}, dy = {dy}, dz = {dz}")

    # Determine ranges for the two directions dynamically
    n = len([row for row in valid_rows if float(row[3]) != 0 and float(row[4]) == 0])
    
    m = len(valid_rows)
    
    #create "Visualize Currents" collections
    collections = bpy.data.collections
    col_names = []
    for col in collections:
        col_names.append(col.name)
    if 'Visualize Currents' not in col_names:
        bpy.data.collections.new('Visualize Currents')
        bpy.context.scene.collection.children.link(bpy.data.collections['Visualize Currents'])

    visualize_currents_col = bpy.data.collections['Visualize Currents']

    # check if visualize current objects "Current_X_Direction" and "Current_Y_Direction" already exist, if so delete them
    for obj in visualize_currents_col.objects:
        if obj.name == "Current_X_Direction":
            visualize_currents_col.objects.unlink(obj)
            bpy.data.meshes.remove(obj.data)

        elif obj.name == "Current_Y_Direction":
            visualize_currents_col.objects.unlink(obj)
            bpy.data.meshes.remove(obj.data)

    # Create objects for the two edge directions
    obj_Current_X_Direction = create_edge_object_with_attributes("Current_X_Direction", valid_rows[:n], Vector((1.0, 0.0, 0.0)), -dx)
    visualize_currents_col.objects.link(obj_Current_X_Direction)

    obj_Current_Y_Direction = create_edge_object_with_attributes("Current_Y_Direction", valid_rows[n:m], Vector((0.0, 1.0, 0.0)), dy)
    visualize_currents_col.objects.link(obj_Current_Y_Direction)

    return Jmag_exist, obj_Current_X_Direction, obj_Current_Y_Direction


# Ranges for the two directions will be determined dynamically
# after identifying rows to ignore

def determine_grid_size(rows):
    """
    Determines the grid size (spacing along x, y, z) based on the vertex positions in the CSV data.
    Assumes a uniform grid.
    """
    positions = set()
    for row in rows:
        try:
            x, y, z = map(float, row[:3])
            positions.add((x, y, z))
        except ValueError:
            continue  # Skip invalid rows

    # Convert to sorted lists along each axis
    x_values = sorted(set(pos[0] for pos in positions))
    y_values = sorted(set(pos[1] for pos in positions))
    z_values = sorted(set(pos[2] for pos in positions))

    # Calculate grid spacing
    dx = min(abs(x2 - x1) for x1, x2 in zip(x_values[:-1], x_values[1:])) if len(x_values) > 1 else 0.0
    dy = min(abs(y2 - y1) for y1, y2 in zip(y_values[:-1], y_values[1:])) if len(y_values) > 1 else 0.0
    dz = min(abs(z2 - z1) for z1, z2 in zip(z_values[:-1], z_values[1:])) if len(z_values) > 1 else 0.0

    return dx, dy, dz

def filter_valid_rows(rows):
    """
    Filters rows, ignoring those with attributes in columns 4, 5, 6
    containing non-zero values in at least two out of three columns.
    """
    valid_rows = []
    for row in rows:
        try:
            attr_x, attr_y, attr_z = map(float, row[3:6])
            if (attr_x == 0 and attr_y == 0 and attr_z == 0) or (
                (attr_x != 0 and attr_y == 0 and attr_z == 0) or
                (attr_x == 0 and attr_y != 0 and attr_z == 0)):
                valid_rows.append(row)
        except ValueError:
            continue  # Skip invalid rows
    return valid_rows


def create_edge_object_with_attributes(object_name, rows, edge_vector, scale_factor):
    """
    Create a Blender object from CSV rows, assigning attributes to the EDGE domain. From ChatGPT
    """
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(f"{object_name}Mesh")
    obj = bpy.data.objects.new(object_name, mesh)

    vertices = []
    edges = []
    attributes = []  # To store vector attributes
    vertex_dict = {}  # Use dictionary for fast lookup

    def find_or_add_vertex(vertex_tuple):
        """Use a dictionary to store and look up vertices efficiently."""
        if vertex_tuple in vertex_dict:
            return vertex_dict[vertex_tuple]
        index = len(vertices)
        vertices.append(Vector(vertex_tuple))  # Store as Vector
        vertex_dict[vertex_tuple] = index
        return index

    # Convert `rows` to NumPy array for fast processing
    rows_np = np.array(rows, dtype=np.float32)
    valid_rows = rows_np[~np.isnan(rows_np).any(axis=1)]  # Remove NaN rows

    for row in valid_rows:
        x, y, z, attr_x, attr_y, attr_z = row[:6]  # Faster unpacking

        start_tuple = (x, y, z)
        end_tuple = (x + edge_vector.x * scale_factor, 
                     y + edge_vector.y * scale_factor, 
                     z + edge_vector.z * scale_factor)

        start_idx = find_or_add_vertex(start_tuple)
        end_idx = find_or_add_vertex(end_tuple)
        
        edges.append((start_idx, end_idx))
        attributes.append(Vector((attr_x*1e-3, attr_y*1e-3, attr_z*1e-3)))

    # Apply all data at once 
    mesh.from_pydata(vertices, edges, [])
    attr_layer = mesh.attributes.new(name="c_edge", type='FLOAT_VECTOR', domain='EDGE')

    # Vectorized attribute assignment (avoid loop if possible)
    for i, attr_vector in enumerate(attributes):
        attr_layer.data[i].vector = attr_vector

    mesh.update()
    return obj

