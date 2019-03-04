import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED, EVENT_SI_PI_DELETED
from models import Clients, ServiceProvider
from tests.conftest import create_mocks_manually


def test_client_create(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, _ = create_mocks

    client = create_client(session, -1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


def test_client_update(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, _ = create_mocks

    client = update_client(session, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


def test_client_delete(setup_db, actor_setup):
    session = setup_db

    client = create_client(session, -1, "mysuperclient")
    on_si_changed, on_pi_changed = create_mocks_manually()
    delete_client(session, 2)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_DELETED,
        ServiceProvider.query.filter_by(id=2).first(),
        client.identifier,
    )


# ============ UTILITIES ============
def create_client(session, orga, name="test"):
    client = Clients()
    client.orga = orga
    client.email = name + "@test.com"
    client.name = name
    client.identifier = name + "id"

    session.add(client)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return client


def update_client(session, id, name="test2"):
    client = Clients.query.filter_by(id=id).first()
    client.email = name + "@test.com"
    client.name = name
    client.identifier = name + "id"
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return client


def delete_client(session, id):
    client = Clients.query.filter_by(id=id).first()
    session.delete(client)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
