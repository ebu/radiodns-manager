import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED
from models import Channel, Clients, ServiceProvider
from tests.conftest import create_mocks_manually


def test_create_channel(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    create_channel(session, 1)
    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        None
    )
    session.close()


def test_create_channel_with_client(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    client = Clients.query.filter_by(id=1).first()
    create_channel(session, 3, 1, "TestChannel2")
    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


def test_update_channel(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    update_channel(session, 1)
    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        None
    )
    session.close()


def test_update_channel_with_client(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    client = Clients.query.filter_by(id=1).first()
    update_channel(session, 2, 1, "TestChannelModified2")
    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


def test_delete_channel_with_client(setup_db, actor_setup):
    session = setup_db

    client = Clients.query.filter_by(id=1).first()

    create_channel(session, 3, 1, "TestChannelModified33")
    on_si_changed, on_pi_changed = create_mocks_manually()
    delete_channel(session, 3)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


# ============ UTILITIES ============
def create_channel(session, station_id, client_id=None, name="TestChannel"):
    channel = Channel()
    channel.station_id = station_id
    channel.name = name
    channel.ecc_id = 159
    channel.frequency = "00917"
    channel.pi = "C00F"
    channel.type_id = "fm"
    if client_id:
        channel.fk_client = client_id
    session.add(channel)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return channel


def update_channel(session, channel_id, client_id=None, name="TestChannelModified"):
    channel = Channel.query.filter_by(id=channel_id).first()
    channel.name = name
    if client_id:
        channel.fk_client = client_id
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return channel


def delete_channel(session, channel_id):
    channel = Channel.query.filter_by(id=channel_id).first()
    session.delete(channel)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
