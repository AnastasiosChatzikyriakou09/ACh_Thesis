import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import glob
import seaborn as sns
import numpy as np
import re  
import subprocess

def pki_transform(value):
    return (value * 1000) / 500000000

def extract_ipc(csv_file):
    data = pd.read_csv(csv_file)
    ipc_values = data.set_index('Benchmark')['IPC'].to_dict()
    return ipc_values


def plot_cache_data(csv_files, benchmarks, header):
    plt.figure(figsize=(12, 6))
    bar_width = 0.3
    num_csv_files = len(csv_files)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'][:num_csv_files]

    # Map each file to a specific color
    color_map = {csv_file: colors[i] for i, csv_file in enumerate(csv_files)}

    # Load best policies information
    directory = os.getcwd()
    best_policies_path = os.path.join(directory, 'bestPolicies.csv')
    best_policies_df = pd.read_csv(best_policies_path)

    # Extract IPC values for LRU only once for base comparison
    ipc_values_lru = extract_ipc("cache-data_0-0.csv")

    # If the user requested to plot 'all' benchmarks, gather all unique benchmarks
    if 'all' in benchmarks:
        all_benchmarks = set()
        for csv_file in csv_files:
            if csv_file == "0-0":
                data = pd.read_csv(f'cache-data_0-0.csv')  # Directly read the data for 0-0 which is single-policy baseline
            else:
                gen, ind = csv_file.split('-')
                data = pd.read_csv(f'cache-data_{gen}-{ind}-PART1.csv')  # Read PART1 just to get benchmark names
            all_benchmarks.update(data['Benchmark'])  # Add benchmarks to the set, ensuring uniqueness
        benchmarks = list(all_benchmarks)  # Convert the set to a list for further processing

    # Determine the order of benchmarks
    num_benchmarks = len(benchmarks)
    benchmark_order = {}
    for csv_file in csv_files:
        if csv_file == "0-0":
            data = pd.read_csv(f'cache-data_0-0.csv')  # Directly read the data for 0-0 which is single-policy baseline
        else:
            gen, ind = csv_file.split('-')
            data = pd.read_csv(f'cache-data_{gen}-{ind}-PART1.csv')
        for i, benchmark in enumerate(data['Benchmark']):
            if benchmark not in benchmark_order:
                benchmark_order[benchmark] = len(benchmark_order)

    sorted_benchmarks = sorted(benchmarks, key=lambda x: benchmark_order.get(x, float('inf')))

    ipc_speedups_all = {csv_file: [] for csv_file in csv_files if csv_file != "0-0"}

    ax = plt.gca()
    ax2 = ax.twinx()

    for i, benchmark in enumerate(sorted_benchmarks):
        for j, csv_file in enumerate(csv_files):
            color = color_map[csv_file]
            gen, ind = csv_file.split('-')
            if csv_file == "0-0":
                # Directly read the data for 0-0 which is single-policy baseline
                data = pd.read_csv(f'cache-data_0-0.csv')
            else:
                # Determine which policy to use from bestPolicies.csv
                best_policy_row = best_policies_df[best_policies_df['ID'] == csv_file]
                if best_policy_row.empty:
                    continue
                best_policy = best_policy_row[benchmark].values[0]
                # Construct the filename with the best policy
                policy_file = f'cache-data_{gen}-{ind}-PART{best_policy}.csv'
                data = pd.read_csv(os.path.join(directory, policy_file))

            benchmark_data = data[data['Benchmark'] == benchmark]
            if benchmark_data.empty:
                continue
            x = i * (num_csv_files + 1) * bar_width + j * bar_width
            transformed_data = benchmark_data[header].apply(pki_transform)
            ax.bar(x, transformed_data, width=bar_width, color=color, label=f'individual {csv_file}' if i == 0 else "", zorder=3)
            
            # Only calculate and plot IPC speedup for non "0-0" CSVs
            if csv_file != "0-0":
                ipc_values_current = extract_ipc(os.path.join(directory, policy_file))
                ipc_speedup = ((ipc_values_current[benchmark] / ipc_values_lru[benchmark]) - 1) * 100
                ipc_speedups_all[csv_file].append((x, ipc_speedup))

    # Plot the IPC speedup points and lines for non "0-0" CSVs
    for j, (csv_file, speedup_data) in enumerate(ipc_speedups_all.items()):
        if speedup_data:  # Ensure there is data to plot
            color = color_map[csv_file]
            x_vals, y_vals = zip(*speedup_data)
            ax2.plot(x_vals, y_vals, label=f'IPC Speedup individual {csv_file}', zorder=4, linewidth=2, color=color)
            ax2.scatter(x_vals, y_vals, color='black', zorder=5)

    ax.set_ylabel('PKI')
    ax2.set_ylabel('IPC Speedup (%)', color='red')
    ax.set_xlabel('Benchmark')
    ax.set_title(header)
    ax.set_xticks(np.arange(num_benchmarks) * (num_csv_files + 1) * bar_width + (num_csv_files - 1) * bar_width / 2)
    ax.set_xticklabels(sorted_benchmarks, rotation=45, ha='right')
    ax.grid(axis='y', zorder=0)

    # Set y-axis for IPC speedup to red
    ax2.tick_params(axis='y', colors='red')

    # Handle legends
    handles, labels = [], []
    for a in [ax, ax2]:
        h, l = a.get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()

    if not os.path.exists("cache-plots"):
        os.makedirs("cache-plots")

    # Construct the filename using the ids and benchmarks
    ids_str = "_".join(csv_files)
    benchmarks_str = "_".join(benchmarks)
    filename = f'cache-plots/{header}_{ids_str}_{benchmarks_str}.png'
    plt.savefig(filename)
    plt.close()



