
from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Dict, List
from cd_alpha.Step import ScreenType
from cd_alpha.Protocol import Protocol
from pathlib import Path
from cd_alpha.Step import ScreenType, ActionType, Step, Reset, Grab
from collections import OrderedDict
from collections.abc import Sequence

def define_setup_steps(protocol_number:str) -> list[JSONScreenBuilder]:

    home_step = JSONScreenBuilder("home").add_type(ScreenType.UserActionScreen).add_header("Chip Diagnostics")\
        .add_description(f"Ready for a new test with Small TENPO protocol {protocol_number}. Press 'Start' to begin.").add_next_text("Start")

    summary_screen = JSONScreenBuilder("summary").add_type(ScreenType.UserActionScreen).add_next_text("Start experiment")

    reset_start_step = JSONScreenBuilder("reset_start").add_type(ScreenType.MachineActionScreen)\
        .add_header("Initialization").add_description("Initializing device. Resetting syringe positions and checking connections.")\
            .add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("Machine has been homed")

    insert_syringes_step = JSONScreenBuilder("insert_syringes").add_type(ScreenType.UserActionScreen).add_header("Insert syringes")\
        .add_description("Insert the waste and lysate syringe. Press 'Start initialization' to initialize when ready.").add_next_text("Start initialization")


    grab_syringes_step = JSONScreenBuilder("grab_syringes").add_type(ScreenType.MachineActionScreen).add_header("Grabbing syringes")\
        .add_description("The device is now grabbing hold of the syringes to secure a precise operation.").add_actions([Grab(5,0.3)]).remove_progress_bar(True).add_completion_msg("Syringes ready")


    insert_chip_step = JSONScreenBuilder("insert_chip").add_type(ScreenType.UserActionScreen).add_header("Insert Kit").add_description("Insert the chip and inlet reservoir. Press 'Next' to proceed.")

    step_list = [home_step, summary_screen, reset_start_step, insert_syringes_step, grab_syringes_step, insert_chip_step]
    step_list.reverse()
    return step_list

def define_teardown_steps() -> list[JSONScreenBuilder]:
    
    remove_kit_step = JSONScreenBuilder("remove_kit").add_type(ScreenType.UserActionScreen).add_header("Remove kit").add_description("Remove used kit from machine.")

    reset_end_step = JSONScreenBuilder("reset_end").add_type(ScreenType.MachineActionScreen).add_header("Homing device").add_description("Resetting syringe pump positions.")\
        .add_actions([Reset()]).remove_progress_bar(True).add_completion_msg("App will restart so a new test may begin.")

    return [remove_kit_step, reset_end_step]
   
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
    
    def json_to_gui_model(self) -> list[JSONScreenBuilder]:
        # given a path obj to a legacy json protocol, make the gui model needed to run this protocol
        # Only care about type, header, description, and completion msg

        list_of_builders = []

        with open(self.json_filepath) as f:
            json_dict = json.load(f)
        
        for step in json_dict:
            j = JSONScreenBuilder(step)

            if "type" in step.keys():
                if step["type"] == "UserActionScreen":
                    screen_type = ScreenType.UserActionScreen
                elif step["type"] == "MachineActionScreen":
                    screen_type = ScreenType.MachineActionScreen
                else:
                    raise KeyError(f"Invalid screen type in {step}")
                j.add_type(screen_type)

            elif "header" in step.keys():
                j.add_header(step["header"])

            elif "description" in step.keys():
                j.add_description(step["description"])

            elif "completion_msg" in step.keys():
                j.add_completion_msg(step["completion_msg"])

            list_of_builders.append(j)

        return list_of_builders   
            

