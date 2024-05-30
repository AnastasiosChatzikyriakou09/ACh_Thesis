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

import operator
import pickle

class Population(object):
    def __init__(self, individuals=[]):
        self.individuals = individuals

    def getIndividual(self, index):
        return self.individuals[index]

    def getFittest(self):
        # Assuming fitness now returns the average of the max IPCs
        best_indiv = max(self.individuals, key=lambda indiv: indiv.getFitness())
        return best_indiv

    def getAvgFitness(self):
        total_fitness = sum(indiv.getFitness() for indiv in self.individuals)
        return total_fitness / len(self.individuals)

    def getSize(self):
        return len(self.individuals)

    def pickRandomlyAnIndividual(self, rand):
        return rand.choice(self.individuals)

    def setCumulativeFitness(self):
        # For roulette wheel selection, recalculating cumulative fitness based on new fitness evaluation
        self.individuals[0].setCumulativeFitness(int(self.individuals[0].getFitness() * 1000000))
        for i in range(1, len(self.individuals)):
            fitness = int(self.individuals[i].getFitness() * 1000000)
            self.individuals[i].setCumulativeFitness(self.individuals[i-1].cumulativeFitness + fitness)

    def sortByFitessToWeakest(self):
        self.individuals.sort(key=lambda indiv: indiv.getFitness(), reverse=True)

    def sortByWeakestToFitess(self):
        self.individuals.sort(key=lambda indiv: indiv.getFitness())

    def saveIndividual(self, index, individual):
        self.individuals[index] = individual

    def __str__(self):
        return "\n".join(str(indiv) for indiv in self.individuals)

    def keepHalfBest(self):
        # Keep the half of the population with the highest fitness
        self.sortByFitessToWeakest()
        self.individuals = self.individuals[:len(self.individuals) // 2]

    def pickle(self, filename):
        pickle.dump(self, filename)

    @staticmethod
    def unpickle(filename):
        return pickle.load(filename)

