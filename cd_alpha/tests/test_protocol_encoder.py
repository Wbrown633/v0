from pathlib import Path
import pathlib
import pytest
import json
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import JSONProtocolParser, JSONProtocolEncoder
from cd_alpha.Step import Grab, Incubate, Pump, Release, Reset, Step, ScreenType, Action


class TestProtocolEncoder:
    def setup_method(self, test_method):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"
        self.path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_step_test.json'
        self.multi_path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_multi_step_test.json'
        self.real_protocol = pathlib.Path.cwd() / 'cd_alpha/tests/v0-protocol-22v0.json'
    
    def test_one_step_json_encoder(self):
        p = Protocol("PBS_step")

        a = Pump()
        encoder = JSONProtocolEncoder(p)

        json_string = encoder.make_json_protocol()

        expected_string = json.load()
        assert False