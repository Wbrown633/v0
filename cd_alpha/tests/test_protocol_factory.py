
from typing import List
import unittest
from collections import OrderedDict

from pkg_resources import resource_filename
from cd_alpha.ProtocolFactory import ProtocolFactory, ScreenType, Step, StepBuilder
import json


class ProtocolFactoryTestCase(unittest.TestCase):

    def setUp(self):
        # import class and prepare everything here.
        pass
        

    def test_protocol_factory_20v0(self):
        test_file = resource_filename("cd_alpha", "protocols/v0-protocol-20v0.json")

        with open(test_file, 'r') as f:
            protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)


        # PSEUDO CODE 
        # make the list of steps needed to replicate protocol 20v0 using the Protocol factory method

        list_of_steps = self.protocol_factory_make_20v0()

        ProtocolFactory(list_of_steps).create_protocol("test.json")

        with open("test.json", 'r') as f:
            test_protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        self.assertEqual(protocol, test_protocol)

    def protocol_factory_make_20v0() -> List[StepBuilder]:
        f127 = StepBuilder("f127").add_type(ScreenType.UserActionScreen).add_header("Add F-127")\
            .add_description("Add 1.4 mL 1% F-127 in 1xPBS to reservoir. Press 'Next' to start.")
        
        flush_1 = StepBuilder("flush_1")

        incubate_1 = StepBuilder("incubate_1")

        pbs_1 = StepBuilder("pbs_1")

        flush_2 = StepBuilder("flush_2")

        add_sample = StepBuilder("add_sample")

        flush_3 = StepBuilder("flush_3")

        pbs_2 = StepBuilder("pbs_2")

        wash_1 = StepBuilder("wash_1")

        pbs_3 = StepBuilder("pbs_3")

        flush_5 = StepBuilder("flush_5")

        flush_6 = StepBuilder("flush_6")

        pbs_4 = StepBuilder("pbs_4")

        flush_7 = StepBuilder("flush_7")

        qiazol = StepBuilder("qiazol")

        extract_1 = StepBuilder("extract_1")

        extract_2 = StepBuilder("extract_2")

        PBSchase = StepBuilder("PBSchase")

        chase_1 = StepBuilder("chase_1")



        





if __name__ == '__main__':
    unittest.main()