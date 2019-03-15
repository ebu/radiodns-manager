import time

import config
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED, EVENT_SI_PI_DELETED
from models import ServiceProvider


def test_service_provider_create(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    sp = create_sp(session, "zzebu")

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        None
    )
    session.close()


def test_service_provider_update(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks

    sp = update_sp(session, 1, "test2")

    on_si_changed.assert_called_with(
        EVENT_SI_PI_UPDATED,
        sp,
        None
    )
    session.close()


def test_service_provider_delete(setup_db, actor_setup, create_mocks):
    session = setup_db
    on_si_changed, on_pi_changed = create_mocks
    delete_sp(session, 1)

    on_si_changed.assert_called_with(
        EVENT_SI_PI_DELETED,
        {"id": 1, "codops": "zzebu"},
        None
    )
    session.close()


# ============ UTILITIES ============
def create_sp(session, codops="zzebu", name="testSP"):
    service_provider = ServiceProvider(codops)
    service_provider.short_name = name
    service_provider.medium_name = name
    service_provider.long_name = name
    service_provider.short_description = name
    service_provider.long_description = name
    session.add(service_provider)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return service_provider


def update_sp(session, id, name="testSP2"):
    service_provider = ServiceProvider.query.filter_by(id=id).first()
    service_provider.short_name = name
    service_provider.medium_name = name
    service_provider.long_name = name
    service_provider.short_description = name
    service_provider.long_description = name
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return service_provider


def delete_sp(session, id):
    service_provider = ServiceProvider.query.filter_by(id=id).first()
    session.delete(service_provider)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
