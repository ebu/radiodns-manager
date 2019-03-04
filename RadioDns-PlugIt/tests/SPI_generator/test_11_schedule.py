import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED
from models import Schedule, ServiceProvider, Station
from tests.conftest import create_mocks_manually


def test_schedule_create(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks
    sp = ServiceProvider.query.filter_by(id=2).first()

    create_schedule(session)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        None
    )

    on_pi_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        Station.query.filter_by(id=1).first()
    )
    session.close()


def test_schedule_update(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    update_schedule(session, 1)

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


def test_schedule_delete(setup_db, actor_setup):
    session = setup_db
    create_schedule(session, 10)
    on_si_changed, on_pi_changed = create_mocks_manually()

    delete_schedule(session, 2)

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
def create_schedule(session, day=1):
    schedule = Schedule()
    schedule.station_id = 1
    schedule.day = day
    session.add(schedule)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return schedule


def update_schedule(session, schedule_id, day=2):
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    schedule.day = day
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return schedule


def delete_schedule(session, schedule_id):
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    session.delete(schedule)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)

