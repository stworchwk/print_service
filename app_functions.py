# CaLL CONFIG FILE
from configparser import ConfigParser

## ==> GLOBALS
CONFIG_FILE_NAME = 'config.ini'

class AppFunctions():

    def initial_config(self):
        config = ConfigParser()
        config.read(CONFIG_FILE_NAME)
        return config

    
    def call_config(self):
        config = AppFunctions.initial_config(self)
        return [config['host']['host'], config['host']['inval']]


    def update_config(self, new_host, new_inval):
        config = AppFunctions.initial_config(self)

        config.set('host', 'host', str(new_host))
        config.set('host', 'inval', str(new_inval))

        with open(CONFIG_FILE_NAME, 'w') as configfile:
            config.write(configfile)

        