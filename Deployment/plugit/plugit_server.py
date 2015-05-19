from fabric.api import *
from fabric.contrib.files import upload_template, append, sed
import config
import utils


# list of dependencies to install
DEPENDENCIES = ['python-gevent', 'python-setuptools', 'debconf-utils', 'python-mysqldb',  'apache2', 'libapache2-mod-wsgi', 'git', 'python-imaging']

conf = utils.conf_path_builder(__file__)


def mysql_execute(sql, user, password):
    """Executes passed sql command using mysql shell."""

    sql = sql.replace('"', r'\"')
    return run('echo "%s" | mysql --user="%s" --password="%s"' % (sql, user, password))


@task
def upgrade():
    """Upgrde the package database and the server packag
    """
    sudo("apt-get update")
    sudo("apt-get upgrade -y")


@task
def create_logs():
    """Create log folders"""
    with settings(warn_only=True):
        sudo('mkdir /home/ubuntu/logs')
        sudo('chmod 777 /home/ubuntu/logs')


@task
def install_dependencies():
    """Install the DEPENDENCIES for the project
    """
    sudo("apt-get install -y " + " ".join(DEPENDENCIES))
    sudo('easy_install pip')

    debconf_defaults = [
        "mysql-server-5.5 mysql-server/root_password_again password %s" % (config.MYSQL_PASSWORD,),
        "mysql-server-5.5 mysql-server/root_password password %s" % (config.MYSQL_PASSWORD,),
    ]

    sudo("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

    # Install mysql
    sudo('aptitude install -y mysql-server')


@task
def create_database():
    """Create the mysql database"""
    mysql_execute("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;" % (config.MYSQL_DATABASE,), "root", config.MYSQL_PASSWORD)


@task
def create_user():
    """Create the mysql suer"""
    with settings(warn_only=True):
        mysql_execute("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (config.MYSQL_USER, config.MYSQL_PASSWORD), "root", config.MYSQL_PASSWORD)
        mysql_execute("GRANT ALL ON %s.* TO '%s'@'localhost'; FLUSH PRIVILEGES;" % (config.MYSQL_DATABASE, config.MYSQL_USER), "root", config.MYSQL_PASSWORD)


@task
def install_pip_dependencies():
    """Install the PIP_DEPENDENCIES for the project
    """
    put(conf('configFiles/pip_requirements.txt'), 'pip_requirements.txt')
    sudo('pip install -r pip_requirements.txt')
    run('rm pip_requirements.txt')


@task
def git_init():
    """Init the git repository"""

    # Copy the deploy key
    put(config.RADIODNS_GIT_KEY, '~/.ssh/id_rsa')
    run('chmod 600 ~/.ssh/id_rsa')

    # To avoid testing of the server key (who ask a question)
    append('~/.ssh/config', "Host github.com\n\tStrictHostKeyChecking no\n")

    # Init the repo in ~/gitrepo-plugit and pull the folder with the flask application
    run('rm -rf ~/gitrepo-plugit')
    run('git init ~/gitrepo-plugit')
    with cd('~/gitrepo-plugit'):
        run('git remote add -m ' + config.RADIODNS_BRANCH + ' origin ' + config.RADIODNS_REPO)
        run('git config core.sparsecheckout true')
        append(".git/info/sparse-checkout", config.RADIODNS_FOLDER)
        run('git pull origin ' + config.RADIODNS_BRANCH)


@task
def pull_code():
    """Pull the latest version from the git repository"""
    with cd('~/gitrepo-plugit'):
        run('git pull origin ' + config.RADIODNS_BRANCH)


@task
def configure():
    """Configure apache and the flask server"""

    upload_template('plugit/configFiles/config.py',
                    '~/gitrepo-plugit/' + config.RADIODNS_FOLDER + '/config.py',
                    context={'PLUGIT_API_URL': config.RADIODNS_PLUGIT_API_URL,
                             'SQLALCHEMY_URL': config.RADIODNS_SQLALCHEMY_URL,
                             'API_SECRET': config.RADIODNS_API_SECRET,
                             'PI_BASE_URL': config.RADIODNS_API_BASE_URL,
                             'PI_ALLOWED_NETWORKS': config.RADIODNS_API_ALLOWED_IPS,
                             'SENTRY_DSN': config.RADIODNS_SENTRY_DSN,
                             'AWS_ACCESS_KEY': config.RADIODNS_AWS_ACCESS_KEY,
                             'AWS_SECRET_KEY': config.RADIODNS_AWS_SECRET_KEY,
                             'PLUGIT_PUBLIC_ACCESS': config.PLUGIT_PUBLIC_ACCESS,
                             'RADIOVIS_RABBITMQ_FALLBACKQUEUE': config.RADIOVIS_RABBITMQ_FALLBACKQUEUE
                            }, use_jinja=True)

    # Disable default site
    sudo('a2dissite 000-default.conf', pty=True)

    # Put our config and enable it
    put(conf('configFiles/apache.conf'), 'apache.conf')
    sudo('mv apache.conf /etc/apache2/sites-available/')
    sudo('a2ensite apache.conf', pty=True)

    # Set rights on upload folder
    folder = '~/gitrepo-plugit/%s' % config.RADIODNS_FOLDER
    with cd(folder):
        sudo('chmod -R 777 media/uploads')


@task
def restart_apache():
    """Restart apache"""
    sudo("service apache2 restart")


@task
def update_database():
    """Update database to the lastest version"""
    with cd('~/gitrepo-plugit/' + config.RADIODNS_FOLDER):
        run('alembic upgrade head')


@task
def install_logstash():
    """Install logstash"""

    sudo('apt-get install -y default-jre')

    sudo('mkdir /home/ubuntu/logstash/')
    with cd('/home/ubuntu/logstash/'):
        sudo('wget https://download.elasticsearch.org/logstash/logstash/logstash-1.2.2-flatjar.jar')
        put(conf('shipper.conf'), '/home/ubuntu/logstash/shipper.conf', use_sudo=True)

    put(conf('logstash.conf'), '/etc/init/logstash.conf', use_sudo=True)
    sudo('service logstash start')


@task
def deploy():
    """Deploy a plugit server on the current host
    """
    upgrade()
    install_dependencies()
    install_pip_dependencies()
    create_logs()
    git_init()
    configure()
    create_database()
    create_user()
    update_database()
    restart_apache()
    # install_logstash()


@task
def update():
    """Upgrade code to the latest version"""
    pull_code()
    update_database()
    restart_apache()
