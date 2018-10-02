RadioDns - PlugIt
=================

This folder contains the PlugIt server API. It has to run in OrgaMode (see PlugIt README for details).

The API is also called by the RadioVisServer.

# Features

## RadioDns

The API allow the management of stations and channels.

### Setting up locally RadioDNS

#### Requirements
- python 2.7
- docker 18.06.1
- virtualenv 16.0.0

#### installation

##### Preparing the `venv`

    virtualenv --python=<your path to python2 binary> venv
    source venv/bin/activate
    
Install the required PIP dependencies

    pip install .
    
To deactivate the running environment

    deactivate
    
You'll find in the root project a script installing every project with their dependencies.
    
#### Running the PlugIt Server

    python server.py
    
#### Extra steps for mac users

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
    
Remember that you must have a running client (proxy) in order to test the service.

## RadioVis /!\ Not ready for use in this revision

The API allow management of defaults medias, and store logs about messages sent on different topics.

## Dependencies

/!\ ALWAYS FIX DEPENDENCIES VERSION! /!\

The python dependencies include (but are not limited to, look at setup.py in the root folder for a full list):

* flask (BSD license)
* sqlalchemy (MIT license)
* Flask-SQLAlchemy (BSD license)
* alembic (MIT license)
* dnspython (BSD-style license)
* requests (Apache2 license)

You can install them using `pip install .`

## Test

Tests are available in the RadioDns-Tests folder of the root folder.

## Core

The core of the API is a flask server. It can be ran (for development) using `python server.py` or (for production) using the `wsgi.py` wsgi script.

All PlugIt actions are in the `actions.py` file. All details are available in the PlugIt documentation (everything is based from the _Simple Flask server_)

## Database

Sqlalchemy is used for database access. Models are defined inside the `models.py` file.

## Database migrations

For easy model upgrade, alembic is used. When a model is modified it's possible to run the command
`alembic revision --autogenerate -m 'message'` to create a new revision of the database.
`alembic upgrade head` is used to apply changes, upgrading the database to the latest version.
Details are available in the official documentation of alembic.

Migrations are done automatically by the server at startup if needed.

### Migration Issue with Log INdexs or with constraint on Logo

If you end up stuck on alembic upgrade because of an index or because of a foreign key constraint. Make sure that
 the constrains are fine. Use the following to check service_provider logos for example:

    SELECT * from service_provider LEFT JOIN logo_image ON (service_provider.default_logo_image_id = logo_image.id) 
    WHERE service_provider.default_logo_image_id  IS NOT NULL AND logo_image.id IS NULL;
    
Or remove the dupplicate indexes using :

    DROP INDEX ix_log_entry_reception_timestamp on log_entry;
    

# Config

The configuration is stored inside `config.py`. You can change it by setting environments variable corresponding to the config parameters.