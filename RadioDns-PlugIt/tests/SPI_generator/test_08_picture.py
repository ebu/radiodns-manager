import time

import config
from models import Picture, Channel, Clients, ServiceProvider
from tests.utils import create_handler


def test_picture_create(setup_db, actor_setup):
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

    create_picture(session, -1)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    session.close()


def test_picture_update(setup_db, actor_setup):
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

    update_picture(session, 1)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    session.close()


def test_picture_delete(setup_db, actor_setup):
    session = setup_db

    on_si_changed_call_history = []
    create_picture(session, -1, "mysuperbepicture")

    client = Clients.query.filter_by(id=1).first()
    sp = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed_verification = [('UPDATE', sp, client),
                                  ('UPDATE', sp, None)]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station_id: None,
    )

    delete_picture(session, 2)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    session.close()


# ============ UTILITIES ============
def create_picture(session, orga, name="testPicture"):
    picture = Picture(orga)
    picture.name = name
    picture.filename = name
    picture.radiotext = name
    picture.radiolink = name
    picture.image_url_prefix = name
    session.add(picture)
    session.commit()
    Channel.query.filter_by(id=1).first().default_picture_id = picture.id
    Channel.query.filter_by(id=2).first().default_picture_id = picture.id
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return picture


def update_picture(session, picture_id, name="testPicture2"):
    picture = Picture.query.filter_by(id=picture_id).first()
    picture.name = name
    picture.filename = name
    picture.radiotext = name
    picture.radiolink = name
    picture.image_url_prefix = name
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return picture


def delete_picture(session, picture_id):
    picture = Picture.query.filter_by(id=picture_id).first()
    session.delete(picture)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
