## 1) Deployment
CONFIG_DIR='configFiles'


## 2) SSH (AWS) (used by fabfile.py)
SSH_USER='...'
SSH_PRIVKEY='...pem'
USE_SSH_CONFIG = False
AWS_VM_TAG = 'io-radiodns'
#AWS_VM_TAG = 'io-radiovis'
AWS_REGION = 'eu-west-1'
# with permissions to get_list
AWS_ACCESS_KEY = '...'
AWS_SECRET_KEY = '...'


## 3) RadioDns-PlugIt (to complete RadioDns-Plugit/config.py)

# 3.1) RadioDns Git (used by "fab plugit_server.git_init")
GIT_PRIV_KEY = '...'
GIT_REPO = 'https://github.com/ebu/radiodns-plugit.git'
GIT_BRANCH = 'develop'
GIT_PLUGITDIR = 'RadioDns-PlugIt/'

# 3.2) PlugIt (used by "fab plugit_server.configure")

PLUGIT_API_URL = 'http://127.0.0.1:8000/plugIt/ebuio_api/'
SQLALCHEMY_URL = 'mysql://plugit_user:plugit_password@localhost/plugit_db'
API_SECRET = 'my_api_secret'
API_BASE_URL = '/'
API_ALLOWD_IPS = ['0.0.0.0/0']

# 3.3) MySQL (used by "fab plugit_server.create_database", "fab plugit_server.create_user")
MYSQL_DATABSE = 'plugit_db'
MYSQL_USER = 'plugit_user'
MYSQL_PASSWORD = 'plugit_password'

# 3.4) Alembic (fab plugit_server.update_database)
PI_ALLOWED_NETWORKS = ['0.0.0.0/0']

# 3.5) Sentry
SENTRY_DSN = 'http://public:secret@example.com/1'


## 4) RadioVisServer (to complete RadioVisServer/config.py)

# 4.1) RabbitMQ (fab rabbitmq_server.setup_auth)
RABBITMQ_USER = 'rabbitmq_user'
RABBITMQ_PASS = 'rabbitmq_password'

# 4.2) RadioVis Git (fab radiovis_server.git_init)
GIT_RADIOVISDIR = 'RadioVisServer/'

# 4.3) RadioVis (fab radiovis_server.configure)
#PLUGIT_PUBLIC_ACCESS = ''
RADIOVIS_RABBITMQ_HOST = '127.0.0.1'
RADIOVIS_RABBITMQ_QUEUE = ''
RADIOVIS_API_URL = 'http://radiodns.mydomain.org%saction/radiovis/api/%s/' % (API_BASE_URL, API_SECRET)
RADIOVIS_LOG_LEVEL = ''
