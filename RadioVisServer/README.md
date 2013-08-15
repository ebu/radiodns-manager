RadioVisServer
==============

The RadioVisServer is an implementation of a RadioVis server in Python. Only the Stomp mode is available.

For scalability, the server is connected to a RabbitMq server. It's possible to run multiples instances of the server (sharing one RabbitMq server), allowing more RadioVis client to be connected.

# Dependencies

The python dependencies are:

* dnspython (BSD-style license)
* haigha (BSD license)
* gevent (MIT license)
* greenlet (MIT license)
* requests (Apache2 license)
* beaker (BSD license)
* nose (for tests, LGPL license)
* psutil (for tests, BSD license)

You can install them using `pip install _package_`. On Windows, gevent can be found [here](https://pypi.python.org/pypi/gevent#downloads), greentlet [here](http://www.lfd.uci.edu/%7Egohlke/pythonlibs/#greenlet) and psutils [here](https://code.google.com/p/psutil/downloads/detail?name=psutil-1.0.1.win32-py2.7.exe&can=2&q=)

# Parts

There is 3 mains parts: The RadioVis server, the fallback server and the test script

## RadioVis server

This part takes care of connection to RadioVis clients and forwarding of messages. This can be started using `python server.py`. Multiple instances can be ran.

It's possible, for debugging, to run the server without a RabbitMq server. In that case, tests will fail and the fallback server won't work.

## Fallback server

The fallback server watch topics, and send the default image and text if there is no activity on a topics for a configurable amount of time. It also takes care of logging all messages (who are forwarded to the PlugIt server). It's connected directly to the RabbitMq server.

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
This process ensure we're connected to the RabbitMq server.

### checks_channels
This process check if a topics didn't receive a message for a long time and send the default media if needed.

### cleanup_logs
This process takes care of cleaning logs

## RabbitMq

The Rabbitmq process take care of the communication with the RabbitMq server. It connects to the main exchange, and consume message, broadcasting them to all listening process.

## RadioDns

The RadioDns class takes care of communications to the PlugIt API server, allowing call e.g. for authentication, listing of topics, etc.

## Stomp

The Stomp class represent a Stomp connection. It takes care of communications with them, allowing login, subscriptions and messages management.

## Server

The server takes care of incoming Stomp connections, spawning a stomp server for each new connection and registering them to the RabbitMq process. It also initializes everything at the startup.

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

### RabbitMq

#### RABBITMQ_LOOPBACK
If set to true, don't use rabbitmq, but just send messages back! (For debugging)

#### RABBITMQ_HOST
The RabbitMq host

#### RABBITMQ_PORT
The RabbitMq port

#### RABBITMQ_USER
The RabbitMq user

#### RABBITMQ_PASSWORD
The RabbitMq password

#### RABBITMQ_VHOST
The RabbitMq vhost

#### RABBITMQ_DEBUG
If we connect to RabbitMq using debug mode

#### RABBITMQ_EXCHANGE
The name of the RabbitMq exchange

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
