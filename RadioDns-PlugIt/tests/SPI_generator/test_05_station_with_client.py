import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED
from models import Clients, ServiceProvider
from tests.SPI_generator.test_03_station import create_station, update_station


def test_station_create_with_client(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    client = Clients.query.filter_by(id=1).first()
    sp = ServiceProvider.query.filter_by(id=2).first()
    create_station_with_client(session, 2, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        client
    )
    session.close()


def test_station_update_with_client(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    client = Clients.query.filter_by(id=1).first()
    sp = ServiceProvider.query.filter_by(id=2).first()
    update_station(session, 3)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        client
    )
    session.close()


# ============ UTILITIES ============
def create_station_with_client(session, service_provider_id, client_id, name="TestStationClient"):
    station = create_station(session, service_provider_id, name, True)
    station.fk_client = client_id
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return station
