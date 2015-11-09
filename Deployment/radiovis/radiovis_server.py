from fabric.api import *
from fabric.contrib.files import upload_template, append, sed
from fabric.api import sudo, run, task, env, settings, put, cd
import config
import utils


# list of dependencies to install
DEPENDENCIES = ['python-gevent', 'python-setuptools', 'supervisor', 'git', 'build-essential', 'libz-dev',
                'gcc', 'python-dev', 'libmemcached-dev', 'memcached']

conf = utils.conf_path_builder(__file__)


def upgrade():
    """Upgrde the package database and the server packag
    """
    sudo("apt-get update")
    sudo("apt-get upgrade -y")


def create_logs():
    """Create log folders"""
    with settings(warn_only=True):
        sudo('mkdir /home/ubuntu/logs')
        sudo('chmod 777 /home/ubuntu/logs')


def install_dependencies():
    """Install the DEPENDENCIES for the project
    """
    sudo("apt-get install -y " + " ".join(DEPENDENCIES))
    sudo('easy_install pip')


def install_pip_dependencies():
    """Install the PIP_DEPENDENCIES for the project
    """
    put(conf('configFiles/pip_requirements.txt'), 'pip_requirements.txt')
    sudo('pip install -r pip_requirements.txt')
    run('rm pip_requirements.txt')


def git_init():
    """Init the git repository"""

    # Copy the deploy key
    put(config.RADIOVIS_GIT_KEY, '~/.ssh/id_rsa')
    run('chmod 600 ~/.ssh/id_rsa')

    # To avoid testing of the server key (who ask a question)
    append('~/.ssh/config', "Host github.com\n\tStrictHostKeyChecking no\n")

    # Init the repo in ~/gitrepo and pull the folder with the django application
    run('rm -rf ~/gitrepo-radiovis')
    run('git init ~/gitrepo-radiovis')
    with cd('~/gitrepo-radiovis'):
        run('git remote add -m ' + config.RADIOVIS_BRANCH + ' origin ' + config.RADIOVIS_REPO)
        run('git config core.sparsecheckout true')
        append(".git/info/sparse-checkout", config.RADIOVIS_FOLDER)
        run('git pull origin ' + config.RADIOVIS_BRANCH)


def pull_code():
    """Pull the latest version from the git repository"""
    with cd('~/gitrepo-radiovis'):
        run('git pull origin ' + config.RADIOVIS_BRANCH)


@task
@roles('radiovis')
def start_fallback():
    """Start the fallback server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER):
        run('supervisord -c supervisord-fallback.conf')


@task
@roles('radiovis')
def stop_fallback():
    """Stop the fallback server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER):
        run('supervisorctl -c supervisord-fallback.conf stop fallbackserver')
        run('supervisorctl -c supervisord-fallback.conf shutdown')


@task
@roles('radiovis')
def restart_fallback():
    """Restart the fallback server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER):
        run('supervisorctl -c supervisord-fallback.conf restart fallbackserver')

@task
@roles('radiovis')
def start_radiovis():
    """Start the radiovis server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER):
        run('supervisord -c supervisord-radiovis.conf')


@task
@roles('radiovis')
def stop_radiovis():
    """Stop the radiovis server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER):
        run('supervisorctl -c supervisord-radiovis.conf stop radiovisserver')
        run('supervisorctl -c supervisord-radiovis.conf shutdown')


@task
@roles('radiovis')
def restart_radiovis():
    """Restart the radiovis server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER):
        run('supervisorctl -c supervisord-radiovis.conf restart radiovisserver')


def configure():
    """Configure radiovisserver and supervisord"""

    # Just upload the template with our settings
    upload_template('radiovis/configFiles/config.py',
                    '~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER + '/config.py',
                    context={
                        'RADIOVIS_LOG_LEVEL': config.RADIOVIS_LOG_LEVEL,
                        'RADIOVIS_RABBITMQ_HOST': config.RADIOVIS_RABBITMQ_HOST,
                        'RABBITMQ_USER': config.RABBITMQ_USER,
                        'RABBITMQ_PASS': config.RABBITMQ_PASS,
                        'RADIOVIS_RABBITMQ_EXCHANGE': config.RADIOVIS_RABBITMQ_EXCHANGE,
                        'RADIOVIS_RABBITMQ_FALLBACKQUEUE': config.RADIOVIS_RABBITMQ_FALLBACKQUEUE,
                        'RADIOVIS_API_URL': config.RADIOVIS_API_URL,
                        'PLUGIT_IMAGE_LOCATIONS': config.PLUGIT_IMAGE_LOCATIONS,
                        'PLUGIT_PUBLIC_ACCESS': config.PLUGIT_PUBLIC_ACCESS,
                        'STATS_GAUGE_APPNAME': config.STATS_GAUGE_APPNAME,
                        'STATS_GAUGE_NB_CLIENTS': config.STATS_GAUGE_NB_CLIENTS,
                        'STATS_GAUGE_NB_SUBSCRIPTIONS': config.STATS_GAUGE_NB_SUBSCRIPTIONS,
                        'STATS_COUNTER_NBMESSAGE_SEND': config.STATS_COUNTER_NBMESSAGE_SEND,
                        'STATS_COUNTER_NBMESSAGE_SEND_BY_WATCHDOG': config.STATS_COUNTER_NBMESSAGE_SEND_BY_WATCHDOG,
                        'STATS_COUNTER_NBMESSAGE_RECV': config.STATS_COUNTER_NBMESSAGE_RECV,
                        'RADIOVIS_monitoring': config.RADIOVIS_monitoring
                    }, use_jinja=True)

    upload_template(conf('configFiles/supervisord-radiovis.conf'),
                    '~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER + '/supervisord-radiovis.conf', {

        })

    upload_template(conf('configFiles/supervisord-fallback.conf'),
                    '~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER + '/supervisord-fallback.conf', {

        })


def deploy():
    """Deploy a radiovis server on the current host
    """
    upgrade()
    install_dependencies()
    install_pip_dependencies()
    create_logs()
    git_init()
    configure()
    restart_radiovis()
    setup_startup_cronjobs()


def setup_startup_cronjobs():
    """Setup statup cronjobs to start radiovis server and fallback automaticaly"""
    run('touch /tmp/crondump')
    with settings(warn_only=True):
        run('crontab -l > /tmp/crondump')

    append('/tmp/crondump',
           '@reboot cd ~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER + ' && supervisord -c supervisord-radiovis.conf')
    append('/tmp/crondump',
           '@reboot cd ~/gitrepo-radiovis/' + config.RADIOVIS_FOLDER + ' && supervisord -c supervisord-fallback.conf')

    run('crontab /tmp/crondump')


def deploy_withfallback():
    """Deploy a radiovis server on the current host, with fallback server
    """
    deploy()
    restart_fallback()


def update():
    """Upgrade code to the latest version"""
    install_dependencies()
    install_pip_dependencies()
    pull_code()
    restart_radiovis()


def update_withfallback():
    """Upgrade code to the latest version, including fallback server"""
    update()
    restart_radiovis()
    restart_fallback()
