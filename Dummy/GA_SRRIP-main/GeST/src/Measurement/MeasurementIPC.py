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

import subprocess
import random
from time import sleep
from Measurement.Measurement import Measurement 


class MeasurementIPC(Measurement):
    '''
    This class extends the Measurement class to handle simulations and IPC calculations 
    for "combination-of-two" individuals. Each individual contains two sets of policy parameters, 
    and simulations are run for both to determine the best IPC performance for each benchmark.
    '''

    def __init__(self, confFile):
        super().__init__(confFile)

    def init(self):
        super().init()
        self.timeToMeasure = self.tryGetIntValue('time_to_measure')

    def move(self, generation, myID):
        super().moveFile(generation, myID)

    def RunSimulations(self, generation):
        # Assuming each policy has a separate simulation setup
        execution_command = f"cd /home/achatz13/Dummy/GA_SRRIP-main/SADRRIP; python3 RunSimFromGeSt.py {generation} >> trash.txt"
        subprocess.run(execution_command, shell=True)

        # Sleep while jobs are running; this time could vary based on the job queue system
        sleep(1800)

        # Check job queue until all jobs from this generation are complete
        while True:
            output = subprocess.check_output("squeue -u achatz13 | wc -l", shell=True)
            output = output.decode().strip()
            if output == "1":
                break
            else:
                sleep(300)

    def GetMeasurement(self, generation, myID):
        # Collect results for both policies
        output_command = f"cd /home/achatz13/Dummy/SADRRIP; python3 ipc_parser.py {generation} {myID}"
        try:
            avg_max_ipc = subprocess.check_output(output_command, shell=True, timeout=300).decode().strip()
            # print(avg_max_ipc + " " + str(myID) + "\n") # DEBUG statement
            return float(avg_max_ipc)  # Ensuring the output is float
        except subprocess.TimeoutExpired:
            print("Failed to get IPC measurement: process timed out.")
            return None
        except ValueError:
            print("Failed to convert IPC result to float.")
            return None


    def measure(self, generation, myID):
        super().moveFile(generation, myID)
        execution_command = f"cd /home/achatz13/Dummy/GA_SRRIP-main/SADRRIP; python3 RunSimFromGeSt.py {generation} {myID}"
        output_command = f"cd /home/achatz13/Dummy/SADRRIP; python3 ipc_parser.py {generation} {myID}"
        subprocess.run(execution_command, shell=True)

        sleep(1800)
        
        while True:
            output = subprocess.check_output("squeue -u achatz13 | wc -l", shell=True)
            output = output.decode().strip()
            if output == "1":
                break
            else:
                print(f"Jobs not finished there are still {output} more jobs")
                sleep(300)

        ipc_results = subprocess.check_output(output_command, shell=True)
        ipc_results = ipc_results.decode().strip().split()

        # Convert IPC strings to float and return as measurements
        measurements = [float(ipc) for ipc in ipc_results]
        return measurements

