import unittest
from cd_alpha.ChipFlowApp import ProcessWindow

class ProtocolChooserTestCase(unittest.TestCase):

    def setUp(self):
        # import class and prepare everything here.
        self.test_window = ProcessWindow()

    # Test a standard protocol load, make sure all steps are present and in the right order
    def test_protocol_load(self):
        # create a test window and check that all of the required screens are added
        self.test_window.load_protocol("./v0-protocol-16v1.json")
        self.assertEqual(len(self.test_window.process_sm.screens), 16)

    # Test that loading protocols multiple times in a row doesn't cause duplicate steps

    # Test that loading an invalid file raises a non fatal error


if __name__ == '__main__':
    unittest.main()