def plot_all_headers_for_benchmark(csv_files, benchmark):
    data = {}
    headers = []
    for csv_file in csv_files:
        csv_data = pd.read_csv(f'cache-data_{csv_file}.csv')
        benchmark_data = csv_data[csv_data['Benchmark'] == benchmark]
        if not benchmark_data.empty:
            csv_headers = [header for header in csv_data.columns if 'LLC' in header and header != 'IPC' and header != 'Benchmark']
            headers.extend(header for header in csv_headers if header not in headers)
            data[csv_file] = benchmark_data

    plt.figure(figsize=(12, 6))
    num_csv_files = len(csv_files)
    num_headers = len(headers)
    
    # Set a reasonable bar width
    bar_width = 0.35
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'][:num_csv_files]  # List of colors with good contrast

    # Calculate the total width for each group of bars including spacing
    total_width = num_headers * (num_csv_files * bar_width) + (num_headers + 1) * 0.2  # Adjust spacing between groups
    # Calculate the spacing between each group of headers
    spacing = total_width / (num_headers + 1)  # Adjust spacing between groups
    
    # Adjust starting position if only one CSV file is given
    if num_csv_files == 1:
        start_position = (total_width - bar_width) / 2
    else:
        start_position = 0

    for i, header in enumerate(headers):
        x_base = start_position + i * (num_csv_files * bar_width) + (i + 1) * spacing  # Start from the beginning of each group
        for j, csv_file in enumerate(csv_files):
            benchmark_data = data.get(csv_file)
            if benchmark_data is not None:
                x = x_base + j * bar_width
                if header != 'IPC':  # Apply PKI transformation except for 'IPC' column
                    transformed_data = benchmark_data[header].apply(pki_transform)  # Transform the data to PKI
                else:
                    transformed_data = benchmark_data[header]  # Keep 'IPC' values as they are
                plt.bar(x, transformed_data, width=bar_width, color=colors[j], label=f'CSV {csv_file}', zorder=3)

    plt.xlabel('Headers')
    plt.ylabel('PKI')
    plt.title(f'All Headers for Benchmark {benchmark}')

    # Adjust x-axis ticks and labels positions
    tick_positions = [start_position + ((i + 0.5) * (num_csv_files * bar_width) + (i + 1) * spacing) for i in range(num_headers)]
    plt.xticks(tick_positions, headers, rotation=45, ha='right')  # Rotate labels by 45 degrees and align them to the right

    # Add horizontal grid lines for every tick of the y-axis
    plt.grid(axis='y', zorder=0)  # Set zorder to 0 for grid lines

    # Simplify legend to only show color mapping for csv_ids
    legend_labels = [f'individual {csv_file}' for csv_file in csv_files]
    plt.legend(legend_labels, loc='upper center', bbox_to_anchor=(1, 1))

    plt.tight_layout()
    # Save plot in cache-plots directory
    if not os.path.exists("cache-plots"):
        os.makedirs("cache-plots")
    plt.savefig(f'cache-plots/all_metrics_for_{benchmark}_{csv_files}.png')
    plt.close()


    # Begin the stacked bar chart visualization


    # Define colors for each metric
    metric_colors = {
        'LLC Load Misses': 'orange',
        'LLC RFO Misses': 'green',
        'LLC Prefetch Misses': 'red',
        'LLC Writeback Misses': 'purple'
    }

    # Calculate the total of all 'Accesses' metrics for normalization
    total_accesses = {}

    # Gather all data for the specified benchmark across all CSV files
    for csv_file in csv_files:
        csv_data = pd.read_csv(f'cache-data_{csv_file}.csv')
        benchmark_data = csv_data[csv_data['Benchmark'] == benchmark]
        if not benchmark_data.empty:
            # Sum all 'Misses' related metrics to calculate the total except 'LLC Total Misses'
            access_columns = [col for col in csv_data.columns if 'LLC' in col and  'Misses' in col and 'Total' not in col]
            total_accesses[csv_file] = benchmark_data[access_columns].sum(axis=1).values[0]

    # Plot the stacked bars
    plt.figure(figsize=(12, 6))

    # We will use a dictionary to collect patches for the legend
    legend_patches = {}

    # Define the width of each stack
    stack_width = 0.35
    # Define the x positions for the CSV files
    x_positions = np.arange(len(csv_files)) * (stack_width * 1.5)

    # Iterate through each CSV file
    for csv_index, csv_file in enumerate(csv_files):
        benchmark_data = pd.read_csv(f'cache-data_{csv_file}.csv')[pd.read_csv(f'cache-data_{csv_file}.csv')['Benchmark'] == benchmark]
        metrics_data = []  # Store tuples of (metric, value)

        for header in access_columns:
            value = benchmark_data[header].values[0]
            metrics_data.append((header, value))
        
        # Calculate the percentages and sort them
        total = sum(value for header, value in metrics_data)
        metrics_data = [(header, value / total * 100) for header, value in metrics_data]
        metrics_data.sort(key=lambda x: x[1], reverse=True)  # Sort by percentage

        # Now, plot the sorted stacks and add text
        bottoms = 0
        for metric, percent in metrics_data:
            color = metric_colors.get(metric, 'gray')  # Get color from dictionary, default to gray if not found
            bar = plt.bar(x_positions[csv_index], percent, bottom=bottoms, color=color, edgecolor='white', width=stack_width)
            bottoms += percent
            # Only add to legend_patches if not already present
            if metric not in legend_patches:
                legend_patches[metric] = plt.Rectangle((0,0),1,1, color=color)
            # Add text annotation
            height = bar[0].get_height()
            plt.text(bar[0].get_x() + bar[0].get_width() / 2, bottoms - (height / 2), f'{percent:.1f}%', ha='center', va='center', color='black', fontsize=8)

    # Set labels and title
    plt.xlabel('Individuals')
    plt.ylabel('Percentage of Total Misses')
    plt.title(f'Side-by-side Percentage Stacked Bar Chart for Benchmark {benchmark}')

    # Adjust the plot
    plt.xticks(x_positions, csv_files)
    plt.tight_layout()

    # Load the IPC speedup data from the CSV file
    speedup_data = pd.read_csv('combined_data_speedups.csv', index_col=0)
    speedup_data.index.name = 'CSV_ID'  # Set the name of the index column

    # Create a secondary y-axis for the IPC speedup
    ax2 = plt.gca().twinx()

    # Initialize a list to hold IPC speedup values for each CSV
    ipc_speedups = []

    # Iterate through the CSV files to get IPC speedup values
    for csv_file in csv_files:
        if csv_file == '0-0':  # Baseline LRU policy has 0% speedup
            ipc_speedups.append(0)
        else:
            # Retrieve the IPC speedup for the current CSV file and benchmark
            ipc_speedup = speedup_data.at[csv_file, benchmark]
            ipc_speedups.append(ipc_speedup)

    # Plot the IPC speedup values on the secondary y-axis
    line = ax2.plot(x_positions, ipc_speedups, label='IPC Speedup', color='blue', marker='o', linestyle='-', linewidth=2)

    # Label the secondary y-axis
    ax2.set_ylabel('IPC Speedup (%)')

    # Add annotations for IPC speedup values next to each point
    for i, txt in enumerate(ipc_speedups):
        plt.text(x_positions[i], ipc_speedups[i], f'{txt:.2f}%', ha='right', va='bottom', color='blue')

    # Create handlers for the bar chart legends (one entry per type of miss)
    bar_handlers = [legend_patches[metric] for metric in sorted(legend_patches)]
    bar_labels = sorted(legend_patches)

    # Create a handler for the IPC Speedup (just one line, hence one entry)
    # The line is already plotted, so we use it to create a legend entry
    line_handler = [line[0]]
    line_labels = ['IPC Speedup']

    # Combine legends from the bar plot and the line plot
    ax2.legend(bar_handlers + line_handler, bar_labels + line_labels, loc='upper left', bbox_to_anchor=(1.05, 1))

    # Adjust the position of the secondary y-axis label if necessary
    ax2.yaxis.set_label_coords(1.05, 0.5)
	

    # Save the plot
    stacked_plot_dir = "STACKED_cache-plots"
    if not os.path.exists(stacked_plot_dir):
        os.makedirs(stacked_plot_dir)
    plt.savefig(f'{stacked_plot_dir}/side_by_side_stacked_all_metrics_for_{benchmark}_{csv_files}.png', bbox_inches='tight')
    plt.close()




