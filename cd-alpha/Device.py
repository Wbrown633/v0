import json
import logging

class Device:
    
    """
    A class to represent the device specific information provided in the device_config.json.
    The following parameters are REQUIRED for a properly formatted config file: 

    REQUIRED

    DEVICE_TYPE: str
        [v0, r0] - Describes the model of this device
    
    DEFAULT_PROTOCOL: str
        - Name of the default script to be used on launch, if anohter script is not chosen with the 
        file chooser this is the protocol that will be run

    PATH_TO_PROTOCOLS: str
        - Absolute path location to the protocols folder on this device. By default
        this should be a sub-folder in the v0/cd-alpha directory
    
    OPTIONAL

    Optional parameters should only be altered if the user is confident they know what they are doing.
    They should not need to be altered during the course of normal operation.

    PUMP_SERIAL_ADDR: str
        - Serial address for the pump/pump network. Defaults to "/dev/ttyUSB0" on linux 
        which shouldn't need to be changed

    PUMP_ADDR: int or list[int]
        - Default for r0: PUMP_ADDR = 0
        - Default for v0: PUMP_ADDR = [1,2]
        - See NE-500 / NE-501 user manual for instructions on changing

    PUMP_DIAMETER: float or list[float]
        - Default for r0: PUMP_DIAMETER = 12.4
        - Default for v0: PUMP_DIAMETER = [12.4, 12.4]
        - For v0 the diameters will be applied in the same order of the pumps.
        Default is [WASTE, LYSATE]
    
    DEBUG_MODE: bool
        - Puts the program in debug mode, for dev use only (default is False)

    
    """    
    def __init__(self, config_file_json):
        try:
            with open(config_file_json) as f:
                required_values = ["DEVICE_TYPE", "DEFAULT_PROTOCOL", "PATH_TO_PROTOCOL"]
                config_file_dict = json.loads(f.read())
                for req in required_values:
                    if req not in config_file_dict.keys():
                        raise KeyError("Required value {} was not found in config file".format(req))
                for key in config_file_dict.keys():
                    print(key, config_file_dict[key])
        
        except IOError:
            logging.error("device_config.json was not found or could not be opened.")