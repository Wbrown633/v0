
from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum
from dataclasses import dataclass
import json
from mimetypes import init
from typing import List

from requests import head


TEST_FILE_LOCATION = "test_output.json"

@dataclass
class StepType(Enum):
    PUMP = 1
    INCUBATE = 2
    PUMPANDRELEASE = 3
    DESCRIPTION = 4

@dataclass
class ActionType(Enum):
    PUMP = 1
    GRAB = 2
    RELEASE = 3
    INCUBATE = 4
    RESET = 5

@dataclass
class Target(Enum):
    WASTE = 1
    LYSATE = 2

@dataclass
class ScreenType(Enum):
    MachineActionScreen = 1
    UserActionScreen = 2


@dataclass
class Step:
    material: str
    step_number: int
    description_text: str
    screentype: ScreenType
    steptype: StepType
    target: Target
    volume: float
    flowrate: float
    wait_time: int


    # how do we handle description steps ? 
    def makejson(self):
        return {self.material + "_" + str(self.step_number): {"type": self.screentype.name, "header": self.material + "_" + str(self.step_number), "description": self.description_text, 
            "action": {self.steptype.name: {"target": self.target.name, "vol_ml": self.volume, "rate_mh": self.flowrate, "eq_time": self.wait_time}}}}


class StepBuilder:

    def __init__(self, step_name: str) -> None:
        self.step_name = step_name
        self.stepdict = OrderedDict()

    def add_type(self, type: ScreenType):
        self.stepdict["type"] = type.name 

    def add_header(self, header: str):
        self.stepdict["header"] = header

    def add_description(self, description: str):
        self.stepdict["description"] = description

    def add_next_text(self, next_text: str):
        self.stepdict["next_text"] = next_text

    def add_actions(self, action_types: List[Action]):
        for act in action_type:
            pass

    def getStep(self):
        return {self.step_name: self.stepdict}


    
class ProtocolFactory:

    '''"type": "MachineActionScreen",
        "header": "Initialization",
        "description": "Initializing device. Resetting syringe positions and checking connections.",
        "action": {
            "RESET": {}
        },
        "remove_progress_bar": true,
        "completion_msg": "Machine has been homed"
        '''
    
    def __init__(self, list_of_steps):
        self.list_of_steps = list_of_steps
    
    def create_step(self):
        # PSEUDO CODE

        # Create a JSON protocol given the following information for every step
        # TYPE: {PUMP, INCUBATE, PUMP/RELEASE}
        # STEP_INFO: [TARGET, VOL_ML, RATE_MH, EQ_TIME_SECS]
        pass

    def json_dump(self):
        with open(TEST_FILE_LOCATION, 'w') as f:
            steps_dictionary = {}
            for s in self.list_of_steps:
                steps_dictionary.update(s.makejson())  
            json.dump(steps_dictionary, f, indent=4)
            


if __name__ == "__main__":
    
    s1 = Step("PBS", 1, "Rinsing the chip step 1.", ScreenType.MachineActionScreen ,StepType.PUMP, Target.WASTE, volume=1.0, flowrate=10.0, wait_time=120)
    s2 = Step("PBS", 2, "Rinsing the chip step 2.", ScreenType.MachineActionScreen ,StepType.PUMP, Target.WASTE, volume=0.5, flowrate=5.0, wait_time=120)
    s3 = Step("PBS", 3, "Rinsing the chip step 3.", ScreenType.MachineActionScreen ,StepType.PUMP, Target.WASTE, volume=1.5, flowrate=15.0, wait_time=120)
    
    list_of_steps = [s1,s2,s3]

    p = ProtocolFactory(list_of_steps)

    print("Making json dump ")
    p.json_dump()
