#!/usr/bin/env python
from setuptools import setup

setup(
    name="cd_alpha",
    version="1.0",
    description="ChipDx App for V0 devices",
    author="Will Brown",
    author_email="will.brown@chip-diagnostics.com",
    url="https://www.chip-diagnostics.com/",
    packages=["cd_alpha", "cd_alpha.tests", "cd_alpha.software_testing"],
    include_package_data=True,
    package_data={"": ["gui-elements/*.kv", "device_config.json"]},
    entry_points={
        "console_scripts": [
            "chip = cd_alpha.ChipFlowApp:main",
            "update = cd_alpha.Device:get_updates",
        ],
    },
)
