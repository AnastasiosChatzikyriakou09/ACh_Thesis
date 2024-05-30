import re
import os

def parse_output(output):
    # Regular expression pattern to match the cache statistics
    cache_pattern = re.compile(r'(\b\w+\b)\s+ACCESS:\s+(\d+)\s+HIT:\s+(\d+)\s+MISS:\s+(\d+)')
    matches = cache_pattern.findall(output)
    return matches

def get_cache_types(output):
    # Regular expression pattern to match cache type lines
    cache_type_pattern = re.compile(r'(\b\w+\b)\s+TOTAL\s+ACCESS:')
    cache_types = [match.group(1) for match in cache_type_pattern.finditer(output)]
    return cache_types

def write_cache_stats_to_file(cache_stats, ipc_value, llc_mshr_values, output_file):
    with open(output_file, 'a') as f:
        line_values = [ipc_value]  # IPC is the first item
        for cache_stat in cache_stats:
            line_values.extend(cache_stat[1:])  # Append cache stats, skipping cache type name

        # Append LLC MSHR values at the end of the line
        line_values.extend(llc_mshr_values)
        f.write(" ".join(map(str, line_values)) + "\n")
        return True

def process_subdirectory(subdir):
    results_dir = os.path.join("Results", subdir)
    pattern = r'-([1-9][0-9]*)-([1-9][0-9]*)-(PART\d+)$'
    match = re.search(pattern, subdir)
    if not match:
        print(f"Skipping directory without ID info: {subdir}")
        return

    gen_id, ind_id, policy = match.groups()
    output_file = os.path.join(results_dir, f"cache-data_{gen_id}-{ind_id}-{policy}.txt")

    ignored_files = {'Leela.out', 'Exchange.out', 'Bwaves.out', 'Povray.out'}
    benchmark_order = ['Blender.out', 'Bwaves.out', 'cactuBSSN.out', 'Cam4.out', 'Exchange.out', 'Fotonik3d.out', 'Gcc.out', 'Imagick.out', 'Lbm.out', 'Leela.out', 'Mcf.out', 'Omnetpp.out', 'Parest.out', 'Perlbench.out', 'Povray.out', 'Roms.out', 'Wrf.out', 'x264.out', 'Xalancbmk.out', 'Xz.out']

    # Get all filenames in the directory and filter out non-.out files and ignored files
    filenames = [filename for filename in os.listdir(results_dir) if filename.endswith('.out') and filename not in ignored_files]
    # Sort filenames according to the benchmark order
    sorted_filenames = sorted(filenames, key=lambda x: benchmark_order.index(x) if x in benchmark_order else -1)

    for filename in sorted_filenames:
        full_filename = os.path.join(results_dir, filename)
        ipc_value = 0
        llc_mshr_values = []
        with open(full_filename, 'r') as f:
            output = f.read()
            # Search for IPC and LLC MSHR data in the output
            for line in output.splitlines():
                if "Finished CPU" in line and "cumulative IPC:" in line:
                    ipc_value = float(line.split("cumulative IPC:")[1].split()[0])

            # Extract LLC MSHR values
            mshr_pattern = re.compile(r'LLC (TOTAL|LOAD|RFO|PREFETCH|WRITEBACK) MSHR MERGED:\s+(\d+)')
            matches = mshr_pattern.findall(output)
            for mshr_type, value in matches:
                llc_mshr_values.append(value)  # Collect all MSHR data

        cache_stats = parse_output(output)
        write_cache_stats_to_file(cache_stats, ipc_value, llc_mshr_values, output_file)

if __name__ == "__main__":
    for subdir in os.listdir("Results"):
        if os.path.isdir(os.path.join("Results", subdir)):
            process_subdirectory(subdir)

