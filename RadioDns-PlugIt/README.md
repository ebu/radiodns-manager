RadioDns - PlugIt
=================

This folder contains the RadioDns API server. The API is also called by the RadioVisServer.

# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and
testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- python 2.7
- docker 18.06.1+
- virtualenv 16.0.0+
- docker-compose 1.23.2+

### Installing
#### Preparing the `venv`

    virtualenv --python=$(which python2) venv
    source venv/bin/activate
    
Install the required PIP dependencies:

    pip install .
    
To deactivate the running environment:

    deactivate
    
### Running the PlugIt Server

    python server.py
    
Remember that you must have a running PlugIt Proxy in order to test the service.

### Extra steps for mac users

You need the mysql connector

    brew install mysql-connector-c
    
Then you must edit the mysql_config file located in ```/usr/local/bin/mysql_config```

You must edit those lines

    # Create options 
    libs="-L$pkglibdir"
    libs="$libs -l "
    
To

    # Create options 
    libs="-L$pkglibdir"
    libs="$libs -lmysqlclient -lssl -lcrypto"
    
Finally you have to add those lines to your .bash_profile (in your home directory)(If this file dosen't exist just create it).

    LDFLAGS:  -L/usr/local/opt/openssl/lib
    CPPFLAGS: -I/usr/local/opt/openssl/include

## Test
Tests are available in the tests folder of the root folder.

## Database
Sqlalchemy is used for database access. Models are defined inside the `models.py` file.

## Database migrations
For easy model upgrade, alembic is used. When a model is modified it's possible to run the command
`alembic revision --autogenerate -m 'message'` to create a new revision of the database.
`alembic upgrade head` is used to apply changes, upgrading the database to the latest version.
Details are available in the official documentation of alembic.

Migrations are done automatically by the server at startup if needed.

# Config
The configuration is stored inside `config.py`. You can change it by setting environment variables  corresponding to the config parameters.