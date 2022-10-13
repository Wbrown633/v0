from dataclasses import dataclass
from typing import Dict, List
from abc import ABC
from enum import Enum

# TODO importing JSONScreenBuilder makes a circular import 
# from cd_alpha.ScreenBuilder import JSONScreenBuilder


class ActionType(ABC):
    def make_dict(self) -> Dict:
        return {self.__class__.__name__.upper():self.__dict__}

    def make_header(self) -> str:
        return "Add header here."

    def make_user_description(self) -> str:
        return "Type description here."


@dataclass
class Grab(ActionType):
    post_run_rate_mm: float
    post_run_vol_ml: float


@dataclass
class Release(ActionType):
    target: str
    vol_ml: float
    rate_mh: float
    eq_time: int


@dataclass
class Pump(Release):
    material: str

    def make_dict(self) -> Dict:
        '''Do not include material for json dict, legacy compatability'''
        pump_dict = super().make_dict()
        del pump_dict["PUMP"]["material"]
        return pump_dict

    def make_header(self) -> str:
        return f"Add {self.material}"

    def make_user_description(self) -> str:
        return f"Add {self.vol_ml} ml of {self.material}"


@dataclass
class Incubate(ActionType):
    material: str
    time: int

    def make_dict(self) -> Dict:
        '''Do not include material for json dict, legacy compatability'''
        dict = super().make_dict()
        del dict["INCUBATE"]["material"]
        return dict

    def make_header(self) -> str:
        return f"Add {self.material}"

@dataclass
class Reset(ActionType):
    def make_dict(self) -> Dict:
        return {"RESET": {}}


class Target(Enum):
    WASTE = 1
    LYSATE = 2

class ScreenType(Enum):
    MachineActionScreen = 1
    UserActionScreen = 2

class StepType(Enum):
    PUMP = 1
    INCUBATE = 2
    PUMPANDRELEASE = 3
    DESCRIPTION = 4

@dataclass
class Step:
    name: str
    list_of_actions: List[ActionType]

    # how do we handle description steps ?
    def make_step_name(self) -> str:
        return f"{type(self.list_of_actions[0]).__name__}"

    def makejson(self):
        return {f"{self.material}_{str(self.step_number)}": {"type": self.screentype.name, "header": f"{self.material}_{str(self.step_number)}", "description": self.description_text, "action": {self.steptype.name: {"target": self.target.name, "vol_ml": self.volume, "rate_mh": self.flowrate, "eq_time": self.wait_time}}}}

@dataclass
class HomeScren:
    type: ScreenType
    header: str
    description: str
    next_text: str

    def make_json_dict(self):
        return {"home": {"type" : self.type, "header" : self.header, "description": self.description, "next_text": self.next_text}}