import unittest
from cd_alpha.ChipFlowApp import ProcessWindow

class ProtocolChooserTestCase(unittest.TestCase):

    def setUp(self):
        # import class and prepare everything here.
        self.test_window = ProcessWindow()

    def test_protocol_load(self):
        # create a test window and check that all of the required screens are added
        self.test_window.load_protocol("./v0-protocol-16v1.json")


if __name__ == '__main__':
    unittest.main()