#Plugit Standalone Proxy

This serves as a replacement for the ebu.io plugit instance for local dev.

## Setup

You need the following dependencies:
- python 2.7
- docker 18.06.1
- virtualenv 16.0.0

Next you have to setup the virtualenv:

    virtualenv --python=<your path to python2 binary> venv
    source venv/bin/activate
    
And then install the required PIP dependencies

    pip install .
  
To deactivate the running environment

    deactivate
    
You'll find in the root project a script installing every project with their dependencies.

## Run
To run start the Plugit Standalone Proxy:

    python manage.py runserver 0.0.0.0:4000