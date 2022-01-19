import unittest
from cd_alpha.ChipFlowApp import ProcessWindow

class SkipButtonTestCase(unittest.TestCase):

    def setUp(self):
        # import class and prepare everything here.
        self.test_window = ProcessWindow(protocol_file_name="v0-protocol-16v1.json")
        self.test_protocol_location = "v0-protocol-16v1.json"

    def test_skip_and_reschedule(self):
        pass



if __name__ == '__main__':
    unittest.main()