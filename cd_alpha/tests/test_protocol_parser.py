import pytest
from cd_alpha.Protocol import Protocol
from cd_alpha.Step import Step


class TestProtocolParser:
    def setUp(self):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"

    def test_protocol_home_step(self):
        p = Protocol("home_test")
        p.add_step_from_json("home_step.json")
        test_step = p.list_of_steps[0]
        expected_step = Step()

