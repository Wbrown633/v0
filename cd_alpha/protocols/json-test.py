import json
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from dacite import data, from_dict

PROTOCOL_FILE_NAME = "cda-protocol-v01.json"


@dataclass
class Step_Content:
    """Class to represent a step in the procedure."""
    type: str = ""
    header: str = ""
    description: str = ""
    next_text: str = ""
    action: dict[str] = field(default_factory=dict)
    remove_progress_bar: bool = False
    completion_msg: str = ""

@dataclass
class Step:
    step: Step_Content

def print_json(filepath: str):
    list_of_steps = []

    with open(filepath, 'r') as f:
        d = json.loads(f.read(), object_pairs_hook=OrderedDict)
    
    step = from_dict(data_class=Step, data=d)
    for k, v in d.items():
        print("Name: " + k)
        for keys, values in v.items():
            print("Key: {}, Value: {}".format(keys,values))

    print(len(step))

            


if __name__ == '__main__':
    list_of_arguments = sys.argv

    print_json(list_of_arguments[1])
