Deployment scripts
==================

This folder contains deployments scripts for each part of the project.

Fabric is used (BSD license)

Scripts assume the presence of an ubuntu user and `apt-get` tool. They should work with any fresh install of ubuntu server, with defaults parameters.

# Setup

Create a `config.py` file, using `config.py.dist.py` as base. Copy the SSH key to connect to servers inside sshKeys.

## Config

### SSH

#### SSH_USER
The user for SSH connections

#### SSH_PRIVKEY
The SSH key for SSH connections

#### USE_SSH_CONFIG
Fabric option to use the local ssh config. Set this to False if you're using windows or you don't have an ssh config file.

### RabbitMQ

#### RABBITMQ_USER
The username for the rabbitmq admin user

#### RABBITMQ_PASS
The password for the rabbitmq admin user

#### RADIOVIS_RABBITMQ_HOST
The rabbitmq host

#### RADIOVIS_RABBITMQ_QUEUE
The name of the main queue for rabbitmq. This should be configured as a 'fanout' exchange.

### RadioVis

#### RADIOVIS_API_URL
The URL of the PlugIt API, for the RadioVisServer

#### RADIOVIS_LOG_LEVEL
The level of logging for the RadioVisServer

### Git

#### GIT_REPO
The git repository to deploy code from

#### GIT_BRANCH
The branch used to deploy code

#### GIT_PRIV_KEY
The private key to connect to the git repository

#### GIT_RADIOVISDIR
The folder with RadioVisServer

#### GIT_PLUGITDIR
The folder with the PlugIt API

### Deployement

#### CONFIG_DIR
The folder with configuration files

### MySQL

#### MYSQL_USER 
The MYSQL user

#### MYSQL_DATABASE
The MYSQL database

#### MYSQL_PASSWORD
The MYSQL password

### PlugIt 

#### PLUGIT_API_URL
The URL to callback the Plugit API

#### SQLALCHEMY_URL
The connection string to MYSQL for SqlAlchemy

#### PLUGIT_PUBLIC_ACCESS
The public URL to access PlugIt (used for fallback medias)

##### API_SECRET
The secret to use the PlugIt API (from the RadioVisServer)

#### API_BASE_URL
The base URL for the PlugIt API.

#### API_ALLOWD_IPS
Subnets allowed to use the PlugIt API.


# Main commands

You can use `fab --list` to list all commands.

#### plugit_server.deploy

Deploy a new RadioDns-PlugIt instance on a server with apache and everything. Main commands are:

#### plugit_server.upgrade

Update the code on a PlugIt server from GIT

#### rabbitmq_server.deploy

Deploy a new RabbitMq server

#### radiovis_server.deploy

Deploy a new RadioVis server node

#### radiovis_server.deploy_withfallback

Deploy a new RadioVis server node, with the fallback client

#### radiovis_server.update

Update code on a RadioVis server node from GIT

#### radiovis_server.update_withfallback

Update code on a RadioVis server node from GIT, including the fallback client