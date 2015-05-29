SSH_USER = ''
SSH_PRIVKEY = ''

USE_SSH_CONFIG = False

RABBITMQ_USER = ''
RABBITMQ_PASS = ''

RADIOVIS_RABBITMQ_HOST = ''
RADIOVIS_RABBITMQ_QUEUE = ''

RADIOVIS_API_URL = ''

RADIOVIS_LOG_LEVEL = ''

STATS_GAUGE_APPNAME = ''
STATS_GAUGE_NB_CLIENTS = 'nb_tcp_clients'
STATS_GAUGE_NB_SUBSCRIPTIONS = 'subscriptions'
STATS_COUNTER_NBMESSAGE_SEND = 'msg_send'
STATS_COUNTER_NBMESSAGE_SEND_BY_WATCHDOG = 'msg_send_watchdog'
STATS_COUNTER_NBMESSAGE_RECV = 'msg_recv'

RADIOVIS_monitoring = {
    'enabled':  True,
    'host':     'log.ebu.io',
    'port':     5672,
    'user':     'radiovis',
    'password': 'PZNi77GDmkER73qCmmGOnoJiu9s=',
    'vhost':    '/',
    'debug':    True,
    'exchange': 'monitoring.buffer',
    'queue':    'radiovis',
    'server_id': 'b502408f-94c2-4cdf-aa1b-5243a7314cf2'
}

GIT_REPO = ''
GIT_BRANCH = ''
GIT_PRIV_KEY = ''

GIT_RADIOVISDIR = ''

CONFIG_DIR = ''

MYSQL_DATABASE = ''
MYSQL_PASSWORD = ''

PLUGIT_PUBLIC_ACCESS = ''

AWS_VM_TAG = 'io-radiodns'
AWS_REGION = ''
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
