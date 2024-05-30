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
import pickle
import copy

class Individual(object):
    '''
    Represents a single individual in the population. Each individual consists of two parts,
    representing two distinct cache replacement policies combined.
    '''
    id = 0

    def __init__(self, part1=[], part2=[], generation=0, parents=None):
        Individual.id += 1
        self.myId = Individual.id
        self.part1 = part1
        self.part2 = part2
        self.fitness = 0.0
        self.measurements = []
        self.generation = generation
        self.parents = parents if parents is not None else []
        self.fixUnconditionalBranchLabels()

    def fixUnconditionalBranchLabels(self):
        for part in [self.part1, self.part2]:
            # Create a dictionary of label positions
            label_positions = {ins.get_label(): idx for idx, ins in enumerate(part) if ins.is_label()}
            
            # Loop through each instruction in the part
            for ins in part:
                if ins.is_branch():
                    # Get the target label of the branch instruction
                    target_label = ins.get_branch_target()
                    
                    # Check if the target label exists in the label positions dictionary
                    if target_label in label_positions:
                        # Set the branch target to the correct index position
                        ins.set_branch_target(label_positions[target_label])
                    else:
                        # If the target label is not found, raise an error
                        raise ValueError(f"Branch target label '{target_label}' not found in the sequence.")
 

    def addInstruction(self, anInstruction, part):
        if part == 1:
            self.part1.append(anInstruction)
        else:
            self.part2.append(anInstruction)

    def getInstructions(self, part):
        return self.part1 if part == 1 else self.part2

    def belongsToInitialSeed(self):
        # Check if parents is None or empty
        return not self.parents  # Returns True if parents is an empty list, False otherwise

    def setParents(self, parents):
        self.parents = parents

    def getParents(self):
        return self.parents

    def clearParents(self):
        self.parents=None;
    
    def setMeasurementsVector(self, measurements):
        self.measurements = measurements

    def setFitness(self, fitness):
        self.fitness = fitness

    def getFitness(self):
        return self.fitness

    def getMeasurements(self):
        return self.measurements

    def __str__(self):
        output = ""
        output += "\tPART_1:\n\t\t"
        for ins in self.part1:
            output += str(ins) + "\n\t\t"
        output += "\n\tPART_2:\n\t\t"
        for ins in self.part2:
            output += str(ins) + "\n\t\t"
        return output

    def copy(self):
        return copy.deepcopy(self)

    def pickle(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def unpickle(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

