import sys
import csv
import os
import time
import re


cache_names = ["ITLB", "DTLB", "L1D", "L1I", "L2C", "LLC"]


def remove_all_items_from_list(in_list, item):
    out_list = [i for i in in_list if i != item]
    return out_list


def per_set_access_validation(directory_name, filename, data):

    full_file_path = f"{directory_name}\\Error.txt"
    with open(full_file_path, 'a', newline="\n") as error:

        try:
            file = open(filename + ".out", "r")
        except FileNotFoundError:
            print(f"An error occurred while accessing file {filename}.out")
            print(f'Error: file {filename} not found')
            exit(1)

        total = [0, 0, 0, 0, 0, 0]

        while True:
            temp = file.readline().replace("\n", "")

            if re.search("LLC WQ FORWARD: .*", temp):
                break

        pos = -1
        lines = remove_all_items_from_list(file.read().split("\n"), '')

        for line in lines:

            if re.search("ID      Value", line):
                continue

            if re.search("PER SET ACCESS:$", line):
                pos += 1
                continue

            if re.search("^Major fault:", line):
                break

            total[pos] += int(line.split(" ")[-1])

        for idx in range(6):
            if int(data.get(filename)[idx].get('TOTAL').get('ACCESS')) != total[idx]:
                error.write(f"Values are not the same for {cache_names[idx]}\n")
                error.write(f"{total[idx]} opposed to {data.get(filename)[idx].get('TOTAL').get('ACCESS')}\n\n")


def cpu_stats(folder, filename):
    try:
        file = open(f"{folder}\\{filename}" + ".out", "r")
    except FileNotFoundError:
        print(f"An error occurred while accessing file {filename}.out")
        print(f'Error: file {filename} not found')
        exit(1)

    ITLB = {}
    DTLB = {}
    L1D = {}
    L1I = {}
    L2C = {}
    LLC = {}
    start = 0

    while True:
        line = file.readline().replace("\n", "")

        if line == "Region of Interest Statistics":
            file.readline()
            file.readline()
            break

    for line in file.read().split("\n"):
        # Reached the end of Region of Interest
        if line == "DRAM Statistics":
            break

        if not line:
            break
        else:
            if line.split(" ")[0] == "ITLB":
                words = line.split()
                for idx, word in enumerate(words):  # Get the index of the first key (contains ':')
                    if ":" in word:
                        start = idx
                        break

                stat_type = words[1]
                key = " ".join(words[2:start + 1]).replace(':', '')
                value = words[start + 1]

                if stat_type not in ITLB:
                    ITLB[stat_type] = {}

                ITLB[stat_type][key] = value

                if (len(words) - 1) > (start + 1):
                    for j in range(start + 1, len(words) - 1):
                        if ":" in words[j]:  # key value
                            ITLB[stat_type][words[j].replace(':', '')] = words[j + 1]

            elif line.split(" ")[0] == "DTLB":

                words = line.split()
                for idx, word in enumerate(words):  # Get the index of the first key (contains ':')
                    if ":" in word:
                        start = idx
                        break

                stat_type = words[1]
                key = " ".join(words[2:start + 1]).replace(':', '')
                value = words[start + 1]

                if stat_type not in DTLB:
                    DTLB[stat_type] = {}

                DTLB[stat_type][key] = value

                if (len(words) - 1) > (start + 1):
                    for j in range(start + 1, len(words) - 1):
                        if ":" in words[j]:  # key value
                            DTLB[stat_type][words[j].replace(':', '')] = words[j + 1]

            elif line.split(" ")[0] == "L1D":

                words = line.split()
                for idx, word in enumerate(words):  # Get the index of the first key (contains ':')
                    if ":" in word:
                        start = idx
                        break

                stat_type = words[1]
                key = " ".join(words[2:start + 1]).replace(':', '')
                value = words[start + 1]

                if stat_type not in L1D:
                    L1D[stat_type] = {}

                L1D[stat_type][key] = value

                if (len(words) - 1) > (start + 1):
                    for j in range(start + 1, len(words) - 1):
                        if ":" in words[j]:  # key value
                            L1D[stat_type][words[j].replace(':', '')] = words[j + 1]

            elif line.split(" ")[0] == "L1I":

                words = line.split()
                for idx, word in enumerate(words):  # Get the index of the first key (contains ':')
                    if ":" in word:
                        start = idx
                        break

                stat_type = words[1]
                key = " ".join(words[2:start + 1]).replace(':', '')
                value = words[start + 1]

                if stat_type not in L1I:
                    L1I[stat_type] = {}

                L1I[stat_type][key] = value

                if (len(words) - 1) > (start + 1):
                    for j in range(start + 1, len(words) - 1):
                        if ":" in words[j]:  # key value
                            L1I[stat_type][words[j].replace(':', '')] = words[j + 1]

            elif line.split(" ")[0] == "L2C":

                words = line.split()
                for idx, word in enumerate(words):  # Get the index of the first key (contains ':')
                    if ":" in word:
                        start = idx
                        break

                stat_type = words[1]
                key = " ".join(words[2:start + 1]).replace(':', '')
                value = words[start + 1]

                if stat_type not in L2C:
                    L2C[stat_type] = {}

                L2C[stat_type][key] = value

                if (len(words) - 1) > (start + 1):
                    for j in range(start + 1, len(words) - 1):
                        if ":" in words[j]:  # key value
                            L2C[stat_type][words[j].replace(':', '')] = words[j + 1]

            elif line.split(" ")[0] == "LLC":

                words = line.split()
                for idx, word in enumerate(words):  # Get the index of the first key (contains ':')
                    if ":" in word:
                        start = idx
                        break

                stat_type = words[1]
                key = " ".join(words[2:start + 1]).replace(':', '')
                value = words[start + 1]

                if stat_type not in LLC:
                    LLC[stat_type] = {}

                LLC[stat_type][key] = value

                if (len(words) - 1) > (start + 1):
                    for j in range(start + 1, len(words) - 1):
                        if ":" in words[j]:  # key value
                            LLC[stat_type][words[j].replace(':', '')] = words[j + 1]

    print("File " + filename + " has been parsed and dictionary created")

    return {filename: [ITLB, DTLB, L1D, L1I, L2C, LLC]}


