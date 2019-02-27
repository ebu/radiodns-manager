import time

import pykka

import config
from SPI.utils import spi_changed, spi_deleted
from models import Station, Clients, ServiceProvider, Channel, Picture, Show, Schedule, GenericServiceFollowingEntry, \
    PictureForEPG, LogoImage


class SPIGeneratorActor(pykka.ThreadingActor):

    def on_start(self):
        self.queue = []
        self.actor_ref.tell({"type": "execute"})

    def on_receive(self, message):
        if message["type"] == "add":
            self.queue.append(message)
        elif message["type"] == "execute":
            affected_resources = {}

            for msg in self.queue:
                service_provider_id = None
                clients = []

                if msg["subject"] == "service_provider":
                    service_provider_id = msg["id"]
                    orga = Station.query.filter_by(service_provider_id=service_provider_id).first().orga
                    clients = [None] + Clients.query.filter_by(orga=orga).all()
                    if msg["action"] == "delete":
                        spi_deleted(generate_service_provider_meta(ServiceProvider.query.filter_by(id=service_provider_id).first()), None)
                        continue
                elif msg["subject"] == "station":
                    station = Station.query.filter_by(id=msg["id"]).first()
                    service_provider_id = station.service_provider_id
                    clients = [station.client]
                elif msg["subject"] == "channel":
                    channel = Channel.query.filter_by(id=msg["id"]).first()
                    station = Station.query.filter_by(id=channel.station_id).first(),
                    service_provider_id = station[0].service_provider_id
                    clients = [channel.client]
                elif msg["subject"] == "ecc":
                    affected_resources = select_all()
                    break
                elif msg["subject"] == "country_code":
                    affected_resources = select_all()
                    break
                elif msg["subject"] == "clients":
                    client = Clients.query.filter_by(id=msg["id"]).first()
                    service_provider_id = Station.query.filter_by(orga=client.orga).first().service_provider_id
                    clients = [client]
                elif msg["subject"] == "picture":
                    picture = Picture.query.filter_by(id=msg["id"]).first()
                    for channel in picture.channels:
                        station = Station.query.filter_by(id=channel.station_id).first(),
                        service_provider_id = station[0].service_provider_id
                        clients = [channel.client]
                        affected_resources = add_to_affected_resources(affected_resources, service_provider_id, clients)
                elif msg["subject"] == "show":
                    show = Show.query.filter_by(id=msg["id"]).first()
                    stations = Station.query.filter(Station.id.in_(map(lambda x: x.station_id, show.schedules))).all()
                    for station in stations:
                        service_provider_id = station.service_provider_id
                        clients = [station.client],
                        affected_resources = add_to_affected_resources(affected_resources, service_provider_id, clients)
                elif msg["subject"] == "schedule":
                    schedule = Schedule.query.filter_by(id=msg["id"]).first()
                    station = Station.query.filter_by(id=schedule.station_id).first(),
                    service_provider_id = station[0].service_provider_id
                    clients = [station[0].client]
                elif msg["subject"] == "gsfe":
                    gsfe = GenericServiceFollowingEntry.query.filter_by(id=msg["id"]).first()
                    if gsfe.station_id:
                        station = Station.query.filter_by(id=gsfe.station_id).first(),
                        service_provider_id = station[0].service_provider_id
                        clients = [station[0].client]
                elif msg["subject"] == "picture_epg":
                    picture_peg = PictureForEPG.query.filter_by(id=msg["id"]).first()
                    service_provider_id = Station.query.filter_by(orga=picture_peg.orga).first().service_provider_id
                    clients = [None] + Clients.query.filter_by(orga=picture_peg.orga).all()
                elif msg["subject"] == "logo_image":
                    logo_image = LogoImage.query.filter_by(id=msg["id"]).first()
                    for station in logo_image.stations:
                        service_provider_id = logo_image.service_provider.id
                        clients = [station.client]
                        affected_resources = add_to_affected_resources(affected_resources, service_provider_id, clients)

                affected_resources = add_to_affected_resources(affected_resources, service_provider_id, clients)

            for _, value in affected_resources.iteritems():
                for client in list(value["clients"]):
                    spi_changed(
                        generate_service_provider_meta(ServiceProvider.query.filter_by(id=value["sp_id"]).first()),
                        client,
                    )
            self.queue = []
            time.sleep(config.SPI_GENERATION_INTERVAL)
            self.actor_ref.tell({"type": "execute"})


class SPIGeneratorManager:

    def __init__(self):
        self.spi_generator_actor = SPIGeneratorActor.start()

    def tell_to_actor(self, msg):
        if not self.spi_generator_actor.is_alive():
            self.spi_generator_actor = SPIGeneratorActor.start()
        self.spi_generator_actor.tell(msg)


def add_to_affected_resources(affected_resources, service_provider_id, clients):
    try:
        affected_resources[service_provider_id]["clients"] \
            = affected_resources[service_provider_id]["clients"] | set(clients)
    except KeyError:
        affected_resources[service_provider_id] = {"sp_id": service_provider_id, "clients": set(clients)}
    finally:
        return affected_resources


def select_all():
    service_providers = ServiceProvider.query.all()
    affected_resources = {}

    for service_provider in service_providers:
        orga = Station.query.filter_by(service_provider_id=service_provider.id).first().orga
        clients = [None] + Clients.query.filter_by(orga=orga).all()
        affected_resources[service_provider.id] = {"sp_id": service_provider.id, "clients": set(clients)}
    return affected_resources


def generate_service_provider_meta(service_provider):
    return {"id": service_provider.id, "codops": service_provider.codops}
