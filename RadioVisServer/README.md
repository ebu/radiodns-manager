RadioVisServer
==============

The RadioVisServer is an implementation of a RadioVis server in Python. Only the Stomp mode is available.

For scalability, the server is connected to a RabbitMq server. It's possible to run multiples instances of the server (sharing one RabbitMq server), allowing more RadioVis client to be connected.

# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and
testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- python 2.7
- docker 18.06.1+
- virtualenv 16.0.0+
- docker-compose 1.23.2+

### Installing
#### Preparing the `venv`

    virtualenv --python=$(which python2) venv
    source venv/bin/activate
    
Install the required PIP dependencies:

    pip install .
    
To deactivate the running environment:

    deactivate
    
## Running the Server

    python server.py
    
## Running the Fallback Server

    python fallback.py
    
## Configuration
The configuration is stored inside `config.py`. You can change it by setting environment variables corresponding to the config parameters.

Here is a list of the options you can configure through environment variables:

- **RABBITMQ_HOST**: Host of the RabbitMQ server. Defaults to `127.0.0.1`.
- **RABBITMQ_PORT**: Port of the RabbitMQ server. Numeric. Defaults to `5672`.
- **RABBITMQ_USER**: User to use when connection to the RabbitMQ server. Default to `guest`.
- **RABBITMQ_PASSWORD**: Password of the chosen user. Defaults to `guest`.
- **RABBITMQ_VHOST**: RabbitMQ vhost to use. Defaults to `/`.
- **RABBITMQ_DEBUG**: If the connections with the RabbitMQ server should be in debug mode. Can be `True` | `False`. 
Defaults to `True`.
- **RABBITMQ_EXCHANGE**: RabbitMQ exchange type that will be used by the vis server. Defaults to `amq.fanout`.
- **MONITORING_ENABLED**: Switch to enable/disable the RabbitMQ monitoring plugin. Can be `True` | `False`. 
Defaults to `True`.
- **MONITORING_HOST**: Host of the monitoring server for the RabbitMQ server. Defaults to `127.0.0.1`.
- **MONITORING_PORT**: Port of the monitoring server for the RabbitMQ server. Defaults to `5672`.
- **MONITORING_USER**: User to use when connection to the monitoring RabbitMQ server. Default to `guest`.
- **MONITORING_PASSWORD**: Password of the chosen monitoring user. Defaults to `guest`.
- **MONITORING_VHOST**: RabbitMQ monitoring vhost to use. Defaults to `/`.
- **MONITORING_DEBUG**: If the connections with the RabbitMQ monitoring server should be in debug mode. Can be `True` | `False`. 
Defaults to `True`.
- **MONITORING_EXCHANGE**: monitoring RabbitMQ exchange type. Defaults to `monitoring.buffer`.
- **MONITORING_QUEUE**: monitoring RabbitMQ queue. Defaults to `radiovis`.
- **MONITORING_SERVER_ID**: RabbitMQ node name. See [the RabbitMQ docs](https://hub.docker.com/_/rabbitmq/).
- **STOMP_IP**: Accepted hosts for the stomp server. List of host comas separated. Defaults to `0.0.0.0`.
- **STOMP_PORT**: Port where the stomp server will listen to. Numeric. Defaults to `61613`.
- **RADIODNS_API_URL**: RadioDns VIS service url. Scheme: `http://<HOST>/<API_SECRET>/action/radiovis/api/<API_SECRET>/`. Please refer
to the RadioDns manager repository for informations about the **API_SECRET** parameter.
- **MEMCACHED_HOST**: Host of the memcached server. Defaults to `127.0.0.1`.
- **FB_CHANNEL_CACHE**: Fallback channels cache time before being considered as stale. In Seconds. Defaults to `60`.
- **FB_FALLBACK_CHECK**: Fallback interval check time. In Seconds. Defaults to `15`.
- **FB_FALLBACK_TIME**: Fallback channel grace time. Time before a channel is considered dead. In Seconds. Defaults to `60`. 
- **FB_LOGS_MAX_AGE**: Fallback logs max age before being discarded. In Seconds. Defaults to `86400` (24h).
- **FB_LOGS_CLEANUP**: Clean Fallaback logs every X seconds, X being this parameter. Defaults to `3600` (1h).
    
# Parts

There is 3 mains parts: The RadioVis server, the fallback server and the test script

## RadioVis server

This part takes care of connection to RadioVis clients and forwarding of messages. This can be started using `python server.py`. Multiple instances can be ran.

It's possible, for debugging, to run the server without a RabbitMQ server. In that case, tests will fail and the fallback server won't work.

## Fallback server

The fallback server watch topics, and send the default image and text if there is no activity on a topics for a configurable amount of time. It also takes care of logging all messages (who are forwarded to the PlugIt server). It's connected directly to the RabbitMQ server.

Only one instance of the fallback server should be running at one time. The command to start it is `python fallback.py`.

## Test script

A testing unit is available to tests the RadioVis server and the fallback deamon. It's use _node_. All tests can simply be run using `nosetests`. More details are available in the nose documentation. All tests are inside the file `test.py`.

For testing, a special RadioDns class is used, faking call to the PlugIt API with testing values.

# General architecture

![Image](../architecture-radiovis.png?raw=true)

## Fallback

The fallback process take care of everything related to the watchdog feature and logging. 4 process are spawn.

### get_channels_threads
This process retrieve the list of topics from the PlugIt server.

### connect_to_rabbitmq
This process ensure we're connected to the RabbitMQ server.

### checks_channels
This process check if a topics didn't receive a message for a long time and send the default media if needed.

### cleanup_logs
This process takes care of cleaning logs

## RabbitMQ

The Rabbitmq process take care of the communication with the RabbitMQ server. It connects to the main exchange, and consume message, broadcasting them to all listening process.

## RadioDns

The RadioDns class takes care of communications to the PlugIt API server, allowing call e.g. for authentication, listing of topics, etc.

## Stomp

The Stomp class represent a Stomp connection. It takes care of communications with them, allowing login, subscriptions and messages management.

## Server

The server takes care of incoming Stomp connections, spawning a stomp server for each new connection and registering them to the RabbitMQ process. It also initializes everything at the startup.

# Config

The config is set in`side `config.py`. A base can be found in `config.py.dist`. Available options are :

### General

#### LOG_LEVEL
The level of logs message to display.

#### STOMP_IP
Listening IP for the stomp server

#### STOMP_PORT
Listening port for the stomp server

#### API_URL
URL for API of the PlugIt server

#### CACHE_OPTS
Caching options, see http://beaker.readthedocs.org/en/latest/configuration.html#configuration

### RabbitMQ

#### RABBITMQ_LOOPBACK
If set to true, don't use rabbitmq, but just send messages back! (For debugging)

#### RABBITMQ_HOST
The RabbitMQ host

#### RABBITMQ_PORT
The RabbitMQ port

#### RABBITMQ_USER
The RabbitMQ user

#### RABBITMQ_PASSWORD
The RabbitMQ password

#### RABBITMQ_VHOST
The RabbitMQ vhost

#### RABBITMQ_DEBUG
If we connect to RabbitMQ using debug mode

#### RABBITMQ_EXCHANGE
The name of the RabbitMQ exchange

### Fallback server

#### FB_CHANNEL_CACHE
Seconds to cache the channel list 

#### FB_QUEUE
Persistant queue 

#### FB_FALLBACK_CHECK
The time when we check for timeouted channels. (Each FB_FALLBACK_CHECK seconds)

#### FB_FALLBACK_TIME
The time before a channel is dead

#### FB_IMAGE_LOCATIONS
The base URL for default images (The PlugIt frontend)

#### FB_LOGS_MAX_AGE
The maximum number of seconds a log entry is kept

#### FB_LOGS_CLEANUP 
When logs are cleaned

### Testing

#### TEST_TOPICS
A list of topics for testing

#### TEST_ECC
A list of CC=>GCC for testing

#### TEST_ECC_TOPIC_GCC
A GCC topic for testing

#### TEST_ECC_TOPIC_CC
The CC equivalent topic for testing

#### TEST_WATCHDOG_TOPIC 
The list of topics for the fallback server

#### TEST_FB_FALLBACK_CHECK
_FB_FALLBACK_CHECK_ for testing

#### TEST_FB_FALLBACK_TIME
_FB_FALLBACK_TIME_ for testing

#### TEST_FB_QUEUE
_FB_QUEUE_ for testing

#### TEST_FB_LOGS_CLEANUP
_FB_LOGS_CLEANUP_ for testing

#### TEST_CHANNEL_DEFAULT
Default values for a channel for testing
