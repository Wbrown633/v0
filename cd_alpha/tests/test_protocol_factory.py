
from deepdiff import DeepDiff
from typing import List
import pytest
from collections import OrderedDict

from pkg_resources import resource_filename
from cd_alpha.Step import Incubate, Pump, Release, ScreenType, Step
from cd_alpha.ProtocolFactory import ProtocolFactory
import json

# TODO everything should be using pytest moving forward
class TestProtocolFactory():

    def setUp(self):
        # import class and prepare everything here.
        pass
        

    def test_protocol_factory_20v0(self):
        assert False
