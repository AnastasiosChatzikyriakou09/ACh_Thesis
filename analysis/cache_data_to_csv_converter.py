import os

# Updated list of benchmark names, excluding the ones to ignore
benchmark_names = ["Blender", "cactuBSSN", "Cam4", "Fotonik3d", "Gcc", 
                   "Imagick", "Lbm", "Mcf", "Omnetpp", "Parest", 
                   "Perlbench", "Roms", "Wrf", "x264", "Xalancbmk", "Xz"]


# Define cache types and their corresponding indices in the cache-data.txt file
cache_types = ['ITLB', 'DTLB', 'L1D', 'L1I', 'L2C', 'LLC']
access_types = ['Total', 'Load', 'RFO', 'Prefetch', 'Writeback']
metrics = ['Accesses', 'Hits', 'Misses', 'MSHR']

# Function to extract cache metrics for specific benchmark from a file
def extract_cache_metrics(filepath):
    cache_metrics = {}
    with open(filepath, "r") as file:
        for i, line in enumerate(file):
            values = line.split()
            ipc = float(values[0])
            cache_metrics[i] = {"IPC": ipc, "Values": values[1:]}
    return cache_metrics

# Function to generate headers
def generate_headers():
    headers = ["Benchmark", "IPC"]
    # Add headers for all cache types and access types except MSHR
    for cache_type in cache_types:
        for access_type in access_types:
            for metric in metrics:
                if metric != 'MSHR':
                    headers.append(f"{cache_type} {access_type} {metric}")
    # Add headers for LLC MSHR
    for access_type in access_types:
        headers.append(f"LLC {access_type} MSHR")
    return headers

# Function to transform cache metrics to CSV format
def transform_to_csv(cache_metrics, filename):
    # Generate CSV filename from the text file name
    csv_filename = os.path.splitext(filename)[0] + ".csv"

    # Write CSV file
    with open(csv_filename, "w") as csv_file:
        # Write header row
        header_row = generate_headers()
        csv_file.write(",".join(header_row) + "\n")
        
        # Write data rows
        for i, metrics in cache_metrics.items():
            if benchmark_names[i] in benchmark_names:  # Ensure benchmark is not ignored
                row = [benchmark_names[i], metrics["IPC"]] + metrics["Values"]
                csv_file.write(",".join(map(str, row)) + "\n")

# Main function to process cache data
def process_cache_data(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt") and all(not filename.startswith(bench + ".") for bench in ["Leela", "Exchange", "Bwaves", "Povray"]):
            filepath = os.path.join(directory, filename)
            cache_metrics = extract_cache_metrics(filepath)
            transform_to_csv(cache_metrics, filename)

# Entry point of the script
if __name__ == "__main__":
    process_cache_data(".")
