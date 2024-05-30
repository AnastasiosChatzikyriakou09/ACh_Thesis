'''
Copyright 2019 ARM Ltd. and University of Cyprus
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import os
import sys
import pickle
from Population import Population
from Individual import Individual
import re

def main():
    path = sys.argv[1]
    files = []
    for root, dirs, filenames in os.walk(path):  # Walk through the directory with saved states
        for f in filenames:
            if ".pkl" in f and "rand" not in f:
                files.append(f)

    files.sort(key=lambda x: int(x.split('.')[0]))
    
    # Print header with properly aligned column titles
    print("{:<10} {:<12} {:<12}".format("Generation", "Best Fitness", "Average Fitness"))

    insHash = {}
    columns = []
    theBest = []
    totalInstructionCount = 0  # Keep track of total instructions across all individuals and generations

    for f in files:
        with open(os.path.join(path, f), "rb") as input_file:
            pop = pickle.load(input_file)
        
        best = pop.getFittest()
        theBest.append(best)
        columns.append(f.split('.')[0])
        sum_fitness = 0.0
        count = 0

        for indiv in pop.individuals:
            sum_fitness += indiv.getFitness()
            count += 1
            # Aggregate instructions from both parts
            for part in [indiv.part1, indiv.part2]:
                for ins in part:
                    if ins.name in insHash:
                        insHash[ins.name] += 1
                    else:
                        insHash[ins.name] = 1
                    totalInstructionCount += 1  # Increment total instruction count

        average_fitness = sum_fitness / count if count else 0
        # Print each generation's results with proper alignment
        print("{:<10} {:<12.6f} {:<12.6f}".format(f.split('.')[0], best.getFitness(), average_fitness))

    print_instruction_mix(insHash, totalInstructionCount)

def print_instruction_mix(instruction_mix, total_instructions):
    print("Instruction Mix per Generation")
    sorted_ins = sorted(instruction_mix.items(), key=lambda item: item[1], reverse=True)
    for ins, count in sorted_ins:
        percentage = (count / total_instructions) * 100  # Correct percentage calculation
        print(f"{ins}: {percentage:.2f}%")

if __name__ == "__main__":
    main()

