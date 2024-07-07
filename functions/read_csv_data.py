import os
import bpy
import numpy as np

### function to read data from csv files
def read_csv_data():

    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)

    ###read frequency csv file  
    arrays_list = []
    frequency = []
    resistance = []
    inductance = []

    #check if files exist
    if os.path.exists("frequency.csv") == False:
        return frequency, resistance, inductance
    if os.path.exists("resistance.csv") == False:
        return frequency, resistance, inductance
    if os.path.exists("inductance.csv") == False:
        return frequency, resistance, inductance
    
    with open('frequency.csv', 'r') as csvfile:
        for row in csvfile:
            arrays_list.append([float(x) for x in row.strip().split(',')])
    frequency = np.array(arrays_list)

    ###read inductance csv file
    # Initialize an empty list to store the 2D arrays
    arrays_list = []

    # Placeholder for the current 2D array
    current_array = []
    
    with open('inductance.csv', 'r') as csvfile:
        for row in csvfile:
            if row.startswith('#'):  # Check if the row starts with '#'
                if current_array:  # If there is an existing array, append it to the list
                    arrays_list.append(np.array(current_array))
                    current_array = []  # Reset the current array
            else:
                # Convert strings to floats and split by commas
                current_array.append([float(x) for x in row.strip().split(',')])

    # Append the last array if not already done
    if current_array:
        arrays_list.append(np.array(current_array))

    # Convert list of arrays into a single 3D numpy array
    inductance = np.array(arrays_list)

    ###read resistance csv file 
    # Initialize an empty list to store the 2D arrays
    arrays_list = []

    # Placeholder for the current 2D array
    current_array = []

    with open('resistance.csv', 'r') as csvfile:
        for row in csvfile:
            if row.startswith('#'):  # Check if the row starts with '#'
                if current_array:  # If there is an existing array, append it to the list
                    arrays_list.append(np.array(current_array))
                    current_array = []  # Reset the current array
            else:
                # Convert strings to floats and split by commas
                current_array.append([float(x) for x in row.strip().split(',')])

    # Append the last array if not already done
    if current_array:
        arrays_list.append(np.array(current_array))

    # Convert list of arrays into a single 3D numpy array
    resistance = np.array(arrays_list)

    return frequency, resistance, inductance

