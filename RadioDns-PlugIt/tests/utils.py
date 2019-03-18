import mock

import server
from SPI.modules.base_spi import BaseSPI
from tests.SPI_generator.test_02_service_provider import create_sp


def setup_service_provider(session, sp_codops="zzebu"):
    sp = create_sp(session, sp_codops)

    on_si_changed = mock.Mock()
    on_pi_changed = mock.Mock()
    create_handler(on_si_changed, on_pi_changed)

    return on_si_changed, on_pi_changed, sp


def create_handler(on_si_changed, on_pi_changed):
    class TestSPI(BaseSPI):
        def on_si_resource_changed(self, event_name, service_provider, client=None):
            on_si_changed(event_name, service_provider, client)

        def on_pi_resource_changed(self, event_name, station_id):
            on_pi_changed(event_name, station_id)

    server.SPI_handler = TestSPI()
