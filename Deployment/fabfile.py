""" This is the main fabfile for deployement ! """
from fabric.api import *
from fabric.state import output

from rabbitmq import rabbitmq_server
from plugit import plugit_server
from radiovis import radiovis_server

import time
import config
import boto.ec2

# Remove useless output
output.stdout = True

# Build the server list from amazon (for all deploy operations)
env.roledefs = {
    'radiodns': [],
    'radiovis': [],
    'rabbitmq': [],
}
# Set settings
env.user = config.SSH_USER
env.key_filename = config.SSH_PRIVKEY

# Get the host from AWS
conn = boto.ec2.connect_to_region(config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)

print '------------------------------'
print ' Loading AWS Services for tags...'
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
print '------------------------------'
print 'Adding RabbitMQ EC2 instances by tag : ' + config.RABBITMQ_AWS_TAG
for res in conn.get_all_instances(filters={"tag:id": config.RABBITMQ_AWS_TAG, 'instance-state-code': 16}):  # 16 = Running
    for ins in res.instances:
        print '   Adding '+ins.public_dns_name + ' ('+ins.ip_address+')'
        env.roledefs['rabbitmq'].append('ubuntu@' + ins.ip_address)
print '------------------------------'

# OLD
# if not env.hosts:
#    # Get the host from AWS
#    import boto.ec2
#    conn = boto.ec2.connect_to_region(config.AWS_REGION, aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY)
#
#    for res in conn.get_all_instances(filters={"tag:id": config.AWS_VM_TAG, 'instance-state-code': 16}):  # 16 = Running
#        for ins in res.instances:
#            env.hosts.append('ubuntu@' + ins.ip_address)

@task
def list_machines():
    """List machines assigned to RadioVIS roles"""
    print
    print
    print "############################################"
    print "#            RADIO DNS MACHINES            #"
    print "############################################"
    print
    for h in env.roledefs['radiodns']:
        print '    -  ' + h
    print
    print
    print "############################################"
    print "#            RADIO VIS MACHINES            #"
    print "############################################"
    print
    for h in env.roledefs['radiovis']:
        print '    -  ' + h
    print
    print
    print "############################################"
    print "#            RABBITMQ MACHINES             #"
    print "############################################"
    print
    for h in env.roledefs['rabbitmq']:
        print '    -  ' + h

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

@task
@roles('radiovis')
def deploy_radiovis():
    """Deploy RadioDNS Servers (plugit)"""
    print '\n\nStarting RadioVIS Server Deployment.\n'

    radiovis_server.deploy()

@task
@roles('radiovis')
def update_radiovis():
    """Update RadioVIS Servers (plugit)"""
    print '\n\nUpdating RadioVIS Server Deployment.\n'

    radiovis_server.update_withfallback()

@task
@roles('rabbitmq')
def deploy_rabbtimq():
    """Deploy RabbitMQ Servers (plugit)"""
    print '\n\nStarting RabbitMQ Server Deployment.\n'

    rabbitmq_server.deploy()


@task
def restart_services():
    """Restart all Services"""
    print '\n\nRestarting RadioDNS and RadioVIS Services.\n'

    print '\n\nRestarting RadioDNS Plugit Server ...\n'
    execute(plugit_server.restart_apache)
    time.sleep(2)

    print '\n\nRestarting RadioVIS Main Service ...\n'
    execute(radiovis_server.restart_radiovis)
    time.sleep(2)

    print '\n\nRestarting RadioVIS Fallback Service ...\n'
    execute(radiovis_server.restart_fallback)
    time.sleep(2)
