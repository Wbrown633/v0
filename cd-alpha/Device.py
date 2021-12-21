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

    
    OPTIONAL

    Optional parameters should only be altered if the user is confident they know what they are doing.
    They should not need to be altered during the course of normal operation.

    PUMP_SERIAL_ADDR: str
        - Serial address for the pump/pump network. Defaults to "/dev/ttyUSB0" on linux 
        which shouldn't need to be changed

    LIST_OF_PUMPS: list[str]
        - for r0 default is ["WASTE"]
        - for v0 default is ["WASTE", "LYSATE"]
        - Should only be changed if more pumps have been added to the network, length must 
        match the len(PUMP_ADDR) AND len(PUMP_DIAMETER)

    PUMP_ADDR: int or list[int]
        - Default for r0: PUMP_ADDR = 0
        - Default for v0: PUMP_ADDR = [1,2]
        - See NE-500 / NE-501 user manual for instructions on changing

    PUMP_DIAMETER: float or list[float]
        - Default for r0: PUMP_DIAMETER = 12.4
        - Default for v0: PUMP_DIAMETER = [12.4, 12.4]
        - For v0 the diameters will be applied in the same order of the pumps.
        Default is [WASTE, LYSATE]

    PATH_TO_PROTOCOLS: str
        - Absolute path location to the protocols folder on this device. By default
        this should be a sub-folder in the v0/cd-alpha directory
    
    DEBUG_MODE: bool
        - Puts the program in debug mode, for dev use only (default is False)

    
    """    
    def __init__(self, config_file_json):

        try:
            with open(config_file_json) as f:
                required_values = ["DEVICE_TYPE", "DEFAULT_PROTOCOL"]
                config_file_dict = json.loads(f.read())
                for req in required_values:
                    if req not in config_file_dict.keys():
                        print(config_file_dict.keys())
                        raise KeyError("Required value {} was not found in config file".format(req))
                for key in config_file_dict.keys():
                    self.__setattr__(key, config_file_dict[key])
            
            # Set univeral defaults
            if not hasattr(self, "PUMP_SERIAL_ADDR"):
                self.PUMP_SERIAL_ADDR = "/dev/ttyUSB0"

            if not hasattr(self, "DEBUG_MODE"):
                self.DEBUG_MODE = False

            if not hasattr(self, "PATH_TO_PROTOCOLS"):
                self.PATH_TO_PROTOCOLS = "/home/pi/cd-alpha/protocols/"
            
            # Set defaults based on device type
            if self.DEVICE_TYPE == "R0":
                if not hasattr(self, "LIST_OF_PUMPS"):
                    self.LIST_OF_PUMPS = ["WASTE"]
                if not hasattr(self, "PUMP_ADDR"):
                    self.PUMP_SERIAL_ADDR = 0
                if not hasattr(self, "PUMP_DIAMETER"):
                    self.PUMP_DIAMETER = 12.4
            elif self.DEVICE_TYPE == "V0":
                if not hasattr(self, "LIST_OF_PUMPS"):
                    self.LIST_OF_PUMPS = ["WASTE", "LYSATE"]
                if not hasattr(self, "PUMP_ADDR"):
                    self.PUMP_SERIAL_ADDR = [1,2]
                if not hasattr(self, "PUMP_DIAMETER"):
                    self.PUMP_DIAMETER = [12.4, 12.4]
            else:
                raise ValueError("Device type was not either V0 or R0 (Case sensitive)")


            print(vars(self))
        
        except IOError:
            logging.error("device_config.json was not found or could not be opened.")