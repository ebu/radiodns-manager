# Lightweight PlugIt Proxy

The Lightweight PlugIt Proxy is a project meant to help PlugIt based app to
decouple from EBU.io. 

**Before doing anything with this project**
Note that the PlugIt Technology is old and is in the process of being discarded.

**DO NOT START A NEW PROJECT USING PLUGIT.**

This repository is a temporary solution for any old projects that need to decouple from ebu.io quickly.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and
testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You'll need the following software:
- Python 3.7.0+
- virtualenv 16.0.0+
- Docker 18.09.0+
- docker-compose 1.23.2+

### Installing
First create a virtual env using python 3 as a base:

    virtualenv --python=$(which python3) venv
    
Now activate this virtual python environment. If you wish to deactivate it simply type `deactivate` in the terminal.

    source venv/bin/activate
    
Now install the project dependencies:

    pip install .

### Configuration
You can configure this docker image by providing the following environment variables:

- **DEBUG**:  Can be `True`|`False`. Defaults to `True`. If `True` we django app will run in debug mode. Otherwise, it will run in production mode.
- **LPP_PORT**: Stands for Lightweight PlugIt Proxy port. Numeric. Defaults to `4000`. Defines the port where the app will listen.
- **PLUGIT_APP_URL**: The location of the PlugIt backend. Default to `http://localhost:5000/`. The app url must end with a `/`.
- **SECRET_KEY**: Django secret (random string). To be defined in production.
- **ALLOWED_HOSTS**: List of allowed hosts to connect to the django server separated by commas. Defaults to ` 127.0.0.1,localhost`.
- **DATABASE_NAME**: The name of the postgres database to connect to. Defaults to `lpp`.
- **DATABASE_USER**: The username of the posgtres user that the application will use. Defaults to `root`.
- **DATABASE_PASSWORD**The password of the posgtres user that the application will use. Defaults to empty string.
- **DATABASE_HOST**: The database hostname/ip address that the application will connect to. Defaults to `127.0.0.1`.
- **DATABASE_PORT**: The database port that the application will connect to. Defaults to `5432`.
- **PLUGIT_REMOTE_SERVER_SECRET**: Secret shared with the PlugIt Backend. Must be a random string. Defaults to `dev-secret`.
- **SU_NAME**: Superuser name for the Django admin panel.
- **SU_EMAIL**: Email for the superuser of Django admin panel.
- **SU_PASSWORD**: Password for the superuser of Django admin panel.
- **DATABASE_CONNECTION_MERCY_TIME**: Time to wait (in seconds) until each reset of the backoff database connection retry function. Default to 60.
The application will wait an increasingly longer time for each failed database connection attempts. This is done in order to
avoid having multiple apps connecting to a database at the same time but rather spread those connections so all app can reconnect smoothly.
After X seconds (X being the time chosen for this parameter) the increasing time to wait between each attempt will be
reset so an application doesn't take 300 seconds to reconnect to its database.

## Running the tests
The tests will create a local sqlite database. They do not require any networking setup.
Instead every http call is mocked.

To run the tests:

    python manage.py test

### Tests structure
Tests are mainly made for the PlugIt bridge between this django app and any PlugIt reliant backend.

The tests are located under the plugit/tests folder.

The file `test_proxy_do_query.py` tests the connectivity between
the proxy and a PlugIt backend. It asserts that the do_query function (which is basically the transport layer) can
transmit/receive files/template to the PlugIt backend.

The file `test_proxy_plugit.py` tests the general PlugIt proxy functionalities required to run a minimal PlugIt proxy.

## Deployment
### Building Docker image
You can use the `ebutech/platform-proxy.open.radio` docker image directly into you production stack. However
if you wish to build the image yourself this can be achieved by running the following command:

    docker build -t <docker hub orga/account>/<name of the image>:<tag>
    
To push this image to your orga/account in docker hub:
    
    docker login
    docker push <docker hub orga/account>   /<name of the image>:<tag>
    
The `<tag>` is optional and is by default "latest".

### Deploy on any device
You will need a docker-compose configuration. You can take the `docker-compose.yml` as a base and then add
the PlugIt backend into the stack. An full featured example with HTTPS and RadioDns can be found
[here](https://github.com/ioannisNoukakis/radiodns-docker-demo).

#### General commands with docker-compose

**NOTE** These commands should be run in the application's folder.

To check the service status:

    docker ps
    
To access applications logs:

    docker logs <name_of_docker_container>

To start up:

    docker-compose up --build -d

To shut down:

    docker-compose down

To remove the database and start afresh

    docker-compose down
    docker volume rm radiodns-docker-demo_pgdata
    docker-compose up --build -d

## Authors
* **Ioannis Noukakis** - *Initial work* - [ioannisNoukakis](https://github.com/ioannisNoukakis)
