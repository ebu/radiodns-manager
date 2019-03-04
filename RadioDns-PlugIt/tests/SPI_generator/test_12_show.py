import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED
from models import Show, ServiceProvider, Station
from tests.conftest import create_mocks_manually


def test_show_create(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    create_show(session, -1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        None
    )

    on_pi_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        Station.query.filter_by(id=1).first()
    )
    session.close()


def test_show_update(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    update_show(session, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        None
    )

    on_pi_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        Station.query.filter_by(id=1).first()
    )
    session.close()


def test_show_delete(setup_db, actor_setup):
    session = setup_db
    create_show(session, -1, "mysupershow")
    on_si_changed, on_pi_changed = create_mocks_manually()

    update_show(session, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        ServiceProvider.query.filter_by(id=2).first(),
        None
    )

    on_pi_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        Station.query.filter_by(id=1).first()
    )
    session.close()


# ============ UTILITIES ============
def create_show(session, orga, name="show1"):
    show = Show(orga)
    show.medium_name = name
    show.long_name = name
    show.station_id = 1
    session.add(show)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return show


def update_show(session, show_id, name="show2"):
    show = Show.query.filter_by(id=show_id).first()
    show.medium_name = name
    show.long_name = name
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return show
