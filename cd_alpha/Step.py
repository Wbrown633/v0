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
    material: str
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
    material: str
    time: int

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
    description: str
    list_of_actions: List[Action]

    # Material cannot be required because not all actions have materials

    # how do we handle description steps ? 
    def makejson(self):
        return {f"{self.material}_{str(self.step_number)}": {"type": self.screentype.name, "header": f"{self.material}_{str(self.step_number)}", "description": self.description_text, "action": {self.steptype.name: {"target": self.target.name, "vol_ml": self.volume, "rate_mh": self.flowrate, "eq_time": self.wait_time}}}}

