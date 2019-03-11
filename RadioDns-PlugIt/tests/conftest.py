import os
import subprocess
import time

import mock
import pytest

import SPI
import SPI.actions
import SPI.event_listener.ORM_events_listeners
import config
from db_utils import db
from server import db_setup
from tests.utils import create_handler


def create_mocks_manually():
    on_si_changed = mock.Mock()
    on_pi_changed = mock.Mock()
    create_handler(on_si_changed, on_pi_changed)
    return on_si_changed, on_pi_changed


@pytest.fixture()
def create_mocks():
    return create_mocks_manually()


def teardown_db():
    subprocess.call(args="docker-compose -f docker-compose-test.yml down", shell=True)


@pytest.fixture(scope="session")
def actor_setup():
    config.USES_CDN = True
    config.SPI_GENERATION_INTERVAL = 0.2
    time.sleep(5)
    yield SPI.event_listener.ORM_events_listeners.spi_generator_manager


@pytest.fixture(scope="session")
def setup_db():
    teardown_db()
    subprocess.call(args="docker-compose -f docker-compose-test.yml up -d", shell=True)
    os.chdir("../")
    db_setup()
    os.chdir("tests")
    yield db.session
    teardown_db()
    SPI.event_listener.ORM_events_listeners.spi_generator_manager.stop()
