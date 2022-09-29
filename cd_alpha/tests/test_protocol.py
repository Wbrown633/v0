from pathlib import Path
import pathlib
import pytest
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import JSONProtocolParser
from cd_alpha.Step import Incubate, Pump, Step, ScreenType, Action


class TestProtocol:
    def setup_method(self, test_method):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"
        self.path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_step_test.json'
        self.multi_path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_multi_step_test.json'
    
    def test_PBS_only_step(self):
        p = Protocol("pbs_step_test")
        a = Pump("waste", 1.0, 15.0, 120)
        s = Step("PBS", "Test PBS steps.", [a])
        p.add_steps([s])
        
        protocol_from_json = JSONProtocolParser(self.path).make_protocol()

        assert p == protocol_from_json

    def test_multi_step_protocol(self):

        p1 = Protocol("pbs_multi_step_test")
        a1 = Pump("waste", 1.0, 15.0, 120)
        s1 = Step("PBS", "Test PBS steps.", [a1])
        a2 = Incubate(3600)
        s2 = Step("F-127", "Blocking chip with F-127", [a2])
        a3 = Pump("waste", 1.2, 10, 120)
        s3 = Step("Sample", "Pulling sample thru chip.", [a3])

        p1.add_steps([s1,s2,s3])
        multi_step_protocol_from_json = JSONProtocolParser(self.multi_path).make_protocol()

        assert p1 == multi_step_protocol_from_json


#{
#    "home": {
#        "type": "UserActionScreen",
#        "header": "Chip Diagnostics",
#        "description": "Ready for a new test with protocol 16v1. Press 'Start' to begin.",
#        "next_text": "Start"
#    }
#}