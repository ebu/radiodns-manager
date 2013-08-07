""" This is the main fabfile for deployement ! """
from fabric.api import *
from fabric.state import output

from rabbitmq import rabbitmq_server

import config

# Remove useless output
output.stdout = True

#include the ssh config file
env.use_ssh_config = config.USE_SSH_CONFIG

# Set settings
env.user = config.SSH_USER
env.key_filename = config.SSH_PRIVKEY
