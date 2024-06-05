#this function read Zc impedance ouput file and processes its contents into three lists: frequency, resistance , inductance 

import re
import math
import bpy #type: ignore
import os
import cmath

def read_Zc():

    # Initialize an empty list to store the vectors and frequency numbers
    vectors_list = []
    frequency_list = []
    inductance_list = []
    resistance_list =[]

    # Read the content of the file and store it as a string
    basedir = os.path.dirname(bpy.data.filepath)
    os.chdir(basedir)
    file_path = basedir + "//" + "Zc.mat"

    if os.path.isfile(file_path):
        read_status = "file exist"
    else:
        read_status = "no Zc file"
        return read_status, frequency_list, inductance_list, resistance_list

    with open(file_path, 'r') as file:
        Zc_file = file.read()

    # Split the text into lines
    lines = Zc_file.strip().split('\n')



    # Process each line separately
    for line in lines:
        # Check if the line contains only numbers (and potentially whitespace)
        if re.match(r"^\s*([-+]?\d*\.\d+e?[-+]?\d*j?\s*)+$", line):
            # Find all real and complex numbers in the line
            numbers = re.findall(r"[-+]?\d*\.\d+e?[-+]?\d*j?", line)
            # Append the list of numbers as a vector to the vectors list
            vectors_list.append(numbers)
        # Check if the line contains the word 'frequency'
        elif 'frequency' in line:
            # Find the first number (scientific or non-scientific notation) immediately after the 'equal' sign
            freq_number = re.search(r"=\s*([-+]?\d*\.?\d+(?:e[+-]?\d+)?)", line)
            if freq_number:
                # Append the found number to the frequency_numbers list
                frequency_list.append(float(freq_number.group(1)))

    # Perform division of complex number by corresponding frequency number and convert to float
    for i, vector in enumerate(vectors_list):
        #separete real part of vector into a resistance list
        resistance_list.append(float(vector[0]))
        for num in vector:
            if 'j' in num:
                # Convert string representations to complex and float types
                complex_num = complex(num)
                freq_num = frequency_list[i]
                # Perform division and append result to results_list as a float, i.e. create inductance list
                result = complex_num / (2*math.pi*freq_num)
                inductance_list.append(float(result.imag))

    return read_status, frequency_list, inductance_list, resistance_list
    # Print results in scientific notation
    #print("Results of division in scientific notation:")
    #for result in results_list:
    #    print(f"{result:.6e}")

    # print("printing")
    # print (frequency_list)
    # #print(vectors_list)
    # print(resistance_list)
    # print(inductance_list)