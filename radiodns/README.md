# Standalone RadioDNS manager

This part of the project contains all of the code for running the RadioDNS manager panel and the AWS integration. 
This module has been rewritten from scratch in order to remove the dependancy from plugit protocol. 
It is still work in progress and some parts of the documentation and test suite may still be obsolete.

## Project Structure
The project has three major parts
* apps - core implementation split info functional parts 
* common - common views and static files - templates, styles and scripts
* config - django project base, and setting presets for different environments

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and
testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- python 3.8
- virtualenv 20.0.0+

AND/OR

- docker 19.0.0+
- docker-compose 1.26+

### Running with `venv`

If you prefer to have the application running locally without additional virtualization layer, you can use python's native virtualenv.
```
virtualenv -p3.8 venv
source venv/bin/activate
cd radiodns
```
    
Install the required PIP dependencies:
```
pip install -r requirements.txt
```
    
To deactivate the running environment:
```
deactivate
```

Running the application locally follows the typical flow of a Django based application:

Initialize migrations and migrate
```
python manage.py makemigrations
python manage.py migrate
```
Add constant country code and languages data
```
python manage.py create_ecc_records
python manage.py create_language_records
```

Create a superuser 
```
python manage.py initadmin 
```
Run the server
```
python manage.py runserver
```
### Running with docker
If you don't want or can't setup virtualenv, you can run project with docker.

Copy example .env file and set all the required variables. Then build docker images, and run them. 
```
docker-compose -f docker-compose-new-standalone.yml build
docker-compose -f docker-compose-new-standalone.yml up
```
If there are any problems with database on startup, you might find that just simply resetting the containers does not work, as the storage is permanent.
To ensure that all the configurations have been reloaded use:
```
docker-compose -f docker-compose-new-standalone.yml down
docker-compose -f docker-compose-new-standalone.yml up --force-recreate
```

## Configuration
Configuration is designed to be modular and use inheritance. 
Base settings needed in every environment are defined in the `config/settings/base.by`
They can be overwritten in the enviroment files like `config/settings/local.by`
and `config/settings/staging.by`.

If you need to add a new environment be sure to follow the current template.

## Database

## Database migrations
Like all django applications, the migrations are handled automatically.
If a model was changed it is enough to use two commands
```
python manage.py makemigrations
python manage.py migrate
```

When using docker, migrations are done automatically by the server at startup if needed.


