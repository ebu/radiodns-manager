RadioDNS-plugit
===============

This project gathers a web interface based on [plugit](https://github.com/ebu/plugit) to manage RadioDNS services ([RadioVIS, RadioEPG and ServiceFollowing](http://www.radiodns.org)). 

The project contains a scalable RadioVis server written in python (without comet support).

You can find the plugit module inside `RadioDns-PlugIt` (See installation below to see how to run it), the RadioVis server inside `RadioVisServer` and deployments scripts inside `Deployment`. 

Check each folder for specifics README about each part.


## General architecture

![Image](architecture-radiodns.png?raw=true)


## Installation

The RadioDNS manager is based on PlugIt, so you will need to :

* Download a PlugIt [client](https://github.com/ebu/PlugIt)
* Configure the [server](https://github.com/ebu/radiodns-plugit/tree/develop/RadioDns-PlugIt#config)

Instruction to deploy each parts of the project are available in the [Deployment folder](https://github.com/ebu/radiodns-plugit/tree/develop/Deployment)

## RadioDNS Services

## RadioVIS Server

### MQ and VIS on same machine
If you are using RabbitMQ and VIS on the same machine make sure that the config.py contains either localhost as MQ server
or to add the machines public DNS name to /etc/hosts.

### Processes

![Image](architecture-radiovis-processes.png?raw=true)

## Contact

Contact the EBU (Mathias Coinchon, coinchon@ebu.ch) if you need more information about RadioDNS and its associated developments.


## Contributors

* Maximilien Cuony [@the-glu](https://github.com/the-glu)
* Malik Bougacha [@gcmalloc](https://github.com/gcmalloc)
* Michael Barroco [@barroco](https://github.com/barroco)
* Mathieu Habegger [@mhabegger](https://github.com/mhabegger)


## Copyright & License

Copyright (c) 2013-2015, EBU-UER Technology & Innovation

The code is under BSD (3-Clause) License. (see LICENSE.txt)