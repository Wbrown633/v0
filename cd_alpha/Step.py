from dataclasses import dataclass
from typing import Dict, List


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
        return {f"{self.material}_{str(self.step_number)}": {"type": self.screentype.name, "header": f"{self.material}_{str(self.step_number)}", "description": self.description_text, "action": {self.steptype.name: {"target": self.target.name, "vol_ml": self.volume, "rate_mh": self.flowrate, "eq_time": self.wait_time}}}}


class StepBuilder:

    def __init__(self, step_name: str):
        self.step_name = step_name

    def add_type(self, type: ScreenType) -> Step:
        self.stepdict["type"] = type.name
        return self

    def add_header(self, header: str) -> Step:
        self.stepdict["header"] = header
        return self

    def add_description(self, description: str) -> Step:
        self.stepdict["description"] = description
        return self

    def add_next_text(self, next_text: str) -> Step:
        self.stepdict["next_text"] = next_text
        return self

    def add_actions(self, action_types: List[ActionType]) -> Step:
        
        for act in action_types:
            if "action" in self.stepdict:
                self.stepdict["action"].update(act.make_dict())
            else:
                self.stepdict["action"] = act.make_dict()

        return self

    def remove_progress_bar(self, remove: bool) -> Step:
        self.stepdict["remove_progress_bar"] = remove
        return self

    def add_completion_msg(self, msg: str) -> Step:
        self.stepdict["completion_msg"] = msg
        return self

    def getStep(self) -> Step:
        return {self.step_name: self.stepdict}
