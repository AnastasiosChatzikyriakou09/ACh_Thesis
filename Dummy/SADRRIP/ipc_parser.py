import os
import sys

# Default Benchmarks
Benchmarks = ["Blender", "cactuBSSN", "Cam4", "Fotonik3d", "Gcc", "Imagick", "Lbm", "Mcf", "Omnetpp", "Parest", "Perlbench", "Roms", "Wrf", "x264", "Xalancbmk", "Xz"]

# LRU IPC values for each benchmark
lru_ipc_values = {
    "Blender": 0.660544,
    "cactuBSSN": 0.761481,
    "Cam4": 0.724672,
    "Fotonik3d": 0.620779,
    "Gcc": 0.353046,
    "Imagick": 2.19348,
    "Lbm": 0.652418,
    "Mcf": 0.40031,
    "Omnetpp": 0.246394,
    "Parest": 0.934739,
    "Perlbench": 0.448236,
    "Roms": 1.07878,
    "Wrf": 0.822571,
    "x264": 1.37157,
    "Xalancbmk": 0.394671,
    "Xz": 0.893902
}

generation = sys.argv[1]
myID = sys.argv[2]

# Initialize list to hold speedup values for each benchmark
speedup_values = []

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

# Compute the maximum IPC for each benchmark and calculate the speedup
for benchmark in Benchmarks:
    max_ipc = max(ipc_values_part1[benchmark], ipc_values_part2[benchmark])
    speedup = ((max_ipc / lru_ipc_values[benchmark])-1) if lru_ipc_values[benchmark] != 0 else 0
    speedup_values.append(speedup)

# Calculate the average of the speedup values
avg_speedup = sum(speedup_values) / len(speedup_values) if speedup_values else 0
print("{:.3f}".format(avg_speedup))

