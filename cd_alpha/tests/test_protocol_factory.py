from typing import List
import pytest
from collections import OrderedDict
from cd_alpha.Step import ScreenType, Pump, Incubate, Release, Reset
from cd_alpha.ProtocolFactory import JSONProtocolParser, JSONScreenFactory, JSONScreenBuilder
from pkg_resources import resource_filename
import json
from pathlib import Path

class TestJSONScreenFactory():

    def setup_method(self, test_method):
        # import class and prepare everything here.
        self.gui_file_path = Path.cwd() / 'cd_alpha/tests/v0-protocol-22v0.json'
        

    def test_protocol_factory_20v0(self):
        # TODO tests should probably be updated to make use of guimodels for default steps
        test_file = resource_filename("cd_alpha", "protocols/v0-protocol-20v0.json")

        with open(test_file, 'r') as f:
            protocol_20v0 = json.loads(f.read(), object_pairs_hook=OrderedDict)

        list_of_steps = self.protocol_factory_make_20v0()

        protocol_number = "20v0"

        test_output_location = f"test_{protocol_number}.json"

        JSONScreenFactory(protocol_number=protocol_number,list_of_screen_builder=list_of_steps).create_protocol(test_output_location)

        with open(test_output_location, 'r') as f:
            result_from_factory = json.loads(f.read(), object_pairs_hook=OrderedDict)

        assert protocol_20v0 == result_from_factory

    def test_screen_builder_single_step(self):
        
        # test that the screen builder can produce valid json for a single step

        test_file = resource_filename("cd_alpha", "tests/pbs_step_test.json")
        
        with open(test_file, "r") as f:
            expected_json_dict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        
        json_from_builder = JSONScreenBuilder("PBS").add_type(ScreenType.MachineActionScreen).add_header("PBS pull").add_description("Test PBS steps.").add_actions([Pump(material="PBS", target="waste", vol_ml=1.0, rate_mh=15.0, eq_time=120)]).getStep()
        assert expected_json_dict == json_from_builder

    def test_gui_screenbuilder_list(self):
        list_of_screenbuilder = JSONProtocolParser(self.gui_file_path).json_to_gui_model()
        print(list_of_screenbuilder)
        assert False

    def protocol_factory_make_20v0(self) -> List[JSONScreenBuilder]:
        f127 = JSONScreenBuilder("f127").add_type(ScreenType.UserActionScreen).add_header("Add F-127")\
            .add_description("Add 1.4 mL 1% F-127 in 1xPBS to reservoir. Press 'Next' to start.")
        
        flush_1 = JSONScreenBuilder("flush_1").add_type(ScreenType.MachineActionScreen).add_header("F-127 pull").add_description("Wetting the chip with F-127").add_actions([Pump(material="F-127", target="waste", vol_ml=1, rate_mh=50, eq_time=1)])

        incubate_1 = JSONScreenBuilder("incubate_1").add_type(ScreenType.MachineActionScreen).add_header("Blocking").add_description("Blocking chip with F-127").add_actions([Incubate(material="F-127", time=3600)]).add_completion_msg("F-127 blocking finished.")

        pbs_1 = JSONScreenBuilder("pbs_1").add_type(ScreenType.UserActionScreen).add_header("PBS rinse").add_description("Add 1 mL 1xPBS to reservoir. Press 'Next' to start.")

        flush_2 = JSONScreenBuilder("flush_2").add_type(ScreenType.MachineActionScreen).add_header("PBS rinse").add_description("Rinsing the chip.").add_actions([Pump(material="PBS", target="waste", vol_ml=1.05, rate_mh=50, eq_time=120)]).add_completion_msg("PBS rinse complete")

        add_sample = JSONScreenBuilder("add_sample").add_type(ScreenType.UserActionScreen).add_header("Add sample").add_description("Add 1 mL sample to reservoir. Press 'Next' to start")

        flush_3 = JSONScreenBuilder("flush_3").add_type(ScreenType.MachineActionScreen).add_header("Sample pull").add_description("Pulling sample thru chip.").add_actions([Pump(material="Sample", target="waste", vol_ml=1.2, rate_mh=10, eq_time=120)]).add_completion_msg("Sample pull completed")

        pbs_2 = JSONScreenBuilder("pbs_2").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 1").add_description("Add 400 µL 1xPBS to reservoir. Press 'Next' to start.")

        wash_1 = JSONScreenBuilder("wash_1").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 1").add_description("Washing the chip.").add_actions([Pump(material="PBS", target="waste", vol_ml=0.2, rate_mh=10, eq_time=120)]).add_completion_msg("Wash 1 complete")

        pbs_3 = JSONScreenBuilder("pbs_3").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 2").add_description("Add 800 µL 1xPBS to reservoir. Press 'Next' to start.")

        flush_5 = JSONScreenBuilder("flush_5").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 2").add_description("Washing the chip.").add_actions([Pump(material="PBS", target="waste", vol_ml=0.4, rate_mh=10, eq_time=120)]).add_completion_msg("Wash 2 complete")

        flush_6 = JSONScreenBuilder("flush_6").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 2 Part 2").add_description("Washing the chip.").add_actions([Pump(material="PBS",target="waste", vol_ml=0.4, rate_mh=50, eq_time=120)]).add_completion_msg("Wash 2 complete")

        pbs_4 = JSONScreenBuilder("pbs_4").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 3").add_description("Add 1000 µL 1xPBS to reservoir. Press 'Next' to start.")

        flush_7 = JSONScreenBuilder("flush_7").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 3").add_description("Washing the chip.").add_actions([Pump(material="PBS", target="waste", vol_ml=1.2, rate_mh=50, eq_time=120)]).add_completion_msg("Wash 3 complete")

        qiazol = JSONScreenBuilder("qiazol").add_type(ScreenType.UserActionScreen).add_header("Qiazol").add_description("Add 700 µL Qiazol to reservoir. Press 'Next' to start.")

        extract_1 = JSONScreenBuilder("extract_1").add_type(ScreenType.MachineActionScreen).add_header("Qiazol 1").add_description("Pulling Qiazol into chip.").add_actions([Pump(material="Qiazol", target="waste", vol_ml=0.5, rate_mh=10, eq_time=0)]).add_completion_msg("Qiazol pull to waste complete")

        extract_2 = JSONScreenBuilder("extract_2").add_type(ScreenType.MachineActionScreen).add_header("Qiazol 2").add_description("Pulling Qiazol into chip.").add_actions([Pump(material="Qiazol", target="lysate", vol_ml=0.2, rate_mh=10, eq_time=0), Release(target="waste", vol_ml=1.5, rate_mh=-50, eq_time=0)]).add_completion_msg("Qiazol pull and incubation complete")

        PBSchase = JSONScreenBuilder("PBSchase").add_type(ScreenType.UserActionScreen).add_header("PBS Chase").add_description("Add 1 mL PBS to reservoir. Press 'Next' to start.")

        chase_1 = JSONScreenBuilder("chase_1").add_type(ScreenType.MachineActionScreen).add_header("PBS Chase").add_description("Extracting lysate from chip.").add_actions([Pump(material="PBS", target="lysate", vol_ml=0.7, rate_mh=15, eq_time=120)])

        return [f127, flush_1, incubate_1, pbs_1, flush_2, add_sample, flush_3, pbs_2,
        wash_1, pbs_3, flush_5, flush_6, pbs_4, flush_7, qiazol, extract_1, extract_2, 
        PBSchase, chase_1]