def ind_speedup(csv_ids):
    # Ensure the directory exists
    os.makedirs('cache-plots', exist_ok=True)

    # Load the CSV file
    data = pd.read_csv('combined_data_speedups.csv')

    # Filter the data for the specified csv_ids
    filtered_data = data[data['Unnamed: 0'].isin(csv_ids)]

    if filtered_data.empty:
        print("No data found for the provided CSV IDs.")
        return

    # Sort the filtered data based on csv_ids in ascending order
    filtered_data = filtered_data.sort_values(by='Unnamed: 0')
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(filtered_data['Unnamed: 0'], filtered_data['Average Speedup'], color='skyblue')
    plt.xlabel('Individuals')
    plt.ylabel('Average Speedup')
    plt.title('Average Speedup of individuals')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the plot as a PNG file
    plot_filename = 'cache-plots/average_speedup_plot.png'
    plt.savefig(plot_filename)
    plt.close()  # Close the figure to free up memory



def plot_ipc_speedup(ids, benchmarks):
    csv_file = 'speedups.csv'
    plot_dir = 'cache-plots'
    
    # Ensure the directory for plots exists
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    # Check if the speedups.csv file exists
    if not os.path.exists(csv_file):
        print(f"{csv_file} not found. Executing speedups.py to generate the file.")
        subprocess.run(["python3", "speedups.py"], check=True)

    # Load the speedups data, set the first column as the index since it contains the IDs
    df = pd.read_csv(csv_file, index_col=0)

    # If 'all' is passed as benchmarks, use all columns except 'Average Speedup'
    if benchmarks == ['all']:
        benchmarks = [col for col in df.columns if col != 'Average Speedup']
    else:
        # Sort benchmarks by the order they appear in the CSV file if specific benchmarks are requested
        benchmark_order = {name: idx for idx, name in enumerate(df.columns) if name in benchmarks}
        benchmarks = sorted(benchmarks, key=lambda x: benchmark_order[x])

    # Set up the plotting parameters
    plt.figure(figsize=(12, 7))
    num_ids = len(ids)
    bar_width = 0.3 / num_ids  # Adjust bar width based on number of IDs
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'][:num_ids]

    # Create a bar chart for each ID
    for i, id_ in enumerate(ids):
        positions = [j + bar_width * i for j in range(len(benchmarks))]
        plt.bar(positions, df.loc[id_, benchmarks], width=bar_width, color=colors[i], label=f'ID {id_}')

    # Add plot labels and legend
    plt.xlabel('Benchmark')
    plt.ylabel('Speedup (%)')
    plt.title('IPC Speedup Comparison Across Benchmarks')
    plt.xticks([r + bar_width * (num_ids - 1) / 2 for r in range(len(benchmarks))], benchmarks, rotation=45)
    plt.legend()

    # Enable horizontal grid lines for better readability
    plt.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

    # Adjust layout to ensure everything fits and nothing is cut off
    plt.tight_layout()

    # Define the filename based on benchmarks and ids
    if len(benchmarks) == 16:
        benchmark_part = 'all-benchmarks'
    else:
        benchmark_part = '-'.join(benchmarks)
    filename = f"IPC-speedup-for-{benchmark_part}-ids.png"
    plt.savefig(os.path.join(plot_dir, filename))
    plt.close()  # Close the plot to free up memory

    print(f"Plot saved to {os.path.join(plot_dir, filename)}")

