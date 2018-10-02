RadioDNS-plugit
===============

## /!\ THIS PROJECT IS UNDER HEAVY REFACTORING. IT IS ADVISED TO WAIT THE NEXT RELEASE AS IT WILL HAVE BREAKING CHANGES /!\

This project gathers a web interface based on [plugit](https://github.com/ebu/plugit) to manage RadioDNS services ([RadioVIS, RadioEPG and ServiceFollowing](http://www.radiodns.org)). 

The project contains a scalable RadioVis server written in python (without comet support).

At the end of this refactor the project will be able to be deployed on docker. 

Check each folder for specifics README about each part.

## Glossary

- When we refer to "client" we mean a standalone PlugIt proxy.
- By PlugIt Server we mean the dns service (RadioDns-PlugIt folder).

## General architecture

This part will be updated once a new structure is fixed.

## Requirements
- python 2.7 and 3.7
- docker 18.06.1
- virtualenv 16.0.0

## Installation

To install automatically the python environment on an unix system simply use the `setup-envs.sh script.

To get at least the basic service working you must have the PlugIt Client (standalone_proxy), the Dns service (RadioDns-Plugit) and a mysql instance (you can use the one provided in docker-compose-dev.yml, by using the `docker-compose -f docker-compose-dev.yml up -d`) up and running.

Old instructions to deploy each parts of the project are available in the [Deployment folder](https://github.com/ebu/radiodns-plugit/tree/develop/Deployment) (On this revision omit RadioVisServer as further investigation is needed on this project). For local development please refer to each project's readme.

## How to run tests
If you haven't already, run the `setup-envs.sh` (if you are on an unix based system).
Then set your working directory to the tests folder and read its README for further instructions.

# How to run in local development 

To start up a local instance

```
docker-compose up --build 
```

To shut down the local instance

```
docker-compose down
```

To remove the database and start afresh

```
docker-volume rm radiodns-plugit_db_data 
```

## Contribution guidelines
- Always fix version of dependencies.
- Any new module that can be written in python 3 must be written in python 3.

## Contact

Contact the EBU (Ben Poor poor@ebu.ch) if you need more information about RadioDNS and its associated developments.


## Contributors

* Maximilien Cuony [@the-glu](https://github.com/the-glu)
* Malik Bougacha [@gcmalloc](https://github.com/gcmalloc)
* Michael Barroco [@barroco](https://github.com/barroco)
* Mathieu Habegger [@mhabegger](https://github.com/mhabegger)
* Ioannis Noukakis [@inoukakis](https://github.com/ioannisNoukakis)


## Copyright & License

Copyright (c) 2013-2015, EBU-UER Technology & Innovation

The code is under BSD (3-Clause) License. (see LICENSE.txt)
