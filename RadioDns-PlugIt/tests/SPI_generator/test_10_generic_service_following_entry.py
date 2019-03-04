import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED
from models import Clients, GenericServiceFollowingEntry, ServiceProvider
from tests.conftest import create_mocks_manually


def test_gsfe_create(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    client = Clients.query.filter_by(id=1).first()

    create_gsfe(session)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


def test_gsfe_update(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    client = Clients.query.filter_by(id=1).first()

    update_gsfe(session, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


def test_gsfe_delete(setup_db, actor_setup):
    session = setup_db

    create_gsfe(session, 300)
    on_si_changed, on_pi_changed = create_mocks_manually()
    client = Clients.query.filter_by(id=1).first()

    delete_gsfe(session, 2)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        client
    )
    session.close()


# ============ UTILITIES ============
def create_gsfe(session, cost=100):
    gsfe = GenericServiceFollowingEntry()
    gsfe.active = True
    gsfe.cost = cost
    gsfe.station_id = 3
    session.add(gsfe)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return gsfe


def update_gsfe(session, gsfe_id, cost=101):
    gsfe = GenericServiceFollowingEntry.query.filter_by(id=gsfe_id).first()
    gsfe.cost = cost
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return gsfe


def delete_gsfe(session, gsfe_id):
    gsfe = GenericServiceFollowingEntry.query.filter_by(id=gsfe_id).first()
    session.delete(gsfe)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
