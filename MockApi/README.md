#Development mock API.

The Mock API serves as a local dev replacement for some AWS and ebu.io functionalities. 
Currently it provides functionalities like image hosting and
organisation api rest endpoint. 

## Setup

You need the following dependencies:
- python 3.7
- docker 18.06.1
- virtualenv 16.0.0

Next you have to setup the virtualenv:

    virtualenv venv
    source venv/bin/activate
    
And then install the required PIP dependencies

    pip install .
    

You'll find installation instructions for each project in the README.md of their respective folder.

## Run
To run start the mock API run

    python src/app.py