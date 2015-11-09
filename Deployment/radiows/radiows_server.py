from fabric.api import *
from fabric.contrib.files import upload_template, append, sed
from fabric.api import sudo, run, task, env, settings, put, cd
import config
import utils


# list of dependencies to install
DEPENDENCIES = ['python-gevent', 'python-setuptools', 'supervisor', 'git', 'build-essential', 'libz-dev',
                'gcc', 'python-dev', ]

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
    put(config.WS_GIT_KEY, '~/.ssh/id_rsa')
    run('chmod 600 ~/.ssh/id_rsa')

    # To avoid testing of the server key (who ask a question)
    append('~/.ssh/config', "Host github.com\n\tStrictHostKeyChecking no\n")

    # Init the repo in ~/gitrepo and pull the folder with the django application
    run('rm -rf ~/gitrepo-radiows')
    run('git init ~/gitrepo-radiows')
    with cd('~/gitrepo-radiows'):
        run('git remote add -m ' + config.WS_BRANCH + ' origin ' + config.WS_REPO)
        run('git config core.sparsecheckout true')
        append(".git/info/sparse-checkout", config.WS_FOLDER)
        run('git pull origin ' + config.WS_BRANCH)


def pull_code():
    """Pull the latest version from the git repository"""
    with cd('~/gitrepo-radiows'):
        run('git pull origin ' + config.WS_BRANCH)


@task
@roles('radiowsserver')
def start_simpleserver():
    """Start the fallback server (using supervisord)"""
    with cd('~/gitrepo-radiows/website'):
        run('supervisord -c supervisord-simpleserver.conf')


@task
@roles('radiowsserver')
def stop_simpleserver():
    """Stop the simpleserver server (using supervisord)"""
    with cd('~/gitrepo-radiows/website'):
        run('supervisorctl -c supervisord-simpleserver.conf stop simpleserver')
        run('supervisorctl -c supervisord-simpleserver.conf shutdown')


@task
@roles('radiowsserver')
def restart_simpleserver():
    """Restart the simpleserver server (using supervisord)"""
    with cd('~/gitrepo-radiows/website'):
        run('supervisorctl -c supervisord-simpleserver.conf restart simpleserver')


@task
@roles('radiowsserver')
def start_websocketserver():
    """Start the websocketserver server (using supervisord)"""
    with cd('~/gitrepo-radiows/' + config.WS_FOLDER):
        run('supervisord -c supervisord-websocketserver.conf')


@task
@roles('radiowsserver')
def stop_websocketserver():
    """Stop the websocketserver server (using supervisord)"""
    with cd('~/gitrepo-radiows/' + config.WS_FOLDER):
        run('supervisorctl -c supervisord-websocketserver.conf stop websocketserver')
        run('supervisorctl -c supervisord-websocketserver.conf shutdown')


@task
@roles('radiowsserver')
def restart_websocketserver():
    """Restart the websocketserver server (using supervisord)"""
    with cd('~/gitrepo-radiows/' + config.WS_FOLDER):
        run('supervisorctl -c supervisord-websocketserver.conf restart websocketserver')



def configure():
    """Configure websocketserver"""

    # Just upload the template with our settings
    # upload_template('radiows/configFiles/config.py',
    #                 '~/gitrepo-radiows/' + config.WS_FOLDER + '/config.py',
    #                 context={
    #                     'WS_monitoring': config.WS_monitoring,
    #                 }, use_jinja=True)

    # upload_template(conf('configFiles/supervisord-ws.conf'),
    #                 '~/gitrepo-ws/' + config.W_FOLDER + '/supervisord-ws.conf', {
    #
    #     })
    #
    # upload_template(conf('configFiles/supervisord-fallback.conf'),
    #                 '~/gitrepo-ws/' + config.WS_FOLDER + '/supervisord-fallback.conf', {
    #
    #     })


def deploy():
    """Deploy a websocketserver server on the current host
    """
    upgrade()
    install_dependencies()
    install_pip_dependencies()
    create_logs()
    git_init()
    configure()
    restart_websocketserver()
    setup_startup_cronjobs()


def setup_startup_cronjobs():
    """Setup statup cronjobs to start websocketserver automaticaly"""
    run('touch /tmp/crondump')
    with settings(warn_only=True):
        run('crontab -l > /tmp/crondump')

    append('/tmp/crondump',
           '@reboot cd ~/gitrepo-radiows/' + config.WS_FOLDER + ' && supervisord -c supervisord-websocketserver.conf')
    # append('/tmp/crondump',
    #        '@reboot cd ~/gitrepo-radiows/' + config.WS_FOLDER + ' && supervisord -c supervisord-fallback.conf')

    run('crontab /tmp/crondump')


def update():
    """Upgrade code to the latest version"""
    install_dependencies()
    install_pip_dependencies()
    pull_code()
    restart_websocketserver()