def create_csv(directory_name, data, filename, cache_type):

    full_file_path = f"{directory_name}\\{cache_type}.csv"
    # Open the output file

    with open(full_file_path, 'w', newline='') as f:
        # Create a CSV writer
        writer = csv.writer(f)
        # Write the header row
        writer.writerow(['type', 'key', 'value'])
        # Iterate over the data
        for type, subdata in data.items():
            # Iterate over the subdata
            for key, value in subdata.items():
                # Write the data to the CSV file
                writer.writerow([type, key, value])

    print("File " + cache_type + ".csv has been created")


def create_folder(folder, filename):

    # Create the folder name by combining the specified name and the current date and time
    full_folder_name = f"{folder}\\Parsed_{filename}"

    # Check if the folder exists
    if not os.path.exists(full_folder_name):
        # Create the folder if it doesn't exist
        os.makedirs(full_folder_name)
        print(f"A sub folder with the name '{full_folder_name}' has been created")
    else:
        with open(f"{full_folder_name}\\Error.txt", 'a', newline="\n") as error:
            error.write(f"An error occured while creating folder {full_folder_name}\n")
            error.write("Folder already exists\n")

    return full_folder_name


parsed_data = []

folder = "LRU"
file_list = os.listdir(f'./{folder}')

file_list = [filename.split(".")[0] for filename in file_list if filename.endswith(".out")]

for i, filename in enumerate(file_list):
    label = "_Data"
    parsed_data.append(cpu_stats(folder, filename))
    dir_name = create_folder(folder, filename)
    # per_set_access_validation(dir_name, filename, parsed_data[i])
    for j in range(6):
        create_csv(dir_name, parsed_data[i].get(filename)[j], filename, cache_names[j])


