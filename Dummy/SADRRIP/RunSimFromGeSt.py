import re
import subprocess
import sys
import os
from datetime import datetime

GenerationRun = False

if len(sys.argv) == 2:
    generation = sys.argv[1]
    GenerationRun = True
elif len(sys.argv) == 3:
    generation = sys.argv[1]
    myID = sys.argv[2]

error = open("error.out", 'a')

# Get a list of all files in the directory
file_list = os.listdir('./Individuals')

# Check if we are running a generation run or an individual run
if GenerationRun:
    file_list = [filename for filename in file_list if filename.startswith(generation + "_")]
    file_list.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    sbatch = open("Gen_" + str(generation) + ".sh", 'w')
else:
    file_list = [filename for filename in file_list if filename.startswith(generation + "_" + myID + "_")]
    sbatch = open("individual_" + str(generation) + "_" + str(myID) + ".sh", 'w')

current_part = None

for filename in file_list:
    values = {'part1': {}, 'part2': {}}
    with open("./Individuals/" + filename, 'r') as file:
        for line in file:
            line = line.strip()
            if 'PART_1:' in line:
                current_part = 'part1'
                continue  # Skip the label line
            elif 'PART_2:' in line:
                current_part = 'part2'
                continue  # Skip the label line

            if current_part:
                parts = line.split()
                if len(parts) == 2:
                    key, value = parts
                    value = value.strip('%')
                    values[current_part][key] = value  # Store values in corresponding part dictionary
                else:
       	       	   continue
                   #error.write(f"Failed to parse line: {line}\n")


    # Process plist, dirty_plist, and demmask for each part
    for part in ['part1', 'part2']:
        plist_keys = ["W_SPromClean", "W_Insert", "P_SPromClean", "P_Insert", "R_SPromClean", "R_Insert", "L_SPromClean", "L_Insert"]
        dirty_plist_keys = ["W_SPromDirty", "W_Insert", "P_SPromDirty", "P_Insert", "R_SPromDirty", "R_Insert", "L_SPromDirty", "L_Insert"]
        demmask_keys = ["W_DemDirty", "W_DemClean", "P_DemDirty", "P_DemClean", "R_DemDirty", "R_DemClean", "L_DemDirty", "L_DemClean"]

        plist = ""
        dirty_plist = ""
        demmask = ""

        for key in plist_keys:
            plist += values[part].get(key, "0")
        for key in dirty_plist_keys:
            dirty_plist += values[part].get(key, "0")
        for key in demmask_keys:
            demmask += values[part].get(key, "0")

        plist = plist+plist
        dirty_plist = dirty_plist+dirty_plist
        demmask = demmask+demmask

        batch_script = "RRIP_BATCH_RUN"
        switch_script = "RRIP_RUN"
        myID = filename.split("_")[1].split(".")[0]
        batch_command = f"sbatch --export=ALL,script=RRIP_RUN,plist={plist},dplist={dirty_plist},demmask={demmask},id='{generation}-{myID}-{part.upper()}' {batch_script}\n"
        sbatch.write(batch_command)

sbatch.close()

if GenerationRun:
    error.write("Simulations for generation " + str(generation) + " started at " + datetime.now().strftime("%H:%M:%S") + "\n")
    subprocess.call(f"chmod u+x Gen_{generation}.sh", shell=True)
    subprocess.call(f"./Gen_{generation}.sh", shell=True)
else:
    error.write("Simulations for individual " + str(myID) + " from generation " + str(generation) + " started at " + datetime.now().strftime("%H:%M:%S") + "\n")
    subprocess.call(f"chmod u+x individual_{generation}_{myID}.sh", shell=True)
    subprocess.call(f"./individual_{generation}_{myID}.sh", shell=True)

error.close()