@dataclass
class GUIModel:
    """Class to contain all GUI specific logic. Including user instruction screens"""
    protocol_number: str
    instruction_screens_dict: dict[str, JSONScreenBuilder]
    # TODO could just update this to be its own class of JSONScreenbuilder called UpdateJSONScreenBuilder
    # that inherits from screenbuilder and takes in the name of the step to update
    step_updates_dict: dict[str, JSONScreenBuilder] = None
    start_steps: list[JSONScreenBuilder] = None
    shutdown_steps: list[JSONScreenBuilder] = None

    # TODO need to be able to change header and description, along with completion msg
    def __post_init__(self):
        if self.start_steps == None:
            self.start_steps = define_setup_steps(self.protocol_number)

        if self.shutdown_steps == None:
            self.shutdown_steps = define_teardown_steps

 

class JSONProtocolEncoder:
    """Given a protocol object, return a legacy json representation as a string"""
    def __init__(self, protocol: Protocol, guimodel: GUIModel) -> str:
        super().__init__()
        self.protocol = protocol
        self.guimodel = guimodel

    def make_json_protocol_file(self, protocol_number: str, output_file_path: str):
        #TODO how to handle GUI specific settings/logic
        # such as user instructions and completion messages? 
        screen_builder_from_protocol = self.make_screen_builders_from_protocol()
        fac = JSONScreenFactory(protocol_number=protocol_number,list_of_screen_builder=screen_builder_from_protocol)
        fac.create_protocol(output_file=output_file_path)

    def make_screen_builders_from_protocol(self) -> list[JSONScreenBuilder]:

        list_of_screen_builders = []
        for step in self.protocol.list_of_steps:
            first_action_in_list = step.list_of_actions[0]

            # Check if this step needs an instruction screen
            # if it does, put it in before we add the model step
            # also check if we need to update the default settings for 
            # each model step
            if step.name in self.guimodel.instruction_screens_dict:
                list_of_screen_builders.append(self.guimodel.instruction_screens_dict[step.name])

            step_header = first_action_in_list.make_header()
            step_description = first_action_in_list.make_user_description()
            step_completion = None

            updates_dict = self.guimodel.step_updates_dict
            if updates_dict is not None and step.name in updates_dict:
                if "header" in updates_dict[step.name].stepdict:
                    step_header = updates_dict[step.name].stepdict["header"]
                if "description" in updates_dict[step.name].stepdict:
                    step_description = updates_dict[step.name].stepdict["description"]
                if "completion_msg" in updates_dict[step.name].stepdict:
                    step_completion = updates_dict[step.name].stepdict["completion_msg"]
            
            screen = JSONScreenBuilder(step.name).add_type(ScreenType.MachineActionScreen).add_header(step_header).add_description(step_description).add_actions(step.list_of_actions)
            if step_completion is not None:
                screen.add_completion_msg(step_completion)
                
            list_of_screen_builders.append(screen)

        return list_of_screen_builders

class JSONScreenBuilder:
    """Utility class to make construction legacy JSON protocols easier."""

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
    """Given a list of JSONScreenBuilders, construct a legacy JSON protocol."""
    
    def __init__(self, protocol_number: str, list_of_screen_builder: List[JSONScreenBuilder], guimodel: GUIModel = None):
        self.protocol_number = protocol_number
        self.list_of_screenbuilder = list_of_screen_builder

    def create_protocol(self, output_file: str):
        '''Creates and exports a json protocol at the givent file location.'''

        ## Add default steps before and after pump steps ### 
        self._add_default_steps()
        self.json_dump(output_file)

    def _add_default_steps(self):
        for step in define_setup_steps(self.protocol_number):
            self.list_of_screenbuilder.insert(0,step)
        for s in define_teardown_steps():
            self.list_of_screenbuilder.append(s)
    


    def json_to_str(self) -> str:
        steps_dictionary = {}
        for s in self.list_of_screenbuilder:
                steps_dictionary.update(s.getStep())  
        json.dumps(steps_dictionary, indent=4)

    def json_dump(self, file_location: str):
        with open(file_location, 'w') as f:
            steps_dictionary = {}
            for screen in self.list_of_screenbuilder:
                steps_dictionary.update(screen.getStep())  
            json.dump(steps_dictionary, f, indent=4)

   
