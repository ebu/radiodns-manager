import time

import config
from models import LogoImage, Clients, Station, ServiceProvider
from tests.utils import create_handler


def test_logo_image_create(setup_db, actor_setup):
    session = setup_db

    on_si_changed_call_history = []

    client = Clients.query.filter_by(id=1).first()
    sp = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed_verification = [('UPDATE', sp, client),
                                  ('UPDATE', sp, None)]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station_id: None,
    )

    create_logo_image(session, -1)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    session.close()


def test_logo_image_update(setup_db, actor_setup):
    session = setup_db

    on_si_changed_call_history = []

    client = Clients.query.filter_by(id=1).first()
    sp = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed_verification = sorted([('UPDATE', sp, client),
                                         ('UPDATE', sp, None)])

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station_id: None,
    )

    update_logo_image(session, 1)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    session.close()


def test_logo_image_delete(setup_db, actor_setup):
    session = setup_db

    on_si_changed_call_history = []

    client = Clients.query.filter_by(id=1).first()
    sp = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed_verification = sorted([('UPDATE', sp, client),
                                         ('UPDATE', sp, None)])

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station_id: None,
    )

    delete_logo_image(session, 1)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    session.close()


# ============ UTILITIES ============
def create_logo_image(session, orga, filename="testLogoImage"):
    logo_image = LogoImage(orga)
    logo_image.filename = filename
    session.add(logo_image)
    session.commit()
    Station.query.filter_by(id=1).first().default_logo_image_id = logo_image.id
    Station.query.filter_by(id=3).first().default_logo_image_id = logo_image.id
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return logo_image


def update_logo_image(session, logo_image_id, filename="testLogoImage2"):
    logo_image = LogoImage.query.filter_by(id=logo_image_id).first()
    logo_image.filename = filename
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return logo_image


def delete_logo_image(session, logo_image_id):
    logo_image = LogoImage.query.filter_by(id=logo_image_id).first()
    session.delete(logo_image)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)

