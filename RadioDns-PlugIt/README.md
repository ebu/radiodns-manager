RadioDns - PlugIt
=================

This folder contains the PlugIt server API. It has to run in OrgaMode (see PlugIt README for details).

The API is also called by the RadioVisServer.

# Features

## RadioDns

The API allow the management of stations and channels.

## RadioVis

The API allow management of defaults medias, and store logs about messages sent on different topics.

# Tools used

The server is written in Python.

## Dependencies

The python dependencies are:

* flask (BSD license)
* sqlalchemy (MIT license)
* Flask-SQLAlchemy (BSD license)
* alembic (MIT license)
* dnspython (BSD-style license)
* requests (Apache2 license)

You can install them using `pip install _package_`

## Core

The core of the API is a flask server. It can be ran (for development) using `python server.py` or (for production) using the `wsgi.py` wsgi script.

All PlugIt actions are in the `actions.py` file. All details are available in the PlugIt documentation (everything is based from the _Simple Flask server_),

## Database

Sqlalchemy is used for database access. Models are defined inside the `models.py` file.

## Database migrations

For easy model upgrade, alembic is used. When a model is modified it's possible to run the command
`alembic revision --autogenerate -m 'message'` to create a new revision of the database.
`alembic upgrade head` is used to apply changes, upgrading the database to the latest version.
Details are available in the official documentation of alembic.

# Config

The configuration is stored inside `config.py`, who can be created from `config.py.dist`.

#### API_URL
The URL to call the PlugIt client

#### SQLALCHEMY_URL
The connection string to MYSQL for SqlAlchemy

#### API_SECRET
A secret, shared with the RadioVisServer to access specials calls.

#### DEBUG
Set this to True to launch flask in debug mode.

#### PI_BASE_URL
The base URL for the PlugIi API (Check PlugIt documentation)

#### PI_ALLOWED_NETWORKS
Clients allowed to use the PlugIt API (Check PlugIt documentation)
