from pathlib import Path
import pathlib
import pytest
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import JSONProtocolParser
from cd_alpha.Step import Incubate, Pump, Reset, Step, ScreenType, Action


class TestProtocol:
    def setup_method(self, test_method):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"
        self.path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_step_test.json'
        self.multi_path = pathlib.Path.cwd() / 'cd_alpha/tests/pbs_multi_step_test.json'
        self.real_protocol = pathlib.Path.cwd() / 'cd_alpha/tests/v0-protocol-22v0.json'
    
    def test_PBS_only_step(self):
        p = Protocol("pbs_step_test")
        a = Pump("PBS", "waste", 1.0, 15.0, 120)
        s = Step("Test PBS steps.", [a])
        p.add_steps([s])
        
        protocol_from_json = JSONProtocolParser(self.path).make_protocol()

        assert p == protocol_from_json

    def test_multi_step_protocol(self):

        p1 = Protocol("pbs_multi_step_test")
        a1 = Pump("PBS", "waste", 1.0, 15.0, 120)
        s1 = Step("Test PBS steps.", [a1])
        a2 = Incubate("F-127", 3600)
        s2 = Step("Blocking chip with F-127", [a2])
        a3 = Pump("Sample", "waste", 1.2, 10, 120)
        s3 = Step("Pulling sample thru chip.", [a3])

        # TODO strings are currently case sensitive, this mostly comes up in material (Sample != sample) as material

        p1.add_steps([s1,s2,s3])
        multi_step_protocol_from_json = JSONProtocolParser(self.multi_path).make_protocol()

        assert p1 == multi_step_protocol_from_json

    def test_real_protocol(self):
        # PSEUDO CODE FOR TEST 
        # Construct a list of steps that corresponds with a known valid protocol
        # Check equality with JSONProtocol Parser

        # Test with v0-protocol-22v0.json 

        # How do we handle steps that we want to ignore in our model? e.g. "home" step and 
        # other steps that are only GUI screens

        v0_22v0_protocol_from_json = JSONProtocolParser(self.real_protocol).make_protocol()

        p = Protocol("v0-protocol-22v0")
        a = Reset()
        s = Step(None, "Initializing device. Resetting syringe positions and checking connections.", [a])
        a1 = Pump("waste", 1.0, 15.0, 120)
        s1 = Step("PBS", "Test PBS steps.", [a1])
        a2 = Incubate(3600)
        s2 = Step("F-127", "Blocking chip with F-127", [a2])
        a3 = Pump("waste", 1.2, 10, 120)
        s3 = Step("Sample", "Pulling sample thru chip.", [a3])
        assert False
