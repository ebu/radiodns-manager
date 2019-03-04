import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED, EVENT_SI_PI_DELETED
from models import Station, ServiceProvider
from tests.conftest import create_mocks_manually
from tests.utils import setup_service_provider


def test_station_create(setup_db, actor_setup):
    session = setup_db
    on_si_changed, on_pi_changed, sp = setup_service_provider(session, "rai")

    create_station(session, sp.id)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        None,
    )
    session.close()


def test_station_update(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    update_station(session, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        None,
    )
    session.close()


def test_station_delete(setup_db, actor_setup):
    session = setup_db

    create_station(session, 2)
    on_si_changed, on_pi_changed = create_mocks_manually()
    delete_station(session, 2)

    sp = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        None,
    )

    on_pi_changed.assert_called_with(
        EVENT_SI_PI_DELETED,
        2,
    )


# ============ UTILITIES ============
def create_station(session, service_provider_id, name="TestStation", no_commit=False):
    station = Station(-1, name)
    station.service_provider_id = service_provider_id
    station.short_name = name[:8]
    station.medium_name = name[:16]
    station.long_name = name[:64]
    station.short_description = name[:128]
    session.add(station)
    if not no_commit:
        session.commit()
        time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return station


def update_station(session, station_id, name="TestStation2"):
    station = Station.query.filter_by(id=station_id).first()
    station.short_name = name[:8]
    station.medium_name = name[:16]
    station.long_name = name[:64]
    station.short_description = name[:128]
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return station


def delete_station(session, id):
    station = Station.query.filter_by(id=id).first()
    session.delete(station)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)

