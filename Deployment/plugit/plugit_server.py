from fabric.api import sudo, run, task, env, settings, put, cd
import config
import utils

from fabric.contrib.files import upload_template, append

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
    mysql_execute("CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;" % (config.MYSQL_DATABSE,), "root", config.MYSQL_PASSWORD)


@task
def create_user():
    """Create the mysql suer"""
    mysql_execute("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (config.MYSQL_USER, config.MYSQL_PASSWORD), "root", config.MYSQL_PASSWORD)
    mysql_execute("GRANT ALL ON %s.* TO '%s'@'localhost'; FLUSH PRIVILEGES;" % (config.MYSQL_DATABSE, config.MYSQL_USER), "root", config.MYSQL_PASSWORD)


@task
def install_pip_dependencies():
    """Install the PIP_DEPENDENCIES for the project
    """
    put(conf('pip_requirements.txt'), 'pip_requirements.txt')
    sudo('pip install -r pip_requirements.txt')
    run('rm pip_requirements.txt')


@task
def git_init():
    """Init the git repository"""

    # Copy the deploy key
    put(config.GIT_PRIV_KEY, '~/.ssh/id_rsa')
    run('chmod 600 ~/.ssh/id_rsa')

    # To avoid testing of the server key (who ask a question)
    append('~/.ssh/config', "Host github.com\n\tStrictHostKeyChecking no\n")

    # Init the repo in ~/gitrepo and pull the folder with the django application
    run('git init ~/gitrepo-plugit')
    with cd('~/gitrepo-plugit'):
        run('git remote add -m ' + config.GIT_BRANCH + ' origin ' + config.GIT_REPO)
        run('git config core.sparsecheckout true')
        append(".git/info/sparse-checkout", config.GIT_PLUGITDIR)
        run('git pull origin ' + config.GIT_BRANCH)


@task
def pull_code():
    """Pull the latest version from the git repository"""
    with cd('~/gitrepo-plugit'):
        run('git pull origin ' + config.GIT_BRANCH)


@task
def configure():
    """Configure apache and the flask server"""

    upload_template(conf('config.py'), '~/gitrepo-plugit/' + config.GIT_PLUGITDIR + 'config.py', {
        'PLUGIT_API_URL': config.PLUGIT_API_URL,
        'SQLALCHEMY_URL': config.SQLALCHEMY_URL,
        'API_SECRET': config.API_SECRET,
        'API_BASE_URL': config.API_BASE_URL,
        'API_ALLOWD_IPS': config.API_ALLOWD_IPS
    })

    # Disable default site
    sudo('a2dissite default', pty=True)

    # Put our config and enable it
    put(conf('apache.conf'), 'apache.conf')
    sudo('mv apache.conf /etc/apache2/sites-available/')
    sudo('a2ensite apache.conf', pty=True)


@task
def restart_apache():
    """Restart apache"""
    sudo("service apache2 restart")


@task
def update_database():
    """Update database to the lastest version"""
    with cd('~/gitrepo-plugit/' + config.GIT_PLUGITDIR):
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
    install_logstash()


@task
def update():
    """Upgrade code to the latest version"""
    pull_code()
    update_database()
    restart_apache()
