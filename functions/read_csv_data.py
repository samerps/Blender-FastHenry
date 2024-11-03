# Samer Aldhaher @samerps 2024

import os
import bpy  #type: ignore
import numpy as np  #type: ignore 
import math

### function to read data from csv files
def read_csv_data():


    # Read the CSV file
    # Initialize lists to hold frequency groups, resistances, and inductances
    frequencies = []
    current_group_resistances = []
    current_group_inductances = []
    all_resistances = []
    all_inductances = []


    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)
    file_path = os.path.join(basedir, "Zc.csv")

    # check if files exist
    if os.path.exists("Zc.csv") == False:
        return frequencies, all_resistances, all_inductances
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Iterate through each line to process the frequency, resistance, and inductance values
    for line in lines:
        # Strip whitespace and split the line by whitespace
        parts = line.strip().split()
        
        # Extract the frequency as float
        freq = float(parts[0])
        
        # Initialize lists to hold resistance and inductance values for the current line
        resistance_values = []
        inductance_values = []

        # Iterate over the parts starting from the second value
        for idx in range(1, len(parts)):
            value = float(parts[idx].replace('j', ''))
            if idx % 2 == 1:
                resistance_values.append(value)  # Real values in even-numbered columns (1-based index)
            else:
                inductance_values.append(value/(2*math.pi*freq))  # Imaginary values in odd-numbered columns (1-based index)

        # Check if the frequency is the same as the last one in the frequencies list
        if len(frequencies) == 0 or freq != frequencies[-1]:
            # If it's a new frequency, save the previous group's resistances and inductances if any
            if current_group_resistances:
                all_resistances.append(np.array(current_group_resistances))
                all_inductances.append(np.array(current_group_inductances))
                current_group_resistances = []
                current_group_inductances = []
            frequencies.append(freq)
        
        # Append the resistance and inductance values to the current group
        current_group_resistances.append(resistance_values)
        current_group_inductances.append(inductance_values)

    # Append the last group of resistances and inductances
    if current_group_resistances:
        all_resistances.append(np.array(current_group_resistances))
        all_inductances.append(np.array(current_group_inductances))

    # Convert the list of frequencies to a numpy array
    frequency_array = np.array(frequencies)

    # Convert all resistance and inductance groups to numpy arrays
    all_resistances = [np.array(group) for group in all_resistances]
    all_inductances = [np.array(group) for group in all_inductances]

    # # Display the frequency array and each resistance/inductance group array
    # print("Frequency Array:", frequency_array)
    # for idx, (resistance_group, inductance_group) in enumerate(zip(all_resistances, all_inductances)):
    #     print(f"Resistance Array for Frequency {frequency_array[idx]}:")
    #     print(resistance_group)
    #     print(f"Inductance Array for Frequency {frequency_array[idx]}:")
    #     print(inductance_group)

    return frequency_array, all_resistances, all_inductances
