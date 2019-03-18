from tests.SPI_generator.test_02_service_provider import delete_sp
from tests.utils import create_handler


def test_delete_sp_with_stations(setup_db, actor_setup):
    session = setup_db

    on_si_changed_call_history = []
    on_pi_changed_call_history = []

    on_si_changed_verification = [('DELETE', {"id": 2, "codops": "rai"}, None)]
    on_pi_changed_verification = [
        ('DELETE', 1),
        ('DELETE', 3),
    ]

    create_handler(
        lambda event_name, service_provider, client: on_si_changed_call_history.append(
            (event_name, service_provider, client)),
        lambda event_name, station: on_pi_changed_call_history.append((event_name, station)),
    )

    delete_sp(session, 2)

    assert len(on_si_changed_call_history) == len(on_si_changed_verification)
    assert len(on_pi_changed_call_history) == len(on_pi_changed_verification)

    for call in on_si_changed_call_history:
        assert call in on_si_changed_verification

    for call in on_pi_changed_call_history:
        assert call in on_pi_changed_verification

    session.close()
