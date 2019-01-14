#Development mock API.

The Mock API serves as a local dev replacement for some AWS and ebu.io functionalities. 
Currently it provides image hosting and organisation api rest endpoint. 

## Setup

Virtualenv is not mandatory but **STRONGLY** recommended.

You need the following dependencies:
- python 3.7
- docker 18.06.1
- virtualenv 16.0.0

Next you have to setup the virtualenv:

    virtualenv --python=<your path to python3 binary> venv
    source venv/bin/activate
    
And then install the required PIP dependencies

    pip install .
    
To deactivate the running environment

    deactivate

You'll find in the root project a script installing every project with their dependencies.

## Run
To run start the mock API run

    python app.py
    
## Configuration

You can configure the application by setting the environment variables described in `config.py`.