def plot_average_speedup_by_generation(csv_file):
    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        # If not, run the script to generate the CSV file
        print(f"{csv_file} not found. Generating new CSV file...")
        subprocess.run(['python3', 'speedups.py'], check=True)
        
        # Check if the file was successfully created
        if not os.path.exists(csv_file):
            print("{csv_file} does not exist and failed to generate the CSV file.")
            return  # Exit the function if file is still not present

    # Read the CSV file; the first column is unnamed and will be automatically assigned a header
    data = pd.read_csv(csv_file, header=0)
    data.rename(columns={data.columns[0]: 'ID'}, inplace=True)  # Rename the first unnamed column to 'ID'

    # Define a function to validate and extract the generation number
    def extract_generation(id_string):
        # Match the expected 'X-Y' pattern
        match = re.match(r'^(\d+)-\d+$', id_string.strip())
        if match:
            return int(match.group(1))
        return None  # Return None for any format that does not match

    data['Generation'] = data['ID'].apply(extract_generation)

    # Filter out rows with invalid or missing generation numbers
    data = data.dropna(subset=['Generation'])

    # Calculate the mean speedup per generation
    average_speedup = data.groupby('Generation')['Average Speedup'].mean()

    # Plotting
    plt.figure(figsize=(12, 6))
    average_speedup.plot(kind='bar', color='skyblue', rot=0)  # rot parameter rotates the x-axis labels

    # Customize the x-axis to have integer labels
    plt.xticks(range(len(average_speedup)), average_speedup.index.astype(int))

    plt.xlabel('Generation')
    plt.ylabel('Average Speedup (%)')
    plt.title('Average IPC Speedup per Generation')
    plt.grid(True)
    plt.tight_layout()  # This adjusts the plot to make sure everything fits without overlapping
    plt.savefig('average_IPC_speedup_by_generation.png')
    plt.close()


