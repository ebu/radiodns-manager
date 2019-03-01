import server
from SPI.modules.base_spi import BaseSPI
from db_utils import db
from models import ServiceProvider, Station


def create_handler(on_event_1, on_event_3):
    class TestSPI(BaseSPI):
        def on_event_epg_1(self, event_name, service_provider_meta, client=None):
            on_event_1(event_name, service_provider_meta, client)

        def on_event_epg_3(self, event_name, service_provider_meta, client=None):
            on_event_3(event_name, service_provider_meta, client)

    server.SPI_handler = TestSPI()


def create_sp(codops="zzebu", name="testSP"):
    service_provider = ServiceProvider(-1)
    service_provider.codops = codops
    service_provider.short_name = name
    service_provider.medium_name = name
    service_provider.long_name = name
    service_provider.short_description = name
    service_provider.long_description = name
    db.session.add(service_provider)
    db.session.commit()
    return service_provider


def update_sp(id, name="testSP"):
    service_provider = ServiceProvider.query.filter_by(id=id).first()
    service_provider.short_name = name
    service_provider.medium_name = name
    service_provider.long_name = name
    service_provider.short_description = name
    service_provider.long_description = name
    db.session.commit()
    return service_provider


def delete_sp(id):
    service_provider = ServiceProvider.query.filter_by(id=id).first()
    db.session.delete(service_provider)
    db.session.commit()


def create_station(service_provider_id, name="TestStation"):
    station = Station(-1)
    station.service_provider_id = service_provider_id
    station.name = name
    station.short_name = name[:8]
    station.medium_name = name[:16]
    station.long_name = name[:64]
    station.short_description = name[:128]
    db.session.add(station)
    db.session.commit()
    return station
