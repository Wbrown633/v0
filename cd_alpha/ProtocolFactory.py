
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum
from dataclasses import dataclass
import json
from typing import Dict, List


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
    def make_dict(self) -> Dict:
        return {self.__class__.__name__.upper():self.__dict__}

@dataclass
class Pump(ActionType):
    target:str
    vol_ml: float
    rate_mh: float
    eq_time: int

@dataclass
class Grab(ActionType):
    post_run_rate_mm: float
    post_run_vol_ml: float

@dataclass
class Release(Pump):
    def make_dict(self) -> Dict[str, str]:
        return json.dumps(self, default=lambda o: o.__dict__)

@dataclass
class Incubate(ActionType):
    time: int

@dataclass
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
    description_text: str
    steptype: StepType
    target: Target
    volume: float
    flowrate: float
    wait_time: int


    # how do we handle description steps ? 
    def makejson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


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

    def create_protocol(self, output_file: str):
        '''Creates and exports a json protocol at the givent file location.'''

        ## Add default steps before and after pump steps ### 

        self._add_default_steps()
        self.json_dump(output_file)

    def _add_default_steps(self):
        SETUP_STEPS = self._define_setup_steps()
        TEARDOWN_STEPS = self._define_teardown_steps()
        
        self.list_of_steps.insert(0,SETUP_STEPS)
        self.list_of_steps.append(TEARDOWN_STEPS)

    def _define_setup_steps(self) -> List[Step]:
        list_of_steps = []

        home_step = StepBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics")\
            .add_description("Ready for a new test with protocol 20v0. \
                Press 'Start' to begin.").add_next_text("Start").getStep()

        reset_start_step = StepBuilder("reset_start").add_type(ScreenType.MachineActionScreen)\
            .add_header("Initialization").add_description("Initializing device. Resetting syringe positions and checking connections.")\
                .add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("Machine has been homed").getStep()

        insert_syringes_step = StepBuilder("insert_syringes").add_type(ScreenType.UserActionScreen).add_header("Insert syringes")\
            .add_description("Insert the waste and lysate syringe. Press 'Start initialization' to initialize when ready.").add_next_text("Start initialization").getStep()


        grab_syringes_step = StepBuilder("grab_syringes").add_type(ScreenType.MachineActionScreen).add_header("Grabbing syringes")\
            .add_description("The device is now grabbing hold of the syringes to secure a precise operation.").add_actions([Grab(5,0.3)]).remove_progress_bar(True).add_completion_msg("Syringes ready").getStep()
    
    
    
    def _define_teardown_steps(self) -> List[Step]:
        pass

    def json_dump(self, file_location: str):
        with open(file_location, 'w') as f:
            steps_dictionary = {}
            for s in self.list_of_steps:
                steps_dictionary.update(s.getStep())  
            json.dump(steps_dictionary, f, indent=4)
            


if __name__ == "__main__":

    s1 = StepBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics").add_description("Ready for a new test").add_next_text("Start")
    s2 = StepBuilder("reset_start").add_type(ScreenType.MachineActionScreen).add_header("Initialization").add_description("Init device").add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("Machine has been homed")
    s3 = StepBuilder("flush_2").add_type(ScreenType.MachineActionScreen).add_header("PBS rinse").add_description("Risning the chip.").add_actions([Pump("waste", 1.05, 50, 120)])

    list_of_steps = [s1, s2, s3]

    p = ProtocolFactory(list_of_steps)
    TEST_FILE_LOCATION = "test_output.json"

    print("Making json dump ")
    p.json_dump(TEST_FILE_LOCATION)
