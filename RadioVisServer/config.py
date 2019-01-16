import logging
import os

LOG_LEVEL = logging.DEBUG

# If set to true, don't use rabbitmq but just send messages back !
RABBITMQ_LOOPBACK = False
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "127.0.0.1")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "/")
RABBITMQ_DEBUG = "True" == os.environ.get("RABBITMQ_DEBUG", "True")
RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE", "amq.fanout")

monitoring = {
    "enabled": "True" == os.environ.get("MONITORING_ENABLED", "True"),
    "host": os.environ.get("MONITORING_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MONITORING_PORT", 5672)),
    "user": os.environ.get("MONITORING_USER", "guest"),
    "password": os.environ.get("MONITORING_PASSWORD", "guest"),
    "vhost": os.environ.get("MONITORING_VHOST", "/"),
    "debug": "True" == os.environ.get("MONITORING_DEBUG", "True"),
    "exchange": os.environ.get("MONITORING_EXCHANGE", "monitoring.buffer"),
    "queue": os.environ.get("MONITORING_QUEUE", "radiovis"),
    "server_id": os.environ.get("MONITORING_SERVER_ID", "rabbit@radiodnsrabbitmq").strip().split(','),
}

STOMP_IP = os.environ.get("STOMP_IP", "0.0.0.0").strip().split(',')
STOMP_PORT = int(os.environ.get("STOMP_PORT", 61613))

# RadioDns plugit API
# Scheme:
# 'http://<HOST>/<API_SECRET>/action/radiovis/api/<API_SECRET>/'
API_URL = os.environ.get("RADIODNS_API_URL", "http://127.0.0.1:5000/action/radiovis/api/dev-secret/")

# http://beaker.readthedocs.org/en/latest/configuration.html#configuration
CACHE_OPTS = {
    'cache.type': 'memory',
}

MEMCACHED_HOST = os.environ.get("MEMCACHED_HOST", "127.0.0.1")

FB_CHANNEL_CACHE = int(os.environ.get("FB_CHANNEL_CACHE", 60))  # 1 minute
FB_QUEUE = os.environ.get("FB_QUEUE", "fallbacklogs")

# The time when we check for timeouted channels. (Each FB_FALLBACK_CHECK seconds)
FB_FALLBACK_CHECK = int(os.environ.get("FB_FALLBACK_CHECK", 15))
FB_FALLBACK_TIME = int(os.environ.get("FB_FALLBACK_TIME", 60))  # The time before a channel is considered dead

FB_IMAGE_LOCATIONS = os.environ.get("FB_IMAGE_LOCATIONS", "")  # Should be the public url of plugit

FB_LOGS_MAX_AGE = int(os.environ.get("FB_LOGS_MAX_AGE", 60 * 60 * 24))  # Cleanup logs if > 24h
FB_LOGS_CLEANUP = int(os.environ.get("FB_LOGS_CLEANUP", 60 * 60))  # Cleanup logs each 1h

TEST_TOPICS = ['/topic/id/tests._ebu.nowhere/topic1/', '/topic/id/tests._ebu.nowhere/topic2/']

TEST_ECC = {"ch": "4e1"}
TEST_ECC_TOPIC_GCC = "/topic/fm/4e1/ffff/99999/"
TEST_ECC_TOPIC_CC = "/topic/fm/ch/ffff/99999/"

TEST_WATCHDOG_TOPIC = [("/topic/id/tests._ebu.nowhere/topicwatchdogeg/", 1),
                       ("/topic/id/tests._ebu.nowhere/topicwatchdogegnoinfo/", 2)]

TEST_FB_FALLBACK_CHECK = 2
TEST_FB_FALLBACK_TIME = 10
TEST_FB_QUEUE = FB_QUEUE + "_testMode"
TEST_FB_LOGS_CLEANUP = 5
TEST_CHANNEL_DEFAULT = {"id": "1", "orga": "", "name": "test", "filename": "testfilename",
                        "radiotext": "testdefaultext", "radiolink": "testdefaultlink", "clean_filename": "testfilename"}

STATS_GAUGE_APPNAME = os.environ.get("STATS_GAUGE_APPNAME", "radiovis.app")
STATS_GAUGE_NB_CLIENTS = os.environ.get("STATS_GAUGE_NB_CLIENTS", "nb_tcp_cox")
STATS_COUNTER_NBMESSAGE_SENT = os.environ.get("STATS_COUNTER_NBMESSAGE_SENT", "radiovis.app.msg_sent")
STATS_COUNTER_NBMESSAGE_RECV = os.environ.get("STATS_COUNTER_NBMESSAGE_RECV", "radiovis.app.msg_recv")
