import os
import subprocess
import time

import mock
import pytest

import SPI
import SPI.actions
import SPI.event_listener.ORM_events_listeners
import config
from server import db_setup
from tests.SPI_generator.utils import create_handler


@pytest.fixture()
def create_mocks():
    version_1 = mock.Mock()
    version_3 = mock.Mock()
    create_handler(version_1, version_3)
    return version_1, version_3


def teardown_db():
    subprocess.call(args="docker-compose -f docker-compose-test.yml down", shell=True)


@pytest.fixture(scope="session")
def actor_setup():
    config.SPI_GENERATION_INTERVAL = 0.05
    time.sleep(5)
    return SPI.event_listener.ORM_events_listeners.spi_generator_manager


@pytest.fixture(scope="session")
def setup_db():
    teardown_db()
    subprocess.call(args="docker-compose -f docker-compose-test.yml up -d", shell=True)
    os.chdir("../")
    db_setup()
    os.chdir("tests")
    yield None
    teardown_db()
    SPI.event_listener.ORM_events_listeners.spi_generator_manager.stop()
