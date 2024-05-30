# ChampSimParser
A python tool to Parse ChampSim output files

This repository consists of 2 python scripts

The Output_to_CSV.py script will parse the output for 1 replacement policy and create for each benchmark 6 CSV files that contain the values of each statistic.
The CSV files have the format of type,key,value where type coresponds to one of Total/Load/RFO/Prefetch/Writeback/RQ.


The CSV_to_Statistics script will read the csv files created can crate charts or print other metrics
