from cmath import exp
from locale import ABDAY_3
from operator import eq
from pathlib import Path
import pathlib
from tkinter import E
import pytest
import json
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import GUIModel, JSONProtocolParser, JSONProtocolEncoder, JSONScreenBuilder
from cd_alpha.Step import Grab, Incubate, Pump, Release, Reset, Step, ScreenType, ActionType


class TestProtocolEncoder:
    def setup_method(self, test_method):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"
        self.path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_step_test.json'
        self.path_21v3 = pathlib.Path.cwd() / 'cd_alpha/protocols/v0-protocol-21v3.json'
        self.multi_path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_multi_step_test.json'
        self.real_protocol = pathlib.Path.cwd() / 'cd_alpha/tests/v0-protocol-22v0.json'
    
    def test_one_step_json_encoder(self):
        p = Protocol("PBS_step")

        a = Pump(material="PBS", target="waste", vol_ml=1.0, rate_mh=15, eq_time=120)
        s = Step("PBS", [a])
        p.add_steps([s])
        g = GUIModel("100v0", {}) # for this test we don't need any gui logic
        encoder = JSONProtocolEncoder(protocol=p, guimodel=g)

        encoder.make_json_protocol_file("100v0", "pbs_step_from_encoder.json")

        with open(pathlib.Path("pbs_step_from_encoder.json"), "r") as f: 
            json_string = json.load(f)

        with open(self.path, 'r') as f:
            expected_string = json.load(f)

        
        assert json_string == expected_string

    def test_21v3_json_encoder(self):

        #TODO need a way to avoid making user screen when making pump step
        #TODO need to be able to add completion message
        p = Protocol("json_encoder_21v3.json")

        a = Pump(material="F-127", target="waste", vol_ml=0.5, rate_mh=15, eq_time=0)
        s = Step("flush_1", [a])

        a1 = Incubate("F-127", 3600)
        s1 = Step("Incubate", [a1])

        a2 = Pump(material="F-127", target="waste", vol_ml= 0.5, rate_mh= 15, eq_time=0)
        s2 = Step("flush_2", [a2])

        a3 = Pump(material="PBS", target="waste", vol_ml= 1.0, rate_mh= 15, eq_time=0)
        s3 = Step("pbs_1", [a3])

        a4 = Pump(material="Sample", target="waste", vol_ml= 0.5, rate_mh= 1.0, eq_time=0)
        s4 = Step("add_sample", [a4])

        a5 = Pump(material="PBS", target="waste", vol_ml= 0.7, rate_mh= 15.0, eq_time=0)
        s5 = Step("pbs_2", [a5])

        a6 = Pump(material="PBS", target="waste", vol_ml= 0.7, rate_mh= 15.0, eq_time=0)
        s6 = Step("pbs_3", [a6])

        a7 = Pump(material="PBS", target="waste", vol_ml= 0.7, rate_mh= 15.0, eq_time=0)
        s7 = Step("pbs_4", [a7])

        a8 = Pump(material="Qiazol", target="lysate", vol_ml= 0.2, rate_mh= 15.0, eq_time=150)
        a9 = Release(target="waste", vol_ml=1.5, rate_mh=-50, eq_time=0)
        s8 = Step("qiazol", [a8, a9])

        a10 = Pump(material="Qiazol", target="lysate", vol_ml= 1.0, rate_mh= 15.0, eq_time=0)
        s9 = Step("extract", [a10])

        p.add_steps([s, s1, s2, s3, s4, s5, s6, s7, s8, s9])

        flush_1 = JSONScreenBuilder("f127").add_type(ScreenType.UserActionScreen).add_header("Add F-127").add_description("Add 1.0 mL 1% F-127 in 1xPBS to reservoir. Press 'Next' to start.")
        flush_3 = JSONScreenBuilder("pbs_1").add_type(ScreenType.UserActionScreen).add_header("PBS rinse").add_description("Add 1 mL 1xPBS to reservoir. Press 'Next' to start.")
        flush_4 = JSONScreenBuilder("add_sample").add_type(ScreenType.UserActionScreen).add_header("Add sample").add_description("Add 0.5 mL sample to reservoir. Press 'Next' to start")
        wash_1 = JSONScreenBuilder("pbs_2").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 1").add_description("Add 700 µL 1xPBS to reservoir. Press 'Next' to start.")
        flush_5 = JSONScreenBuilder("pbs_3").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 2").add_description("Add 700 µL 1xPBS to reservoir. Press 'Next' to start.")
        flush_6 = JSONScreenBuilder("pbs_4").add_type(ScreenType.UserActionScreen).add_header("PBS Wash 3").add_description("Add 700 µL 1xPBS to reservoir. Press 'Next' to start.")
        extract_1 = JSONScreenBuilder("qiazol").add_type(ScreenType.UserActionScreen).add_header("Qiazol").add_description("Add 700 µL Qiazol to reservoir. Press 'Next' to start.")
        
        gui_dict = {"flush_1" : flush_1, "flush_3": flush_3, "flush_4": flush_4, "wash_1": wash_1,
        "flush_5": flush_5, "flush_6": flush_6, "extract_1": extract_1}
        g = GUIModel("21v3", gui_dict)
        encoder = JSONProtocolEncoder(protocol=p,guimodel=g)

        output_file = "encoder_21v3.json"

        encoder.make_json_protocol_file("200v0", output_file)

        with open(pathlib.Path(output_file), "r") as f: 
            json_string = json.load(f)

        with open(self.path_21v3, 'r') as f:
            expected_string = json.load(f)


        assert json_string == expected_string