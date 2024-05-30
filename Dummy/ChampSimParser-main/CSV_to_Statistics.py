import csv
import matplotlib.pyplot as plt
import os


def create_folder(filename):
    folder_name = filename.split("\\")[0] + "\\" + filename.split("\\")[1]

    full_folder_name = f"{folder_name}\\Charts"
    # Check if the folder exists
    if not os.path.exists(full_folder_name):
        # Create the folder if it doesn't exist
        os.makedirs(full_folder_name)

    return full_folder_name


def generate_hit_rate_chart(filename):
    # Create an empty dictionary to store the data
    access_values = {}
    hit_rates = {}

    # Open the CSV file
    with open(filename, 'r') as f:
        # Create a CSV reader object
        reader = csv.reader(f)

        # Skip the first row of the CSV file which is the header
        next(reader)

        # Iterate over the rows in the CSV file
        for row in reader:
            # Get the type, key, and value from the row
            type_, key, value = row

            if key in ['ACCESS', 'HIT', 'MISS'] \
                    and type_ in ['TOTAL']:

                # If the type is TOTAL, store the value in the dictionary
                if key == "ACCESS":
                    access_values[type_] = int(value)

                # If the type is not TOTAL, calculate the percentage of the value in the TOTAL type
                else:
                    # Convert the value to a float
                    value = int(value)
                    # If value greater than 0 store it in
                    if value > 0 and key not in hit_rates:
                        hit_rates[key] = 0
                        hit_rates[key] = float(value / access_values[type_] * 100)
                    elif value > 0:
                        hit_rates[key] = float(value / access_values[type_] * 100)

    # Create a sub folder named Charts
    full_folder_name = create_folder(filename)

    keys = list(hit_rates.keys())
    values = list(hit_rates.values())

    # Create a figure and axis object
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create a pie chart
    ax.pie(values, labels=keys, startangle=90)

    # Create a list of formatted percentages
    percentages = ['%.2f' % value + '%' for value in values]

    # Create a legend with the formatted percentages
    legend = ax.legend(title="Percentage", labels=percentages, loc="lower right", bbox_to_anchor=(1, 0, 0.5, 1))

    # Set the font size of the legend
    plt.setp(legend.get_texts(), fontsize='large')

    cache_type = filename.split("\\")[2].split('.')[0]

    # displaying the title
    plt.title(f"{cache_type} Hit Rates")
    plt.savefig(f"{full_folder_name}\\{cache_type}_HitRates.png")

    plt.close()


def generate_percentage_charts(filename):
    # Create an empty dictionary to store the data
    total_values = {}
    percentages = {}

    # Open the CSV file
    with open(filename, 'r') as f:
        # Create a CSV reader object
        reader = csv.reader(f)

        # Skip the first row of the CSV file which is the header
        next(reader)

        # Iterate over the rows in the CSV file
        for row in reader:
            # Get the type, key, and value from the row
            type_, key, value = row

            if key in ['ACCESS', 'HIT', 'MISS', 'MSHR MERGED']  \
                    and type_ in ['TOTAL', 'LOAD', 'RFO', 'PREFETCH', 'WRITEBACK']:

                # If the type is TOTAL, store the value in the dictionary
                if type_ == "TOTAL":
                    total_values[key] = int(value)

                # If the type is not TOTAL, calculate the percentage of the value in the TOTAL type
                else:
                    # Convert the value to a float
                    value = int(value)
                    # If value greater than 0 store it in
                    if value > 0 and key not in percentages:
                        percentages[key] = {}
                        percentages[key][type_] = value / total_values[key] * 100
                    elif value > 0:
                        percentages[key][type_] = value / total_values[key] * 100

    # Create a sub folder named Charts
    full_folder_name = create_folder(filename)

    # Iterate over the key-value pairs in the dictionary
    for key, data in percentages.items():

        # Get the keys and values from the dictionary
        keys = list(data.keys())
        values = list(data.values())

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create a pie chart
        ax.pie(values, labels=keys, startangle=90)

        # Create a list of formatted percentages
        percentages = ['%.2f' % value + '%' for value in values]

        # Create a legend with the formatted percentages
        legend = ax.legend(title="Percentage", labels=percentages, loc="lower right", bbox_to_anchor=(1, 0, 0.5, 1))

        # Set the font size of the legend
        plt.setp(legend.get_texts(), fontsize='large')

        # displaying the title
        plt.title(f"{key} Percentages")

        cache_type = filename.split("\\")[2].split('.')[0]

        plt.savefig(f"{full_folder_name}\\{cache_type}_{key}_Percentages.png")

        plt.close()


def create_pki_csv(filename):

    # Create an empty dictionary to store the data
    access_values = {}
    hit_rates = {}

    # Open the CSV file
    with open(filename, 'r') as f:
        # Create a CSV reader object
        reader = csv.reader(f)

        # Skip the first row of the CSV file which is the header
        next(reader)
        # Iterate over the rows in the CSV file
        for row in reader:
            # Get the type, key, and value from the row
            type_, key, value = row


            if key in ['ACCESS'] and type_ in ['PREFETCH']:
                print(str((int(value)*1000)/500000000))





#MAIN#
folder = "SRRIP"
cache = "LLC"

folder_list = os.listdir(f'.\\{folder}')
folder_list = [folder for folder in folder_list if not folder.endswith(".out")] #Get only folder

for subfolder in folder_list:
    benchmark = subfolder.split("_")[1]
    file_list = os.listdir(f'.\\{folder}\\Parsed_{benchmark}')
    file_list = [filename for filename in file_list if filename.endswith(".csv")]

    for file in file_list:
        if cache != "" and file.split(".")[0] == cache:
            create_pki_csv(f"{folder}\\Parsed_{benchmark}\\{file}")
            # generate_percentage_charts(f"{folder}\\Parsed_{benchmark}\\{file}")
            # generate_hit_rate_chart(f"{folder}\\Parsed_{benchmark}\\{file}")