def heat_map_all():
    # Load the speedup data and filter rows based on the X-Y pattern in the first column
    speedup_data = pd.read_csv('combined_data_speedups.csv')
    speedup_data = speedup_data[speedup_data[speedup_data.columns[0]].astype(str).str.match(r'^\d+-\d+$')]
    
    # Map each X-Y to the corresponding Average Speedup
    speedup_map = dict(zip(speedup_data[speedup_data.columns[0]], speedup_data['Average Speedup']))
    
    # Use glob to find all CSV files matching the pattern 'cache-data_*-*.csv'
    files = glob.glob('cache-data_*-*.csv')
    combined_data = pd.DataFrame()

    # Process each file
    for file in files:
        # Extract the X-Y identifier from the filename
        match = re.search(r'cache-data_(\d+-\d+).csv', file)
        if match:
            xy_identifier = match.group(1)
            if xy_identifier in speedup_map:
                data = pd.read_csv(file)
                
                # Filter for 'LLC' related metrics
                llc_columns = [col for col in data.columns if 'LLC' in col]
                
                if llc_columns and 'IPC' in data.columns:
                    # Create a copy of the data to avoid SettingWithCopyWarning
                    filtered_data = data[llc_columns].copy()
                    # Set the corresponding Average Speedup value using loc
                    filtered_data.loc[:, 'Average Speedup'] = speedup_map[xy_identifier]
                    
                    # Append to the combined DataFrame
                    combined_data = combined_data.append(filtered_data, ignore_index=True)
    
    if not combined_data.empty:
        # Generate a heatmap of the correlations using Spearman's rank correlation
        plt.figure(figsize=(10, 8))
        sns.heatmap(combined_data.corr(method='spearman'), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Spearman Rank Correlation Heatmap of LLC Metrics and Average Speedup')
        
        # Save the figure as a PNG file
        plt.savefig('heatmap_spearman_correlation.png')
        plt.close()  # Close the plot to free up memory
    else:
        print("No valid data found in CSV files.")


def heat_map_ind(xy_identifier):
    # Load the specific cache-data file
    cache_data_filename = f'cache-data_{xy_identifier}.csv'
    cache_data = pd.read_csv(cache_data_filename)
    
    # Filter for 'LLC' related metrics
    llc_columns = [col for col in cache_data.columns if 'LLC' in col]
    cache_data = cache_data[llc_columns]
    
    # Generate a heatmap of the correlations using Pearson's correlation
    plt.figure(figsize=(10, 8))
    sns.heatmap(cache_data.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(f'Pearson Correlation Heatmap of LLC Metrics for {xy_identifier}')
    
    # Save the figure as a PNG file
    heatmap_filename = f'heatmap_llc_{xy_identifier}.png'
    plt.savefig(heatmap_filename)
    plt.close()  # Close the plot to free up memory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate plots for cache data.')

    # Adding mutual exclusive group to ensure that the user only selects one plotting mode at a time.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--plot_cache', action='store_true', help='Plot cache data based on headers and benchmarks.')
    group.add_argument('--plot_gen_speedup', action='store_true', help='Plot average speedup by generation.')
    group.add_argument('--hm', action='store_true', help='Activate heat map generation (specify with --ids or use default for all).')
    group.add_argument('--isu', action='store_true', help='Generate individual speedup plot for CSV IDs specified with --ids.')

    parser.add_argument('header', nargs='?', type=str, help='Header of the column to plot ("all" to plot all headers for a specific benchmark)')
    parser.add_argument('--bms', nargs='+', type=str, help='List of benchmark names or "all" to plot all benchmarks')
    parser.add_argument('--ids', nargs='+', type=str, help='List of CSV (individual) ids')
    parser.add_argument('--csv_file', type=str, help='CSV file path for generation speedup plotting', default='speedups.csv')
    
    args = parser.parse_args()

    if args.plot_cache:
        if not args.header or not args.bms or not args.ids:
            parser.error("When plotting cache data, --header, --bms, and --ids are required.")
        if args.header == 'IPC':
            plot_ipc_speedup(args.ids, args.bms)
        elif args.header == 'all':
            if len(args.bms) != 1:
                print("Error: 'all' can only be used with a single benchmark argument.")
            else:
                plot_all_headers_for_benchmark(args.ids, args.bms[0])
        else:
            plot_cache_data(args.ids, args.bms, args.header)
    elif args.plot_gen_speedup:
        if not args.csv_file:
            parser.error("--plot_gen_speedup requires --csv_file.")
        plot_average_speedup_by_generation(args.csv_file)
    elif args.hm:
        if args.ids:
            heat_map_ind(args.ids)  # Assuming heat_map_ind can handle a list or a single identifier
        else:
            heat_map_all()
    elif args.isu:
        if args.ids:
            ind_speedup(args.ids)
        else:
            print("No CSV IDs provided for individual speedup plot.")

        
