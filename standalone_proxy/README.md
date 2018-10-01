#Plugit Standalone Proxy

This serves as a replacement for the ebu.io plugit instance for local dev. Do not run this container in production!
It is advised to use the official PlugIt Proxy from EBU.io.

## Setup

You need the following dependencies:
- python 2.7
- docker 18.06.1
- virtualenv 16.0.0

Next you have to setup the virtualenv:

    virtualenv venv
    source venv/bin/activate
    
And then install the required PIP dependencies

    pip install .
    

You'll find installation instructions for each project in the README.md of their respective folder.

## Run
To run start the Plugit Standalone Proxy:

    python manage.py runserver 0.0.0.0:4000