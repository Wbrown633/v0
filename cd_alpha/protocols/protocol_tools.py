from collections import OrderedDict
import json
import sys
import time
import calendar


class ProcessProtocol:

    def __init__(self, protocol_file) -> None:
        self.protocol_file = protocol_file
        self.load_protocol()
    
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
                            step_time = self.calculate_step_time_sec(volume, flowrate, duration)
                            material = self.protocol[key]["header"].split(" ")[0]
                            list_of_table_entries.append([step_number, material, flowrate, volume, step_time])
                        elif steps == "INCUBATE":
                            # This is so hacky it's insane, but it I couldn't figure out how to fix the year getting set to 1900
                            # So if we force the year to 1970 during the conversion all of the conversions back and forth between date-times
                            # and times work out. 
                            incubate = self.protocol[key][k][steps]["time"]
                            str_time_without_inc = list_of_table_entries[-1][-1]
                            time_as_struct = time.strptime(str_time_without_inc + ":1970", '%H:%M:%S:%Y')
                            time_with_inc = calendar.timegm(time_as_struct) + incubate
                            str_time_with_inc = time.strftime('%H:%M:%S', time.gmtime(time_with_inc))
                            list_of_table_entries[-1][-1] = str_time_with_inc

        
        return list_of_table_entries
                            
    def calculate_step_time_sec(self, vol: int, flowrate: float, wait: int):
        seconds = (vol/flowrate * 3600 + wait)
        return time.strftime('%H:%M:%S', time.gmtime(seconds))


if __name__ == "__main__":
    filename = 'v0-protocol-16v3-pretty.txt'
    original_stdout = sys.stdout
    with open(filename, 'w') as f:
        proto = ProcessProtocol("v0-protocol-16v3.json")
        print("Process Protocol")
        sys.stdout = f
        for line in proto.list_steps():
            print(line)
        sys.stdout = original_stdout
        print("File Output to: {}".format(filename))

