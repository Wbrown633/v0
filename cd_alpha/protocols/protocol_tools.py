from collections import OrderedDict
import argparse
import json
from multiprocessing.sharedctypes import Value
from textwrap import indent
from unicodedata import name
import sys



class ProcessProtocol:

    def __init__(self, protocol_file) -> None:
        self.protocol_file = protocol_file
    
    #protocol_file = "v0-protocol-16v3.json"
    protocol = None

    def load_protocol(self):
        with open(self.protocol_file, 'r') as f:
            self.protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

    def list_steps(self):
        step_number = 0
        incubate = 0
        list_of_table_entries = []
        print("Step # \t\tMaterial \t\tFlowrate(mL/h) \t\tVolume(mL) \t\tStep Duration")
        for key in self.protocol.keys():
            for k in self.protocol[key]:
                if k == "action":
                    for steps in self.protocol[key][k]:
                        if steps == "PUMP":
                            step_number += 1
                            for s in self.protocol[key][k][steps]:
                                if s == "vol_ml":
                                    volume = self.protocol[key][k][steps][s]
                                elif s == "rate_mh":
                                    flowrate = self.protocol[key][k][steps][s]
                                elif s == "eq_time":
                                    duration = self.protocol[key][k][steps][s]
                            material = self.protocol[key]["header"].split(" ")[0]
                            list_of_table_entries.append([step_number, material, flowrate, volume, duration])
                        elif steps == "INCUBATE":
                            incubate = self.protocol[key][k][steps]["time"]
                            list_of_table_entries[-1][-1]+= incubate
        
        for line in list_of_table_entries:
            print(line)
                            

    def calculate_step_time(self, step: OrderedDict):
        step["time"]          


if __name__ == "__main__":
    filename = 'v0-protocol-16v3-pretty.txt'
    original_stdout = sys.stdout
    with open(filename, 'w') as f:
        proto = ProcessProtocol("v0-protocol-16v3.json")
        print("Process Protocol")
        sys.stdout = f
        proto.load_protocol()
        proto.list_steps()
        sys.stdout = original_stdout
        print("File Output to: {}".format(filename))

