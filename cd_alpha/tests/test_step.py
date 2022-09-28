import pytest
from cd_alpha.Protocol import Protocol
from cd_alpha.Step import Step, ScreenType


class TestStep:
    def setUp(self):
        # import class and prepare everything here.
        self.test_protocol_location = "v0-protocol-16v1.json"

    def test_protocol_home_step(self):
        p = Protocol("home_test")
        p.add_step_from_json("home_step.json")
        test_step = p.list_of_steps[0]
        expected_step = Step(type= ScreenType.UserActionScreen, 
            header="Chip Diagnostics",
            description_text="Ready for a new test with protocol 16v1. Press 'Start' to begin.",
            next_text="Start"
        )



#{
#    "home": {
#        "type": "UserActionScreen",
#        "header": "Chip Diagnostics",
#        "description": "Ready for a new test with protocol 16v1. Press 'Start' to begin.",
#        "next_text": "Start"
#    }
#}