""" This is the main fabfile for deployement ! """
from fabric.api import *
from fabric.state import output

from rabbitmq import rabbitmq_server

from plugit import plugit_server

from radiovis import radiovis_server

import config

# Remove useless output
output.stdout = True

#include the ssh config file
env.use_ssh_config = config.USE_SSH_CONFIG

# Set settings
env.user = config.SSH_USER
env.key_filename = config.SSH_PRIVKEY


if not env.hosts:
    # Get the host from AWS
    import boto.ec2
    conn = boto.ec2.connect_to_region(config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)

    for res in conn.get_all_instances(filters={"tag:id": config.AWS_VM_TAG, 'instance-state-code': 16}):  # 16 = Running
        for ins in res.instances:
            env.hosts.append('ubuntu@' + ins.ip_address)
