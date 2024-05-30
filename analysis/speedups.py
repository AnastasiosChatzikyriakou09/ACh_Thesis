import os
import pandas as pd
import re

# Use the current directory
directory = os.getcwd()

# Output file paths
final_csv_path = os.path.join(directory, 'speedups.csv')

# Identify the LRU data file
lru_file = [f for f in os.listdir(directory) if f.endswith('0-0.csv')]
if not lru_file:
    raise Exception("No LRU data file found.")
lru_data = pd.read_csv(os.path.join(directory, lru_file[0]))
lru_data.set_index('Benchmark', inplace=True)

# Define benchmarks to ignore
ignored_benchmarks = {"Leela", "Exchange", "Bwaves", "Povray"}

# Dictionary to store data for all IDs
combined_data = {}

# Look for files matching the 'cache-data_X-Y-PARTZ.csv' pattern
pattern = re.compile(r'cache-data_(\d+)-(\d+)-PART(\d+)\.csv')

# Process files for each part
for filename in os.listdir(directory):
    match = pattern.match(filename)
    if match:
        # Extract generation and individual IDs
        gen, ind, part = match.groups()
        file_id = f"{gen}-{ind}"
        filepath = os.path.join(directory, filename)
        data = pd.read_csv(filepath)

        # Temporary dictionary to hold max IPC values across parts
        if file_id not in combined_data:
            combined_data[file_id] = {benchmark: 0 for benchmark in lru_data.index if benchmark not in ignored_benchmarks}

        for index, row in data.iterrows():
            benchmark = row['Benchmark']
            if benchmark in combined_data[file_id]:  # Check if the benchmark is not ignored
                ipc_value = row['IPC']
                combined_data[file_id][benchmark] = max(combined_data[file_id][benchmark], ipc_value)

# Compute the speedup using the highest IPC value from the two parts
final_data = {benchmark: {} for benchmark in lru_data.index if benchmark not in ignored_benchmarks}
for file_id, benchmarks in combined_data.items():
    for benchmark, ipc_value in benchmarks.items():
        ipc_values_lru = lru_data.at[benchmark, 'IPC']
        speedup = ((ipc_value / ipc_values_lru) - 1) * 100 if not pd.isna(ipc_value) and not pd.isna(ipc_values_lru) else float('nan')
        final_data[benchmark][file_id] = speedup

# Transform the combined data into a DataFrame and calculate average speedups
df = pd.DataFrame(final_data)
df['Average Speedup'] = df.mean(axis=1)
df.sort_values(by='Average Speedup', ascending=False, inplace=True)

# Save the combined DataFrame to a new CSV file
df.to_csv(final_csv_path)
print(f"Combined data with speedups saved to {final_csv_path}")

