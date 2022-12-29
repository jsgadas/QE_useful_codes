#!/usr/bin/python3
import re

# pwo2in.py
# made by jgadas@me.com
# Utility code for Quantum-Espsresso.
# This code converts pw.x output (vc-relax optimization) to new input file.
# Usage:
# >./pwout2in.py
# > ./pwo2in.py
# > Enter the name of the QE VC-RELAX calculation output file: test.out
# > Enter the name of the QE VC-RELAX calculation input file: test.in
# test.in and test.out must exist.
#

# Ask for the name of the QE VC-RELAX calculation output file
out_filename = input("Enter the name of the QE VC-RELAX calculation output file: ")

# Open the Quantum Espresso output file
try:
    with open(out_filename, 'r') as f:
        output = f.read()
except FileNotFoundError:
    print("Error: file not found")
except PermissionError:
    print("Error: permission denied")    
    
    
# Search for "new unit-cell volume"
end_pattern = r"new unit-cell volume."
end_matches = list(re.finditer(end_pattern, output, re.DOTALL))

# Check if there was at least one match
if not end_matches:
    print("Error: Could not find 'new unit-cell volume' in output file")
    exit()

# Get the last match found
last_match = end_matches[-1]
end_index = last_match.end()
output = output[end_index:]



# Search for "CELL_PARAMETERS" and extract the block until "ATOMIC_POSITIONS"
cell_pattern = r"CELL_PARAMETERS.*?(?=ATOMIC_POSITIONS)"
cell_parameters = re.search(cell_pattern, output, re.DOTALL).group()

# Search for "ATOMIC_POSITIONS" and extract the block to "End final coordinates"
positions_pattern = r"ATOMIC_POSITIONS.*?(?=End final coordinates)"
atomic_positions = re.search(positions_pattern, output, re.DOTALL).group()

# Print the results
# print(cell_parameters)
# print(atomic_positions)


# Ask for the name of the Quantum Espresso calculation input file
in_filename = input("Enter the name of the QE VC-RELAX calculation input file: ")

# Abrir o arquivo de saída do Quantum Espresso
try:
    with open(in_filename, 'r') as f:
        input_content = f.read()
except FileNotFoundError:
    print("Error: file not found")
except PermissionError:
    print("Error: permission denied")  

# Include cell_parameters and atomic_positions results at the end of the input file
input_content += cell_parameters
input_content += atomic_positions

# Create a new input file with the results included
with open('new_input.in', 'w') as f:
    f.write(input_content)


# Search for "ATOMIC_POSITIONS crystal" and extract the block until "K_POINTS automatic"
atomic_positions_pattern = r"ATOMIC_POSITIONS crystal.*?(?=K_POINTS automatic)"
atomic_positions_block = re.search(atomic_positions_pattern, input_content, re.DOTALL).group()

# Remove "ATOMIC_POSITIONS crystal" block from input file
output_content = input_content.replace(atomic_positions_block, " ")


# replaces the found line with the string "ibrav=0"
ibrav_old = r"^\s*ibrav=\s*-?\d+"
output_content = re.sub(ibrav_old, "    ibrav = 0", output_content, flags=re.MULTILINE)

# remove celldm's lines
lines = output_content.split("\n")
lines = [line for line in lines if "celldm" not in line]
output_content = "\n".join(lines)


# Using a regex to extract the value of "alat"
alat_pattern = r"alat=\s*(\d+\.\d+)"
alat_match = re.search(alat_pattern, output_content)

# Check if the regex found a match
if alat_match:
    # Extract the value of "alat" from regex group 1
    alat = alat_match.group(1)
    # print("Alat value::", alat)
else:
    print("Could not find the value of alat.")
    
# Split the string into lines
lines = output_content.split("\n")

# Search for the line with "ibrav"
for i, line in enumerate(lines):
    if "ibrav" in line:
        # Insert the new line after the found line
        lines.insert(i+1, "    celldm(1) = {}".format(alat) + " ,")
        break

# Join the lines again
output_content = "\n".join(lines)    

# Update new file
with open('new_input.in', 'w') as f:
    # write the contents of the string output content to the file
    f.write(output_content)    

    
print("The new input file has been successfully created!")
