from argparse import Action
from dataclasses import dataclass
from email import header
from typing import Dict, List
from abc import ABC, abstractmethod
from enum import Enum

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
    pass


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
class StepType(Enum):
    PUMP = 1
    INCUBATE = 2
    PUMPANDRELEASE = 3
    DESCRIPTION = 4


@dataclass
class Step:
    material: str
    header: str
    description_text: str
    next_text: str
    steptype: StepType
    target: Target
    volume: float
    flowrate: float
    wait_time: int
    list_of_actions: List[Action]
    remove_progress_bar: bool
    completion_msg: str

    # how do we handle description steps ? 
    def makejson(self):
        return {f"{self.material}_{str(self.step_number)}": {"type": self.screentype.name, "header": f"{self.material}_{str(self.step_number)}", "description": self.description_text, "action": {self.steptype.name: {"target": self.target.name, "vol_ml": self.volume, "rate_mh": self.flowrate, "eq_time": self.wait_time}}}}


class StepBuilder(Step):

    def __init__(self, step_name: str):
        self.step_name = step_name

    def add_type(self, type: ScreenType) -> Step:
        self.steptype = type
        return self

    def add_header(self, header: str) -> Step:
        self.header = header
        return self

    def add_description(self, description: str) -> Step:
        self.description_text = description
        return self

    def add_next_text(self, next_text: str) -> Step:
        self.next_text = next_text
        return self

    def add_actions(self, action_types: List[ActionType]) -> Step:
        
        for act in action_types:
            if "action" in self.stepdict:
                self.stepdict["action"].update(act.make_dict())
            else:
                self.stepdict["action"] = act.make_dict()

        return self

    def remove_progress_bar(self, remove: bool) -> Step:
        self.remove_progress_bar = remove
        return self

    def add_completion_msg(self, msg: str) -> Step:
        self.stepdict["completion_msg"] = msg
        return self

    def getStep(self) -> Step:
        return {self.step_name: self.stepdict}
