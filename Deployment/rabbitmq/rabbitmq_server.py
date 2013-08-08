from fabric.api import sudo, run, task, env, settings
import config

#list of dependencies to install
DEPENDENCIES = ['rabbitmq-server']

#only used for administration
RABBITMQ_NODE = "server"


@task 
def upgrade():
    """Upgrde the package database and the server packag
    """
    sudo("apt-get update")
    sudo("apt-get upgrade -y")


@task
def install_dependencies():
    """Install the DEPENDENCIES for the project
    """
    sudo("apt-get install -y " + " ".join(DEPENDENCIES))


@task
def start():
    """Start rabbit mq, this will do nothing if rabbitmq server is already running
    """
    sudo("/etc/init.d/rabbitmq-server start")


@task
def stop():
    """Stop rabbitmq without any warning
    """
    sudo("/etc/init.d/rabbitmq-server stop")


@task
def rabbitmq_ctl(*args):
    """Wrapper for the rabbitmqctl command
    """
    return sudo("rabbitmqctl " + " ".join(args))

@task
def add_user(user, password):
    """Add the user to rabbitmq, if the user already exist the password will be set again
    """
    active_users = rabbitmq_ctl("list_users")
    if user in active_users.split():
        rabbitmq_ctl("change_password", user, password)
    else:
        with settings(warn_only=True):
            rabbitmq_ctl("add_user", user, password)

@task
def setup_auth():
    """setup the admin user and the rabbitmq user in read only.
    """
    #add the admin user
    add_user(config.RABBITMQ_USER, config.RABBITMQ_PASS)
    #set  the admin permission to do everything (conf, write, read
    rabbitmq_ctl("set_permissions", "-p", "/", config.RABBITMQ_USER, '".*"', '".*"', '".*"')
    rabbitmq_ctl("set_user_tags", config.RABBITMQ_USER, "administrator")

    #Set guest permistions (read only)
    rabbitmq_ctl("set_permissions", "-p", "/", "guest", '"^amq.gen.*$"', '"^amq.gen.*$"', '".*"')
    rabbitmq_ctl("set_user_tags", "guest")


@task
def activate_management():
    sudo("rabbitmq-plugins enable rabbitmq_management")

@task
def set_permission(host, user, conf, write, read):
    """Wrapper around the permission setting for rabbitmq
    """
    rabbitmq_ctl("set_permissions", "-p", host, user, conf, write, read)


@task
def deploy():
    """Deploy a rabbit mq server on the current host
    """
    upgrade()
    install_dependencies()
    setup_auth()
    activate_management()
    stop()
    start()
