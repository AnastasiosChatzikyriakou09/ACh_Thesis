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
import copy
import sys

class Instruction(object):
    '''
    Represents an assembly instruction, including label and branch capabilities.
    '''

    def __init__(self, name, ins_type, numOfOperands, operands=[], format="op1,op2,op3", toggleable="False", label=None, branch_target=None):
        '''
        Constructor
        '''
        self.name = name
        self.ins_type = ins_type
        self.operands = operands
        self.format = format.replace("\\n", "\n").replace("\\t", "\t")  # Simplified replacement
        self.numOfOperands = numOfOperands
        self.toggleable = toggleable
        self.label = label
        self.branch_target = branch_target
        
    def copy(self):
        return copy.deepcopy(self)
        
    def setOperands(self, operands):
        self.operands = operands
        
    def getOperand(self, index=0):
        if index >= len(self.operands) or index < 0:
            print("error: index out of bounds")
            sys.exit()
        return self.operands[index]
    
    def getOperands(self):
        return self.operands
    
    def toggle(self, value_index):
        for op in self.operands:
            if op.toggleable == "True":
                op.setCurrentValueByIndex(value_index)
    
    def mutateOperands(self, rand):
        for op in self.operands:
            op.mutate(rand)

    def setOperandValue(self, i):
        for op in self.operands:
            op.setCurrentValueByIndex(i)
    
    def is_label(self):
        # Assuming label instructions contain ':'
        return ':' in self.name
    
    def get_label(self):
        if self.is_label():
            return self.name[:-1]  # Assuming label name is like "LABEL:"
        return None

    def is_branch(self):
        # Assuming branch instructions contain certain keywords, e.g., JMP, CALL, etc.
        return 'jmp' in self.ins_type.lower() or 'call' in self.ins_type.lower()

    def set_branch_target(self, label):
        self.branch_target = label

    def __str__(self):
        if (str(self.numOfOperands).strip() == "0") or (self.operands[0].currentValue != ""):
            representation = self.format
            for i in range(len(self.operands)):
                toReplace = "op" + str(i+1)
                representation = representation.replace(toReplace, str(self.operands[i]))
            return representation
        else:
            representation = f"name {self.name}\ntype {self.ins_type}\nformat {self.format}\nnumOfOperands {self.numOfOperands}\n"
            for op in self.operands:
                representation += "\t" + str(op) + "\n"
            return representation


