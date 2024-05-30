import os
import sys

# Default Benchmarks
Benchmarks = ["Blender", "Bwaves", "Cam4", "cactuBSSN", "Exchange", "Gcc", "Lbm", "Mcf", "Parest", "Povray", "Wrf", "Xalancbmk", "Fotonik3d", "Imagick", "Leela", "Omnetpp", "Perlbench", "Roms", "x264", "Xz"]

generation = sys.argv[1]
myID = sys.argv[2]

# Initialize list to hold maximum IPC values for each benchmark
max_ipc_values = []

# Get a list of all directories in the results folder
folder_list = os.listdir('/home/achatz13/Dummy/SADRRIP/Results')

# Filter folder list for directories matching the current generation and individual ID for both parts
folder_part1 = [folder for folder in folder_list if folder.endswith(f"{generation}-{myID}-PART1")]
folder_part2 = [folder for folder in folder_list if folder.endswith(f"{generation}-{myID}-PART2")]

# Check for missing data
if not folder_part1 or not folder_part2:
    print("Error: Missing data for one or more parts.")
    sys.exit(1)

# Function to extract IPC values from a file
def get_ipc_values(folder_name):
    ipc_values = {benchmark: 0 for benchmark in Benchmarks}
    for benchmark in Benchmarks:
        full_filename = f"./Results/{folder_name}/{benchmark}.out"
        if os.path.isfile(full_filename):
            with open(full_filename, 'r') as file:
                for line in file:
                    if "Finished CPU" in line and "IPC:" in line:
                        ipc_index = line.find("IPC:") + 5
                        ipc_value = float(line[ipc_index:].split()[0])
                        ipc_values[benchmark] = ipc_value
                        break
    return ipc_values

# Extract IPC values for each part
ipc_values_part1 = get_ipc_values(folder_part1[0])
ipc_values_part2 = get_ipc_values(folder_part2[0])

# Compute the maximum IPC for each benchmark and calculate the average
for benchmark in Benchmarks:
    max_ipc = max(ipc_values_part1[benchmark], ipc_values_part2[benchmark])
    max_ipc_values.append(max_ipc)

# Calculate the average of the maximum IPC values
avg_max_ipc = sum(max_ipc_values) / len(max_ipc_values) if max_ipc_values else 0
print("{:.3f}".format(avg_max_ipc))
