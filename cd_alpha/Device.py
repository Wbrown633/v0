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

    DEV_MACHINE: bool
        - Set this flag true to disable all communication over serial to motors. This is usefull when doing graphical/app dev,
        or anytime you wish to run the program not on a properly configured device

    PUMP_SERIAL_ADDR: str
        - Serial address for the pump/pump network. Defaults to "/dev/ttyUSB0" on linux 
        which shouldn't need to be changed

    PUMP_ADDR: list[int]
        - Default for r0: PUMP_ADDR = [0]
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
        R0_PUMP_ADDR_DEFAULT = 0
        V0_WASTE_ADDR_DEFAULT = 1
        V0_LYSATE_ADDR_DEFAULT = 2
        R0_PUMP_DIAMETER_DEFAULT = 12.55
        V0_WASTE_DIAMETER_DEFAULT = 12.55
        V0_LYSATE_DIAMETER_DEFAULT = 12.55
        POST_RUN_RATE_MM_DEFAULT = None
        POST_RUN_VOL_ML_DEFAULT = None

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
                self.PATH_TO_PROTOCOLS = "/home/pi/v0/cd_alpha/protocols/"

            if not hasattr(self, "DEV_MACHINE"):
                self.DEV_MACHINE = False

            if not hasattr(self, "START_STEP"):
                self.START_STEP = "home"

            if not hasattr(self, "POST_RUN_RATE_MM"):
                self.POST_RUN_RATE_MM = POST_RUN_RATE_MM_DEFAULT

            if not hasattr(self, "POST_RUN_VOL_ML"):
                self.POST_RUN_VOL_ML = POST_RUN_VOL_ML_DEFAULT
            
            # Set defaults based on device type
            if self.DEVICE_TYPE == "R0":
                if not hasattr(self, "PUMP_ADDR"):
                    self.PUMP_ADDR = [R0_PUMP_ADDR_DEFAULT]
                if not hasattr(self, "PUMP_DIAMETER"):
                    self.PUMP_DIAMETER = [R0_PUMP_DIAMETER_DEFAULT]
            elif self.DEVICE_TYPE == "V0":
                if not hasattr(self, "PUMP_ADDR"):
                    self.PUMP_ADDR = [V0_WASTE_ADDR_DEFAULT,V0_LYSATE_ADDR_DEFAULT]
                if not hasattr(self, "PUMP_DIAMETER"):
                    self.PUMP_DIAMETER = [V0_WASTE_DIAMETER_DEFAULT, V0_LYSATE_DIAMETER_DEFAULT]
            else:
                raise ValueError("Device type was not either V0 or R0 (Case sensitive)")


            print(vars(self))
        
        except IOError:
            logging.error("device_config.json was not found or could not be opened.")