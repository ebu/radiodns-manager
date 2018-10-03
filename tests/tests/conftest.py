import logging
import os
import random
import subprocess
import time

import pytest
import requests
from selenium import webdriver
from sqlalchemy import create_engine

random.seed(9001)

# options to connect to test proxy.
TEST_PROXY_PORT = int(os.environ.get('TEST_PROXY_PORT', '4000'))
TEST_PROXY_URL = """http://{host}:{port}/plugIt/""".format(
    host=os.environ.get('TEST_PROXY_HOSTNAME', '127.0.0.1'),
    port=TEST_PROXY_PORT
)

# url to connect to RadioDNS service
TEST_RADIO_DNS_PORT = int(os.environ.get('TEST_RADIO_DNS_PORT', '5000'))
TEST_RADIO_DNS_URL = """http://{host}:{port}/""".format(
    host=os.environ.get('TEST_RADIO_DNS_HOSTNAME', '127.0.0.1'),
    port=TEST_RADIO_DNS_PORT
)

TEST_MOCK_API_PORT = int(os.environ.get('TEST_MOCK_API_PORT', '8000'))
TEST_MOCK_API_URL = """http://{host}:{port}/""".format(
    host=os.environ.get('TEST_MOCK_API_URL', '127.0.0.1'),
    port=TEST_MOCK_API_PORT
)

# max number health checks to the docker stack the test suite will make before considering that the
# docker stack could not be started
TEST_MAX_TRIES_TO_DOCKER_TO_BOOT = int(os.environ.get('TEST_MAX_TRIES_TO_DOCKER_TO_BOOT', '60'))
# time in seconds between docker stack health checks
TEST_DOCKER_TRIES_INTERVAL = int(os.environ.get('TEST_DOCKER_TRIES_INTERVAL', '1'))
logger = logging.getLogger("RadioDNS Tests")

TEST_MYSQL_USER = os.environ.get('TEST_DOCKER_TRIES_INTERVAL', 'root')
TEST_MYSQL_PASSWORD = os.environ.get('TEST_MYSQL_PASSWORD', '1234')
TEST_MYSQL_DB_NAME = os.environ.get('TEST_MYSQL_DB_NAME', 'radiodns')

TEST_BROWSER = os.environ.get('TEST_BROWSER', "chrome")


def teardown_stack():
    """
    Kills anything running at port TEST_PROXY_PORT, TEST_RADIO_DNS_PORT and TEST_MOCK_API_PORT.
    It should be respectively the proxy, the plugit dns and the mock api.
    Also stops the test db docker container.
    """
    subprocess.run(args="docker-compose down", cwd="../../", shell=True)
    subprocess.run(args="""kill $(lsof -t -i :{port})""".format(port=TEST_PROXY_PORT), shell=True)
    subprocess.run(args="""kill $(lsof -t -i :{port})""".format(port=TEST_RADIO_DNS_PORT), shell=True)
    subprocess.run(args="""kill $(lsof -t -i :{port})""".format(port=TEST_MOCK_API_PORT), shell=True)


@pytest.fixture(scope="session")
def stack_setup():
    """
    Sets up the test stack and establish a connection to the test db for the duration of the tests.
    :return: the connection object.
    """
    logger.info("Starting docker test environment...")

    teardown_stack()  # remove any instances or docker instances of the dev stack
    subprocess.run(args="docker-compose -f docker-compose-test.yml up -d", cwd="../../", shell=True)
    subprocess.Popen(
        args="source venv/bin/activate && python manage.py runserver 0.0.0.0:4000",
        cwd="../../standalone_proxy",
        shell=True
    )
    subprocess.Popen(
        args="source venv/bin/activate && python app.py",
        cwd="../../MockApi",
        shell=True
    )
    subprocess.Popen(
        args="source venv/bin/activate && python server.py",
        cwd="../../RadioDns-PlugIt",
        shell=True
    )

    # Here we just want to poll the proxy and the mock api until we get a 403 and a 200 which means the RadioDNS plugit
    # has done db migrations and is ready with the mock API.
    for number_of_attempts in range(1, TEST_MAX_TRIES_TO_DOCKER_TO_BOOT + 1):
        try:
            proxy_request = requests.get(TEST_PROXY_URL)
            mock_api_request = requests.get(TEST_MOCK_API_URL)
            if proxy_request.status_code == 403 and mock_api_request.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass

        if number_of_attempts == TEST_MAX_TRIES_TO_DOCKER_TO_BOOT:
            raise Exception("Docker-compose or a subprocess is not running. Check the log above for any errors.")
        time.sleep(TEST_DOCKER_TRIES_INTERVAL)

    engine = create_engine(
        """mysql+pymysql://{user}:{password}@127.0.0.1:3306/{dbname}""".format(
            user=TEST_MYSQL_USER,
            password=TEST_MYSQL_PASSWORD,
            dbname=TEST_MYSQL_DB_NAME
        ), echo=False)
    conn = engine.connect()
    yield conn
    conn.close()
    teardown_stack()


subprocess.run(args="docker-compose down", cwd="../../", shell=True)


def firefox_setup():
    """
    Sets up firefox in a headless mode for remote control with selenium.
    :return: driver allowing remote control.
    """
    logger.info("Setting firefox...")
    from selenium.webdriver.firefox.options import Options
    firefox_options = Options()
    firefox_options.add_argument("-headless")
    return webdriver.Firefox(executable_path=os.path.abspath("../geckodriver"), firefox_options=firefox_options)


def chrome_setup():
    """
    Sets up chrome in a headless mode for remote control with selenium.
    :return: driver allowing remote control.
    """
    logger.info("Setting chrome...")
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(executable_path=os.path.abspath("../chromedriver"), chrome_options=chrome_options)


@pytest.fixture
def browser_setup():
    """
    Sets up a browser of your choice to be remotely controlled with selenium.
    :return: driver allowing remote control.
    """
    if TEST_BROWSER == "chrome":
        driver = chrome_setup()
        driver.get('chrome://settings/clearBrowserData')
    else:
        driver = firefox_setup()
    driver.get(TEST_PROXY_URL + "ebuio_setUser?mode=adm")
    yield driver
    driver.close()
