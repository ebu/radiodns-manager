import time

import config
from models import Ecc, Clients, ServiceProvider, Station
from tests.SPI_generator.test_02_service_provider import create_sp
from tests.utils import create_handler


# Since the 'country_code' message and the 'all' message are using the same code we can safely say that they are
# tested as well.


def test_create_ecc(setup_db, actor_setup):
    session = setup_db
    on_si_changed_call_history = []
    on_pi_changed_call_history = []

    sp3 = create_sp(session, codops="CNN", name="CNN-sp")
    sp2 = ServiceProvider.query.filter_by(id=2).first()
    client = Clients.query.filter_by(id=1).first()
    on_si_changed_verification = [('UPDATE', sp3, None),
                                  ('UPDATE', sp2, client),
                                  ('UPDATE', sp2, None)]
    on_pi_changed_verification = [
        ('UPDATE', Station.query.filter_by(id=1).first()),
        ('UPDATE', Station.query.filter_by(id=3).first()),
    ]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station: on_pi_changed_call_history.append((event_name, station)),
    )

    create_ecc(session)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)
    assert len(on_pi_changed_call_history) == len(on_pi_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    for call in on_pi_changed_call_history:
        assert call in on_pi_changed_verification

    session.close()


def test_update_ecc(setup_db, actor_setup):
    session = setup_db
    on_si_changed_call_history = []
    on_pi_changed_call_history = []

    client = Clients.query.filter_by(id=1).first()
    sp3 = ServiceProvider.query.filter_by(id=3).first()
    sp2 = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed_verification = [('UPDATE', sp3, None),
                                  ('UPDATE', sp2, client),
                                  ('UPDATE', sp2, None)]
    on_pi_changed_verification = [
        ('UPDATE', Station.query.filter_by(id=1).first()),
        ('UPDATE', Station.query.filter_by(id=3).first()),
    ]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station: on_pi_changed_call_history.append((event_name, station)),
    )
    update_ecc(session, 1)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)
    assert len(on_pi_changed_call_history) == len(on_pi_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    for call in on_pi_changed_call_history:
        assert call in on_pi_changed_verification

    session.close()


def test_delete_ecc(setup_db, actor_setup):
    session = setup_db
    on_si_changed_call_history = []
    on_pi_changed_call_history = []
    create_ecc(session, "mysuperecc")

    client = Clients.query.filter_by(id=1).first()
    sp3 = ServiceProvider.query.filter_by(id=3).first()
    sp2 = ServiceProvider.query.filter_by(id=2).first()
    on_si_changed_verification = [
        ('UPDATE', sp3, None),
        ('UPDATE', sp2, client),
        ('UPDATE', sp2, None)
    ]
    on_pi_changed_verification = [
        ('UPDATE', Station.query.filter_by(id=1).first()),
        ('UPDATE', Station.query.filter_by(id=3).first()),
    ]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station: on_pi_changed_call_history.append((event_name, station)),
    )
    delete_ecc(session, 2)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)
    assert len(on_pi_changed_call_history) == len(on_pi_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    for call in on_pi_changed_call_history:
        assert call in on_pi_changed_verification

    session.close()


# ============ UTILITIES ============
def create_ecc(session, name="eccTest"):
    ecc = Ecc()
    ecc.name = name
    ecc.iso = "C0"
    ecc.pi = "pi"
    ecc.ecc = "ecc"
    session.add(ecc)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return ecc


def update_ecc(session, ecc_id, name="eccTest2"):
    ecc = Ecc.query.filter_by(id=ecc_id).first()
    ecc.name = name
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
    return ecc


def delete_ecc(session, ecc_id):
    ecc = Ecc.query.filter_by(id=ecc_id).first()
    session.delete(ecc)
    session.commit()
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)
