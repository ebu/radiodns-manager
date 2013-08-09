from fabric.api import sudo, run, task, env, settings, put, cd
import config
import utils

from fabric.contrib.files import upload_template, append


#list of dependencies to install
DEPENDENCIES = ['python-gevent', 'python-setuptools', 'supervisor', 'git']

conf = utils.conf_path_builder(__file__)
    
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
    run('git init ~/gitrepo-radiovis')
    with cd('~/gitrepo-radiovis'):
        run('git remote add -m ' + config.GIT_BRANCH + ' origin ' + config.GIT_REPO)
        run('git config core.sparsecheckout true')
        append(".git/info/sparse-checkout", config.GIT_RADIOVISDIR)
        run('git pull origin ' + config.GIT_BRANCH)


@task
def pull_code():
    """Pull the latest version from the git repository"""
    with cd('~/gitrepo-radiovis'):
        run('git pull origin ' + config.GIT_BRANCH)


@task
def start_radiovis():
    """Start the radiovis server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.GIT_RADIOVISDIR):
        run('supervisord -c supervisord-radiovis.conf')

@task
def stop_radiovis():
    """Stop the radiovis server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.GIT_RADIOVISDIR):
        run('supervisorctl -c supervisord-radiovis.conf stop radiovisserver')
        run('supervisorctl -c supervisord-radiovis.conf shutdown')

@task
def restart_radiovis():
    """Restart the radiovis server (using supervisord)"""
    with cd('~/gitrepo-radiovis/' + config.GIT_RADIOVISDIR):
        run('supervisorctl -c supervisord-radiovis.conf restart radiovisserver')

@task
def configure():
    """Configure radiovisserver and supervisord"""


    # Just upload the template with our settings
    upload_template(conf('config.py'), '~/gitrepo-radiovis/' + config.GIT_RADIOVISDIR + 'config.py',  {
           'RADIOVIS_LOG_LEVEL': config.RADIOVIS_LOG_LEVEL,
           'RADIOVIS_RABBITMQ_HOST': config.RADIOVIS_RABBITMQ_HOST,
           'RABBITMQ_USER': config.RABBITMQ_USER,
           'RABBITMQ_PASS': config.RABBITMQ_PASS,
           'RADIOVIS_RABBITMQ_QUEUE': config.RADIOVIS_RABBITMQ_QUEUE,
           'RADIOVIS_API_URL': config.RADIOVIS_API_URL

        })

    upload_template(conf('supervisord-radiovis.conf'), '~/gitrepo-radiovis/' + config.GIT_RADIOVISDIR + 'supervisord-radiovis.conf', {

        })


@task
def deploy():
    """Deploy a radiovis server on the current host
    """
    upgrade()
    install_dependencies()
    install_pip_dependencies()
    create_logs()
    git_init()
    configure()
    start_radiovis()


@task
def update():
    """Upgrade code to the latest version"""
    pull_code()
    restart_radiovis()