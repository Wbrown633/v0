import pytest
from cd_alpha.Protocol import Protocol
from cd_alpha.ProtocolFactory import JSONProtocolParser
from cd_alpha.Step import Pump, Step, ScreenType, Action


class TestProtocol:
    def setUp(self):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"

    
    def test_PBS_only_step(self):
        p = Protocol("test_protocol")
        a = Pump("waste", 1.0, 15.0, 120)
        s = Step("PBS", "Test PBS steps.", [a])
        p.add_steps([s])

        protocol_from_json = JSONProtocolParser("pbs_step_test.json").make_protocol()

        assert p == protocol_from_json




#{
#    "home": {
#        "type": "UserActionScreen",
#        "header": "Chip Diagnostics",
#        "description": "Ready for a new test with protocol 16v1. Press 'Start' to begin.",
#        "next_text": "Start"
#    }
#}