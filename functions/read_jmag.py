import bpy # type: ignore
import os
import csv
from mathutils import Vector # type: ignore

# Path to the CSV file
def read_jmag():

    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)
    file_path = basedir + "//" + "Jmag.csv"

    if os.path.isfile(file_path):
        Jmag_exist = True
    else:
        Jmag_exist = False
        return Jmag_exist, None, None

    # Read the CSV file
    with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

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
            bpy.data.objects.remove(obj, do_unlink=True)

        elif obj.name == "Current_Y_Direction":
            visualize_currents_col.objects.unlink(obj)
            bpy.data.objects.remove(obj, do_unlink=True)

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
    Create a Blender object from CSV rows, assigning attributes to the EDGE domain.
    """
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(f"{object_name}Mesh")
    obj = bpy.data.objects.new(object_name, mesh)
    #bpy.context.collection.objects.link(obj)

    vertices = []
    edges = []
    attributes = []  # To store vector attributes

    def find_or_add_vertex(vertex):
        for i, v in enumerate(vertices):
            if (v - vertex).length < 1e-6:
                return i
        vertices.append(vertex)
        return len(vertices) - 1

    for row in rows:
        if not row or len(row) < 6:
            continue

        try:
            x, y, z = map(float, row[:3])
            attr_x, attr_y, attr_z = map(float, row[3:6])
        except ValueError:
            continue

        start = Vector((x, y, z))
        end = start + (edge_vector * scale_factor)
        start_idx = find_or_add_vertex(start)
        end_idx = find_or_add_vertex(end)
        edges.append((start_idx, end_idx))
        attributes.append(Vector((attr_x, attr_y, attr_z)))

    mesh.from_pydata(vertices, edges, [])
    attr_layer = mesh.attributes.new(name="c_edge", type='FLOAT_VECTOR', domain='EDGE')

    for i, attr_vector in enumerate(attributes):
        attr_layer.data[i].vector = attr_vector

    mesh.update()

    return obj

