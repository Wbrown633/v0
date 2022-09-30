from multiprocessing.sharedctypes import Value
from tabnanny import check
from cd_alpha.Step import Grab, Incubate, Pump, Release, Reset, Step
import json
from typing import Dict, List

class Protocol:
    def __init__(self, name: str) -> None:
        self.list_of_steps = []
        self.name = name
        self.POSSIBLE_MATERIALS = ["PBS", "F-127", "Sample", "RIPA", "Qiazol"] # TODO This should probably be an Enum, CASE SENSITIVE in tests
    
    def __eq__(self, __o: object) -> bool:
        return __o.name == self.name and self.list_of_steps == __o.list_of_steps

    def __repr__(self) -> str:
        return f"{self.name}:{self.list_of_steps}"
    
    def add_steps(self, list_of_steps: List[Step]):
        self.list_of_steps.extend(list_of_steps)

    def add_steps_from_json(self, json_data: str):
        json_data = json.loads(json_data) 
        list_of_steps_from_json = self.custom_json_parser(json_data)
        self.list_of_steps.extend(list_of_steps_from_json)

    def custom_json_parser(self, json_dict: dict) -> List[Step]:
        # Could almost certainly be done cleaner with an object_hook in the json.loads() method but
        # I needed to get something working fast
        list_of_steps = []
        material = None
        check_material = False
        action_list = []
        for k in json_dict.keys():
            for k1 in json_dict[k].keys():
                if k1 == "description":
                    step_description = json_dict[k][k1]
                # Currently only used to find material
                if k1 == "header":
                    step_header = json_dict[k][k1]
                if k1 == "action":
                    action_list = []
                    for k2 in json_dict[k][k1].keys():
                        action_step_dict = json_dict[k][k1][k2]
                        if k2 == "PUMP":
                            material = self._get_material_from_header_or_desc(step_description, step_header)
                            step_action = Pump(material, action_step_dict["target"],
                            action_step_dict["vol_ml"], action_step_dict["rate_mh"], action_step_dict["eq_time"])
                        elif k2 == "GRAB":
                            step_action = Grab(action_step_dict["post_run_rate_mm"], action_step_dict["post_run_vol_ml"])
                        elif k2 == "RELEASE":
                            step_action = Release(action_step_dict["target"],
                            action_step_dict["vol_ml"], action_step_dict["rate_mh"], action_step_dict["eq_time"])
                        elif k2 == "INCUBATE":
                            material = self._get_material_from_header_or_desc(step_description, step_header)
                            step_action = Incubate(material, action_step_dict["time"])
                        elif k2 == "RESET":
                            step_action = Reset()
                        else:
                            raise ValueError(f"Invalid Action value in dict {k2}, not one of [PUMP, GRAB, RELEASE, INCUBATE, RESET]")
                        action_list.append(step_action)
            if len(action_list) > 0:
                s = Step(step_description, action_list)
                list_of_steps.append(s)
            action_list = []
        
        return list_of_steps

    def _get_material_from_header_or_desc(self, desc: str, header: str) -> str:
        for mat in self.POSSIBLE_MATERIALS:
            mat_upper = mat.upper()
            header_upper = header.upper()
            desc_upper = desc.upper()
            if mat_upper in header_upper:
                return mat
            if mat_upper in desc_upper:
                return mat

        raise ValueError(f"Valid material not found in the provided description string. None of {self.POSSIBLE_MATERIALS} found in string {desc}")

    def remove_step(self):
        pass

    def edit_step(self):
        pass
