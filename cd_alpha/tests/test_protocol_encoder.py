from pathlib import Path
import pathlib
import pytest
import json
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import JSONProtocolParser, JSONProtocolEncoder
from cd_alpha.Step import Grab, Incubate, Pump, Release, Reset, Step, ScreenType, ActionType


class TestProtocolEncoder:
    def setup_method(self, test_method):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"
        self.path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_step_test.json'
        self.multi_path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_multi_step_test.json'
        self.real_protocol = pathlib.Path.cwd() / 'cd_alpha/tests/v0-protocol-22v0.json'
    
    def test_one_step_json_encoder(self):
        p = Protocol("PBS_step")

        a = Pump(material="PBS", target="waste", vol_ml=1.0, rate_mh=15, eq_time=120)
        s = Step("Test PBS steps.", [a])
        p.add_steps([s])
        encoder = JSONProtocolEncoder(p)

        encoder.make_json_protocol_file("pbs_step_from_encoder.json")

        with open(pathlib.Path("pbs_step_from_encoder.json"), "r") as f: 
            json_string = json.load(f)

        with open(self.path, 'r') as f:
            expected_string = json.load(f)

        
        assert json_string == expected_string