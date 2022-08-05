
import unittest
from collections import OrderedDict

from pkg_resources import resource_filename
from cd_alpha.ProtocolFactory import ProtocolFactory, StepBuilder
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

        list_of_steps = [StepBuilder("test").getStep()]

        ProtocolFactory(list_of_steps).create_protocol("test.json")

        with open("test.json", 'r') as f:
            test_protocol = json.loads(f.read(), object_pairs_hook=OrderedDict)

        self.assertEqual(protocol, test_protocol)





if __name__ == '__main__':
    unittest.main()