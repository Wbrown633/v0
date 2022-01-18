#!/usr/bin/env python

from setuptools import setup

setup(
      name='cd_alpha',
      version='1.0',
      description='ChipDx App for V0 devices',
      author='Will Brown',
      author_email='will.brown@chip-diagnostics.com',
      url='https://www.chip-diagnostics.com/',
      packages=["cd_alpha", "cd_alpha.tests", "cd_alpha.software_testing"],
      package_data={'cd_alpha': ['gui-elements/']},
)