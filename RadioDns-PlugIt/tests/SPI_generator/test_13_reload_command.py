import time

import config
from models import ServiceProvider, Clients, Station
from tests.utils import create_handler


def test_reload_command(setup_db, actor_setup):
    session = setup_db

    on_si_changed_call_history = []
    on_pi_changed_call_history = []

    sp = ServiceProvider.query.filter_by(id=2).first()
    client = Clients.query.filter_by(id=1).first()
    on_si_changed_verification = [('UPDATE', sp, None),
                                  ('UPDATE', sp, client)]
    on_pi_changed_verification = [
        ('UPDATE', Station.query.filter_by(id=1).first()),
        ('UPDATE', Station.query.filter_by(id=3).first()),
    ]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station: on_pi_changed_call_history.append((event_name, station)),
    )

    actor_setup.tell_to_actor({"type": "add", "subject": "reload", "id": sp.id, "action": "update"})
    time.sleep(config.SPI_GENERATION_INTERVAL * 3)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)
    assert len(on_pi_changed_call_history) == len(on_pi_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    for call in on_pi_changed_call_history:
        assert call in on_pi_changed_verification

    session.close()
