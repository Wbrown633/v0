from cd_alpha.Step import Step
import json
from types import SimpleNamespace
from typing import List

class Protocol:
    def __init__(self, name: str) -> None:
        self.list_of_steps = []
        self.name = name
    
    def add_steps(self, list_of_steps: List[Step]):
        self.list_of_steps.extend(list_of_steps)

    def add_step_from_json(self, json_data: str):
        x = json.loads(json_data, object_hook=lambda d: SimpleNamespace(**d))
        self.list_of_steps.append(x)

    def remove_step(self):
        pass

    def edit_step(self):
        pass
