import config
import os
import hashlib
import random
import string

def genPassword(*seeds):
    return hashlib.sha224("^34g" + "".join(seeds)).hexdigest()
    
def genSecretKey():
    """Regenerate a random key"""
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))

def conf_path_builder(script_file):
    """Return a function that given the name of a configuration file, return it's absolute location on the disk
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(script_file)), config.CONFIG_DIR)
    def conf(file_name):
        return os.path.join(config_path, file_name)
    return conf
