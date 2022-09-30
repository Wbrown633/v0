
from __future__ import annotations
import json
from typing import Dict, List
from cd_alpha.Protocol import Protocol
from pathlib import Path
from cd_alpha.Step import ScreenType, ActionType, Step, Reset
from collections import OrderedDict

class JSONProtocolParser:
    """Given json representation of a chipdx protocol, return a protocol object."""
    def __init__(self, json_filepath: Path) -> None:
        self.json_filepath = json_filepath

    def make_protocol(self, name=None) -> Protocol:
        with open(self.json_filepath, 'r') as f:
            json_dict = f.read()
        p = Protocol(self.json_filepath.stem)
        p.add_steps_from_json(json_dict)
        return p

class JSONProtocolEncoder:
    """Given a protocol object, return a legacy json representation as a string"""
    def __init__(self, protocol: Protocol) -> str:
        super.__init__(self)
        self.protocol = protocol

    def make_json_protocol(self) -> str:

        # Home step (default but needs the protocol number)

        # default init steps 

        # stuff that comes from Protocol 

        # default cleanup steps
        json_string = json.dumps(self.protocol)

        return json_string

class JSONScreenBuilder:

    def __init__(self, step_name: str) -> None:
        self.step_name = step_name
        self.stepdict = OrderedDict()

    def add_type(self, type: ScreenType):
        self.stepdict["type"] = type.name
        return self

    def add_header(self, header: str):
        self.stepdict["header"] = header
        return self

    def add_description(self, description: str):
        self.stepdict["description"] = description
        return self

    def add_next_text(self, next_text: str):
        self.stepdict["next_text"] = next_text
        return self

    def add_actions(self, action_types: List[ActionType]):
        for act in action_types:
            pass
        return self

    def getStep(self):
        return {self.step_name: self.stepdict}
    
class JSONScreenFactory:

    '''"type": "MachineActionScreen",
        "header": "Initialization",
        "description": "Initializing device. Resetting syringe positions and checking connections.",
        "action": {
            "RESET": {}
        },
        "remove_progress_bar": true,
        "completion_msg": "Machine has been homed"
        '''
    
    def __init__(self, list_of_steps: List[JSONScreenBuilder]):
        self.list_of_steps = list_of_steps

    def create_protocol(self, output_file: str):
        '''Creates and exports a json protocol at the givent file location.'''

        ## Add default steps before and after pump steps ### 
        self._add_default_steps()
        self.json_dump(output_file)

    def _add_default_steps(self):
        for step in self._define_setup_steps():
            self.list_of_steps.insert(0,step)
        for s in self._define_teardown_steps():
            self.list_of_steps.append(s)

    def _define_setup_steps(self) -> List[Step]:
   
        home_step = JSONScreenBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics")\
            .add_description("Ready for a new test with protocol 20v0. Press 'Start' to begin.").add_next_text("Start")

        reset_start_step = JSONScreenBuilder("reset_start").add_type(ScreenType.MachineActionScreen)\
            .add_header("Initialization").add_description("Initializing device. Resetting syringe positions and checking connections.")\
                .add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("Machine has been homed")

        insert_syringes_step = JSONScreenBuilder("insert_syringes").add_type(ScreenType.UserActionScreen).add_header("Insert syringes")\
            .add_description("Insert the waste and lysate syringe. Press 'Start initialization' to initialize when ready.").add_next_text("Start initialization")


        grab_syringes_step = JSONScreenBuilder("grab_syringes").add_type(ScreenType.MachineActionScreen).add_header("Grabbing syringes")\
            .add_description("The device is now grabbing hold of the syringes to secure a precise operation.").add_actions([Grab(5,0.3)]).remove_progress_bar(True).add_completion_msg("Syringes ready")


        insert_chip_step = JSONScreenBuilder("insert_chip").add_type(ScreenType.UserActionScreen).add_header("Insert Kit").add_description("Insert the chip and inlet reservoir. Press 'Next' to proceed.")
    
        step_list = [home_step, reset_start_step, insert_syringes_step, grab_syringes_step, insert_chip_step]
        step_list.reverse()
        return step_list
    
    
    def _define_teardown_steps(self) -> List[Step]:
        
        remove_kit_step = JSONScreenBuilder("remove_kit").add_type(ScreenType.UserActionScreen).add_header("Remove kit").add_description("Remove used kit from machine.")

        reset_end_step = JSONScreenBuilder("reset_end").add_type(ScreenType.MachineActionScreen).add_header("Homing device").add_description("Resetting syringe pump positions.")\
            .add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("App will restart so a new test may begin.")

        return [remove_kit_step, reset_end_step]

    def json_dump(self, file_location: str):
        with open(file_location, 'w') as f:
            steps_dictionary = {}
            for s in self.list_of_steps:
                steps_dictionary.update(s.getStep())  
            json.dump(steps_dictionary, f, indent=4)
            


if __name__ == "__main__":

    s1 = JSONScreenBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics").add_description("Ready for a new test").add_next_text("Start")
    s2 = JSONScreenBuilder("reset_start").add_type(ScreenType.MachineActionScreen).add_header("Initialization").add_description("Init device").add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("Machine has been homed")
    s3 = JSONScreenBuilder("flush_2").add_type(ScreenType.MachineActionScreen).add_header("PBS rinse").add_description("Risning the chip.").add_actions([Pump("waste", 1.05, 50, 120)])

    list_of_JSONScreenBuilders = [s1, s2, s3]

    JSONScreenFactory(list_of_JSONScreenBuilders).create_protocol("protocol_factory.json")
    
