""" This is the main fabfile for deployement ! """
from fabric.api import *
from fabric.state import output

from rabbitmq import rabbitmq_server
from plugit import plugit_server
from radiovis import radiovis_server

import config
import boto.ec2

# Remove useless output
output.stdout = True

# Build the server list from amazon (for all deploy operations)
env.roledefs = {
    'radiodns': [],
    'radiovis': [],
}
# Set settings
env.user = config.SSH_USER
env.key_filename = config.SSH_CERT

# Get the host from AWS
conn = boto.ec2.connect_to_region(config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)

print '------------------------------'
print 'Adding RadioDNS EC2 instances by tag : ' + config.RADIODNS_AWS_TAG
for res in conn.get_all_instances(filters={"tag:id": config.RADIODNS_AWS_TAG, 'instance-state-code': 16}):  # 16 = Running
    for ins in res.instances:
        print '   Adding '+ins.public_dns_name + ' ('+ins.ip_address+')'
        env.roledefs['radiodns'].append('ubuntu@' + ins.ip_address)
print '------------------------------'
print '------------------------------'
print 'Adding RadioVIS EC2 instances by tag : ' + config.RADIODNS_AWS_TAG
for res in conn.get_all_instances(filters={"tag:id": config.RADIOVIS_AWS_TAG, 'instance-state-code': 16}):  # 16 = Running
    for ins in res.instances:
        print '   Adding '+ins.public_dns_name + ' ('+ins.ip_address+')'
        env.roledefs['radiovis'].append('ubuntu@' + ins.ip_address)
print '------------------------------'

@task
@roles('radiodns')
def deploy_radiodns():
    """Deploy RadioDNS Servers (plugit)"""
    print '\n\nStarting RadioDNS Server Deployment.\n'

    plugit_server.deploy()

@task
@roles('radiodns')
def update_radiodns():
    """Update RadioDNS Servers (plugit)"""
    print '\n\nUpdating RadioDNS Server Deployment.\n'

    plugit_server.update()