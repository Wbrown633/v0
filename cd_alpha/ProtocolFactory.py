
from __future__ import annotations
import json
from tkinter import Scrollbar
from turtle import st
from typing import Dict, List
from cd_alpha.Protocol import Protocol
from pathlib import Path
from cd_alpha.Step import ScreenType, ActionType, Step, Reset, Grab
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
        super().__init__()
        self.protocol = protocol

    def make_json_protocol_file(self, protocol_number: str, output_file_path: str):

        # Home step (default but needs the protocol number)

        # default init steps 

        # stuff that comes from Protocol 
        

        # how do we handle User action screens?? 

        # default cleanup steps
        screen_builder_from_protocol = self.make_screen_builders_from_protocol()
        fac = JSONScreenFactory(protocol_number=protocol_number,list_of_screen_builder=screen_builder_from_protocol)
        fac.create_protocol(output_file=output_file_path)

    def make_screen_builders_from_protocol(self) -> List[JSONScreenBuilder]:

        # TODO need way to add extra screens that aren't captured by the protocol
        # such as the user instruction screens 
        # Add all of the steps that are in the protocol
        list_of_screen_builders = []
        for step in self.protocol.list_of_steps:
            # If the ActionType is PUMP, add a user action screen, except for some cases
            # For legacy protocols we never have a situation where PUMP isn't first in the action list 
            first_action_in_list = step.list_of_actions[0]
            if type(first_action_in_list).__name__ == "Pump":
                s = JSONScreenBuilder(step.material + "_1").add_type(ScreenType.UserActionScreen).add_header(first_action_in_list.make_header()).add_description(first_action_in_list.make_user_description())
                list_of_screen_builders.append(s)
            screen = JSONScreenBuilder(step.make_step_name()).add_type(ScreenType.MachineActionScreen).add_header(first_action_in_list.make_header()).add_description(step.description).add_actions(step.list_of_actions)
            list_of_screen_builders.append(screen)

        return list_of_screen_builders

class JSONScreenBuilder:

    def __init__(self, step_name: str) -> None:
        self.step_name = step_name
        self.stepdict = OrderedDict()

    # TODO can add methods be programatically created? they all are basically the same 
    def add_type(self, type: ScreenType) -> JSONScreenBuilder:
        self.stepdict["type"] = type.name
        return self

    def add_header(self, header: str) -> JSONScreenBuilder:
        self.stepdict["header"] = header
        return self

    def add_description(self, description: str) -> JSONScreenBuilder:
        self.stepdict["description"] = description
        return self

    def add_next_text(self, next_text: str) -> JSONScreenBuilder:
        self.stepdict["next_text"] = next_text
        return self

    def add_actions(self, action_types: List[ActionType]) -> JSONScreenBuilder:
        act_dict = {}
        for act in action_types:
            act_dict.update(act.make_dict())

        self.stepdict["action"] = act_dict
        return self

    def add_completion_msg(self, completion_msg) -> JSONScreenBuilder:
        self.stepdict["completion_msg"] = completion_msg
        return self

    def remove_progress_bar(self, bool) -> JSONScreenBuilder:
        self.stepdict["remove_progress_bar"] = bool
        return self

    def getStep(self) -> Dict:
        return {self.step_name: self.stepdict}

  
class JSONScreenFactory:
    
    def __init__(self, protocol_number: str, list_of_screen_builder: List[JSONScreenBuilder]):
        self.protocol_number = protocol_number
        self.list_of_screenbuilder = list_of_screen_builder

    def create_protocol(self, output_file: str):
        '''Creates and exports a json protocol at the givent file location.'''

        ## Add default steps before and after pump steps ### 
        self._add_default_steps()
        self.json_dump(output_file)

    def _add_default_steps(self):
        for step in self._define_setup_steps():
            self.list_of_screenbuilder.insert(0,step)
        for s in self._define_teardown_steps():
            self.list_of_screenbuilder.append(s)

    def _define_setup_steps(self) -> List[Step]:
   
        home_step = JSONScreenBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics")\
            .add_description(f"Ready for a new test with protocol {self.protocol_number}. Press 'Start' to begin.").add_next_text("Start")

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

    def json_to_str(self) -> str:
        steps_dictionary = {}
        for s in self.list_of_screenbuilder:
                steps_dictionary.update(s.getStep())  
        json.dumps(steps_dictionary, indent=4)

    def json_dump(self, file_location: str):
        with open(file_location, 'w') as f:
            steps_dictionary = {}
            repeat_steps = 1
            for screen in self.list_of_screenbuilder:
                screen_step_dict = screen.getStep() # don't overwrite value 
                steps_dictionary.update(screen.getStep())  
            json.dump(steps_dictionary, f, indent=4)
            
