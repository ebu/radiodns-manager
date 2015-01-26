from haigha.connection import Connection
from haigha.message import Message

import logging
import time
import config
import sys
import Queue
import json
import uuid

def skipIfDisabled(f):
  def decorator(self, *args, **kwargs):
    if self.enabled:
      f(self, *args, **kwargs)
  return decorator

class Monitoring():
  """This class manages the connection to the monitoring system"""


  def __init__(self):
    self.logger = logging.getLogger('radiovisserver.monitoring')
    self.buffer = Queue.Queue()
    self.enabled = self.isEnabled()
    self.connection = None
    self.server_id = config.monitoring['server_id']


  @skipIfDisabled
  def log(self, label, content, client='', metadata='', timestamp=None):
    """ Log a single event """
    if timestamp == None:
      timestamp = time.time()
    self.buffer.put({ 'type': 'log', 'label': label, 'content': content, 'client': client, 'metadata': metadata, 'timestamp': timestamp, 'server': self.server_id })


  @skipIfDisabled
  def count(self, label, metadata='', timestamp=None):
    """ Log a single event """
    if timestamp == None:
      timestamp = time.time()

    self.buffer.put({ 'type': 'count', 'label': label, 'timestamp': timestamp, 'server': self.server_id })


  @skipIfDisabled
  def gauge(self, label, level, metadata='', timestamp=None):
    """ Log an aggregated value """
    if timestamp == None:
      timestamp = time.time()

    self.buffer.put({ 'type': 'gauge', 'label': label, 'level': level, 'timestamp': timestamp, 'server': self.server_id })

  def run(self):
    """Thread with connection to send monitoring data"""

    if not self.isEnabled():
      self.logger.info("Monitoring disabled by config.py")
      return
    else:
      self.logger.info("Monitoring enabled by config.py")


    while True:
      try:
        time.sleep(1)
        self.logger.debug("Connecting to RabbitMQ (user=%s,host=%s,port=%s,vhost=%s)" % (config.monitoring['user'],
                                                                                         config.monitoring['host'],
                                                                                         config.monitoring['port'],
                                                                                         config.monitoring['vhost']))
        self.connection = Connection(user = config.monitoring['user'],
                                     password = config.monitoring['password'],
                                     vhost = config.monitoring['vhost'],
                                     host = config.monitoring['host'],
                                     port = config.monitoring['port'],
                                     debug = config.monitoring['debug'])

        self.logger.debug("Creating the channel")
        self.ch = self.connection.channel()

        # Name will come from a callback
        global queue_name
        queue_name = None

        queue_name = config.monitoring['queue']

        self.logger.debug("Creating the queue")
        self.ch.queue.declare(queue=queue_name, durable=True, auto_delete=False, nowait=False)

        for i in range(0, 10):  # Max 10 seconds
          if queue_name is None:
            time.sleep(1)

        if queue_name is None:
          self.logger.warning("Queue creation timeout !")
          raise Exception("Cannot create queue !")

        self.logger.debug("Binding the exchange %s" % (config.monitoring['exchange'], ))
        self.ch.queue.bind(queue_name, config.monitoring['exchange'], '')

        self.logger.debug("Ready, waiting for monitoring data")
        while True:
          data = json.dumps(self.buffer.get(block=True, timeout=None))
          self.logger.debug("Publishing: ", data)
          headers = {}
          headers['when'] = str(int(time.time()))
          self.ch.basic.publish(Message(data, application_headers=headers), config.monitoring['exchange'], '')

      except Exception as e:
        self.logger.error("Error in run: %s" % (e, ))
        self.logger.error('Monitoring connection failed. Reconnecting in 30sec')
      finally:
        if self.connection:
          self.logger.info('connection closed')
          self.connection.close()

        time.sleep(30)

  def isEnabled(self):
    return hasattr(config, 'monitoring') and config.monitoring['enabled']