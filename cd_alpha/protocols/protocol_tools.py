from collections import OrderedDict
import argparse
import json
from multiprocessing.sharedctypes import Value
from textwrap import indent
from unicodedata import name
import pprint



class ProcessProtocol:

    def __init__(self, protocol_file) -> None:
        self.protocol_file = protocol_file
    
    #protocol_file = "v0-protocol-16v3.json"
    protocol = None

    def load_protocol(self):
        with open(self.protocol_file, 'r') as f:
            self.protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

    def list_steps(self):
        step_number = 1
        for key in self.protocol.keys():
            step_number += 1
            for k in self.protocol[key]:
                if k == "header":
                    print("Step # {} : {}".format(step_number, self.protocol[key][k]))
                
                if k == "description":
                    p.pprint(self.protocol[key][k])
                    print("\n")
                if k == "action":
                    for steps in self.protocol[key][k]:
                        p.pprint(steps)
                        for s in self.protocol[key][k][steps]:
                            if s == "target":
                                p.pprint("Targeting Syringe : {}".format(self.protocol[key][k][steps][s]))
                            elif s == "vol_ml":
                                p.pprint("Volume Pulled (mL) : {}".format(self.protocol[key][k][steps][s])) 
                            elif s == "rate_mh":
                                p.pprint("Syringe Pull Rate (mL/h) : {}".format(self.protocol[key][k][steps][s]))
                            elif s == "eq_time":
                                p.pprint("Wait time (s) : {}".format(self.protocol[key][k][steps][s]))
                        print("\n")

                    print("\n")

if __name__ == "__main__":
    p = pprint.PrettyPrinter(indent=4)
    proto = ProcessProtocol("v0-protocol-17v1.json")
    print("Process Protocol")
    proto.load_protocol()
    proto.list_steps()

