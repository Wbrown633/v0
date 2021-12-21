import json
import logging

class Device:
    
    """[summary]
    """    
    def __init__(self, config_file_json):
        try:
            config_file_dict = json.load(config_file_json)
            for key in config_file_dict.keys():
                pass 
        
        except IOError:
            logging.error("device_config.json was not found or could not be opened.")