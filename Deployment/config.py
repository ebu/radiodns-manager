SSH_USER = 'ubuntu'
SSH_PRIVKEY = 'sshKeys/ebu-io-dev.pem'

USE_SSH_CONFIG = False

RABBITMQ_USER = 'masterofrabbits'
RABBITMQ_PASS = 'Ahhce7jaiLofcVei5Oshiqqqdah8Sha6_eey0UoTe!Cee4yaiR1fohc'

RADIOVIS_RABBITMQ_HOST = 'radiovis.ebu.io'
RADIOVIS_RABBITMQ_QUEUE = 'amq.fanout'


API_SECRET = 'xiGh8siWDoog5aQueem0voF0quuo2ahR'
API_BASE_URL = '/thii5Themie3sa3Dfahp4Liaoopa8Quotahp3eZu/'
API_ALLOWD_IPS = "['127.0.0.1/32', '193.43.93.1/32', '54.229.80.247/32']"

RADIOVIS_API_URL = 'http://127.0.0.1' + API_BASE_URL + 'action/radiovis/api/' + API_SECRET + '/'

RADIOVIS_LOG_LEVEL = 'DEBUG'


GIT_REPO = 'git@github.com:ebu/radiodns-plugit.git'
GIT_BRANCH = 'develop'
GIT_PRIV_KEY = 'sshkeys/ebu-io-dev-deploy-2.pem'

GIT_RADIOVISDIR = 'RadioVisServer/'
GIT_PLUGITDIR = 'RadioDns-PlugIt/'

CONFIG_DIR = 'configFiles'

MYSQL_USER = 'radiodns'
MYSQL_DATABSE = 'radiodns'
MYSQL_PASSWORD = 'thisisasecretpassword55'

PLUGIT_API_URL = 'http://ebu.io/plugit/Mrh5HQtTFXO6ZdJtm9tTmfDPPZ4S35Mp/1/'

SQLALCHEMY_URL = 'mysql://' + MYSQL_DATABSE + ':' + MYSQL_PASSWORD + '@localhost/' + MYSQL_USER

PLUGIT_PUBLIC_ACCESS = 'http://ebu.io/plugit/1/'
