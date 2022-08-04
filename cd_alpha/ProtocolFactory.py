
from __future__ import annotations
from abc import ABC, abstractmethod
from argparse import Action
from collections import OrderedDict
from enum import Enum
from dataclasses import dataclass
import json
from typing import Dict, List



TEST_FILE_LOCATION = "test_output.json"

@dataclass
class StepType(Enum):
    PUMP = 1
    INCUBATE = 2
    PUMPANDRELEASE = 3
    DESCRIPTION = 4


# PUMP = 1
# GRAB = 2
# RELEASE = 3
# INCUBATE = 4
# RESET = 5


class ActionType(ABC):
    @abstractmethod
    def make_dict(self) -> Dict:
        raise NotImplementedError("Need to override base class")


class Pump(ActionType):
    target:str
    vol_ml: float
    rate_mh: float
    eq_time: int

    def make_dict(self) -> Dict[str, str]:
        return {"PUMP": {"target": self.target, "vol_ml": self.vol_ml, "rate_mh": self.rate_mh, "eq_time": self.eq_time}}

class Grab(ActionType):
    post_run_rate_mm: float
    post_run_vol_ml: float

    def make_dict(self) -> Dict:
        return {"GRAB": {"post_run_rate_mm": self.post_run_rate_mm, "post_run_vol_ml": self.post_run_vol_ml}}

class Release(Pump):
    def make_dict(self) -> Dict[str, str]:
        return {"RELEASE": {"target": self.target, "vol_ml": self.vol_ml, "rate_mh": self.rate_mh, "eq_time": self.eq_time}}

class Incubate(ActionType):
    time: int

    def make_dict(self) -> Dict:
        return {"INCUBATE": {"time": self.time}}


class Reset(ActionType):
    def make_dict(self) -> Dict:
        return {"RESET": {}}


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

    def __init__(self, step_name: str):
        self.step_name = step_name
        self.stepdict = OrderedDict()

    def add_type(self, type: ScreenType) -> StepBuilder:
        self.stepdict["type"] = type.name
        return self

    def add_header(self, header: str) -> StepBuilder:
        self.stepdict["header"] = header
        return self

    def add_description(self, description: str) -> StepBuilder:
        self.stepdict["description"] = description
        return self

    def add_next_text(self, next_text: str) -> StepBuilder:
        self.stepdict["next_text"] = next_text
        return self

    def add_actions(self, action_types: List[ActionType]) -> StepBuilder:
        for act in action_types:
            self.stepdict["action"] = act.make_dict()

        return self

    def remove_progress_bar(self, remove: bool) -> StepBuilder:
        self.stepdict["remove_progress_bar"] = remove
        return self

    def add_completion_msg(self, msg: str) -> StepBuilder:
        self.stepdict["completion_msg"] = msg
        return self

    def getStep(self) -> OrderedDict:
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
    
    def __init__(self, list_of_steps: List[StepBuilder]):
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
                steps_dictionary.update(s.getStep())  
            json.dump(steps_dictionary, f, indent=4)
            


if __name__ == "__main__":

    s1 = StepBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics").add_description("Ready for a new test").add_next_text("Start")
    s2 = StepBuilder("reset_start").add_type(ScreenType.MachineActionScreen).add_header("Initialization").add_description("Init device").add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("Machine has been homed")




    list_of_steps = [s1, s2]

    p = ProtocolFactory(list_of_steps)

    print("Making json dump ")
    p.json_dump()
