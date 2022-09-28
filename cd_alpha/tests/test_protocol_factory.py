
from deepdiff import DeepDiff
from typing import List
import pytest
from collections import OrderedDict

from pkg_resources import resource_filename
from cd_alpha.ProtocolFactory import Incubate, ProtocolFactory, Pump, Release, ScreenType, Step, StepBuilder
import json

# TODO everything should be using pytest moving forward
class TestProtocolFactory():

    def setUp(self):
        # import class and prepare everything here.
        pass
        

    def test_protocol_factory_20v0(self):
        test_file = resource_filename("cd_alpha", "protocols/v0-protocol-20v0.json")

        with open(test_file, 'r') as f:
            protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)


        # PSEUDO CODE 
        # make the list of steps needed to replicate protocol 20v0 using the Protocol factory method

        list_of_steps = self.protocol_factory_make_20v0()

        ProtocolFactory(list_of_steps).create_protocol("test.json")

        with open("test.json", 'r') as f:
            test_protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        print(DeepDiff(protocol, test_protocol, ignore_order=False))
        self.assertEqual(protocol, test_protocol)

    def protocol_factory_make_20v0(self) -> List[StepBuilder]:
        f127 = StepBuilder("f127").add_type(ScreenType.UserActionScreen).add_header("Add F-127")\
            .add_description("Add 1.4 mL 1% F-127 in 1xPBS to reservoir. Press 'Next' to start.")
        
        flush_1 = StepBuilder("flush_1").add_type(ScreenType.MachineActionScreen).add_header("F-127 pull").add_description("Wetting the chip with F-127").add_actions([Pump("waste", 1, 50, 1)])

        incubate_1 = StepBuilder("incubate_1").add_type(ScreenType.MachineActionScreen).add_header("Blocking").add_description("Blocking chip with F-127").add_actions([Incubate(3600)]).add_completion_msg("F-127 blocking finished.")

        pbs_1 = StepBuilder("pbs_1").add_type(ScreenType.UserActionScreen).add_header("PBS rinse").add_description("Add 1 mL 1xPBS to reservoir. Press 'Next' to start.")

        flush_2 = StepBuilder("flush_2").add_type(ScreenType.MachineActionScreen).add_header("PBS rinse").add_description("Rinsing the chip.").add_actions([Pump("waste", 1.05, 50, 120)]).add_completion_msg("PBS rinse complete")

        add_sample = StepBuilder("add_sample").add_type(ScreenType.UserActionScreen).add_header("Add sample").add_description("Add 1 mL sample to reservoir. Press 'Next' to start")

        flush_3 = StepBuilder("flush_3").add_type(ScreenType.MachineActionScreen).add_header("Sample pull").add_description("Pulling sample thru chip.").add_actions([Pump("waste", 1.2, 10, 120)]).add_completion_msg("Sample pull completed")

        pbs_2 = StepBuilder("pbs_2").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 1").add_description("Add 400 µL 1xPBS to reservoir. Press 'Next' to start.")

        wash_1 = StepBuilder("wash_1").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 1").add_description("Washing the chip.").add_actions([Pump("waste", 0.2, 10, 120)]).add_completion_msg("Wash 1 complete")

        pbs_3 = StepBuilder("pbs_3").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 2").add_description("Add 800 µL 1xPBS to reservoir. Press 'Next' to start.")

        flush_5 = StepBuilder("flush_5").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 2").add_description("Washing the chip.").add_actions([Pump("waste", 0.4, 10, 120)]).add_completion_msg("Wash 2 complete")

        flush_6 = StepBuilder("flush_6").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 2 Part 2").add_description("Washing the chip.").add_actions([Pump("waste", 0.4, 50, 120)]).add_completion_msg("Wash 2 complete")

        pbs_4 = StepBuilder("pbs_4").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 3").add_description("Add 1000 µL 1xPBS to reservoir. Press 'Next' to start.")

        flush_7 = StepBuilder("flush_7").add_type(ScreenType.MachineActionScreen).add_header("PBS Wash 3").add_description("Washing the chip.").add_actions([Pump("waste", 1.2, 50, 120)]).add_completion_msg("Wash 3 complete")

        qiazol = StepBuilder("qiazol").add_type(ScreenType.UserActionScreen).add_header("Qiazol").add_description("Add 700 µL Qiazol to reservoir. Press 'Next' to start.")

        extract_1 = StepBuilder("extract_1").add_type(ScreenType.MachineActionScreen).add_header("Qiazol 1").add_description("Pulling Qiazol into chip.").add_actions([Pump("waste", 0.5, 10, 0)]).add_completion_msg("Qiazol pull to waste complete")

        extract_2 = StepBuilder("extract_2").add_type(ScreenType.MachineActionScreen).add_header("Qiazol 2").add_description("Pulling Qiazol into chip.").add_actions([Pump("lysate", 0.2, 10, 0), Release("waste", 1.5, -50, 0)]).add_completion_msg("Qiazol pull and incubation complete")

        PBSchase = StepBuilder("PBSchase").add_type(ScreenType.UserActionScreen).add_header("PBS Chase").add_description("Add 1 mL PBS to reservoir. Press 'Next' to start.")

        chase_1 = StepBuilder("chase_1").add_type(ScreenType.MachineActionScreen).add_header("PBS Chase").add_description("Extracting lysate from chip.").add_actions([Pump("lysate", 0.7, 15, 120)])

        return [f127, flush_1, incubate_1, pbs_1, flush_2, add_sample, flush_3, pbs_2,
        wash_1, pbs_3, flush_5, flush_6, pbs_4, flush_7, qiazol, extract_1, extract_2, 
        PBSchase, chase_1]
