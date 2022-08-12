import unittest
from cd_alpha.ChipFlowApp import ProcessWindow


class ProtocolChooserTestCase(unittest.TestCase):
    def setUp(self):
        # import class and prepare everything here.
        self.test_window = ProcessWindow(protocol_file_name="v0-protocol-16v1.json")
        self.test_protocol_location = "v0-protocol-16v1.json"

    # Test a standard protocol load, make sure all steps are present and in the right order
    def test_protocol_load_basic(self):
        # create a test window and check that all of the required screens are added
        self.test_window.load_protocol(self.test_protocol_location)

        # For 16v1 there should be 35 screens. {'protocol_chooser': 1, 'home': 1, 'reset_start': 1, 'reset_start_done': 1,
        # 'insert_syringes': 1, 'grab_syringes': 1, 'grab_syringes_done': 1, 'insert_chip': 1, 'f127': 1, 'flush_1': 1,
        # 'incubate_1': 1, 'incubate_1_done': 1, 'pbs_1': 1, 'flush_2': 1, 'flush_2_done': 1, 'add_sample': 1, 'flush_3': 1,
        # 'flush_3_done': 1, 'pbs_2': 1, 'wash_1': 1, 'wash_1_done': 1, 'pbs_3': 1, 'flush_5': 1, 'flush_5_done': 1, 'pbs_4': 1,
        # 'flush_6': 1, 'flush_6_done': 1, 'qiazol': 1, 'extract_1': 1, 'extract_1_done': 1, 'PBSchase': 1, 'chase_1': 1,
        # 'remove_kit': 1, 'reset_end': 1, 'reset_end_done': 1}
        self.assertEqual(len(self.test_window.process_sm.screens), 35)

        # Check that there are no duplicate steps
        self.assertFalse(
            self._find_duplicates(self.test_window.process_sm.screen_names)
        )

    # Test that loading protocols multiple times in a row doesn't cause duplicate steps
    def test_protocol_load_multiple(self):
        # create a test window and check that all of the required screens are added
        self.test_window.load_protocol(self.test_protocol_location)

        # Load the same protocol multiple times in a row to make sure there are no
        # duplicate steps
        for x in range(5):
            self.test_window.load_protocol(self.test_protocol_location)

        self.assertFalse(
            self._find_duplicates(self.test_window.process_sm.screen_names)
        )

    # Test that loading an invalid file raises an error
    def test_load_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            self.test_window.load_protocol("foobar.json")

    # Test that loading an invalid protocol raises an error
    def test_load_invalid_protocol(self):
        with self.assertRaises(TypeError):
            self.test_window.load_protocol("invalid_protocol.json")

    def _find_duplicates(self, list_of_values):
        # Check that there are no duplicate steps
        for value in list_of_values:
            if self.test_window.process_sm.screen_names.count(value) > 1:
                return True
        return False


if __name__ == "__main__":
    unittest.main()
