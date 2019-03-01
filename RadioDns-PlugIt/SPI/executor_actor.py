# -*- coding: utf-8 -*-
import time

import pykka

import config
import server
from SPI.modules.base_spi import EVENT_SPI_UPDATED, EVENT_SPI_DELETED
from models import Station, Clients, ServiceProvider, Channel, Picture, Show, Schedule, GenericServiceFollowingEntry, \
    PictureForEPG, LogoImage


class SPIGeneratorActor(pykka.ThreadingActor):
    """
    Actor (Thread) that handles the SPI file generation and upload to the AWS cloudfront CDN (file itself is stored
    on a s3 bucket).

    For performance reasons this actor will batch updates and execute the said batch every x seconds, x being the
    time configured from the config.SPI_GENERATION_INTERVAL variable.

    It is highly advised to no use this class directly but rather interact with this actor trough the SPIGeneratorManager
    class.
    """

    def on_start(self):
        self.queue = []
        self.actor_ref.tell({"type": "execute"})

    def on_receive(self, message):
        """
        Receive method.

        :param message: This actors accepts messages that are dictionary containing at least one key named "type".

        The messages can be of two types:
            - "add": This message is of shape
            {
                "type": "add",
                "subject": "service_provider" | "station" | "channel" | "ecc" | "country_code" | "clients" | "picture" | "show" | "schedule" | "gsfe" | "picture_epg" | "logo_image" | "reload" | "all",
                "id": integer,
                (optional)"action": "update" | "delete",
            }

            The message structure is as follow:
                - The type of the message states that this is an "add" message.
                - The subject of the message indicates what has changed.
                - The id of the message is the database primary key of the object that has changed.

            The message of type "add" adds to this executor queue the resource that was either updated or deleted. The
            executor will then determine from the changed resources which spi file must be deleted or updated.

            - "execute": Flush the executor queue and triggers the generation/deletion of the affected SPI files.
        """
        if "type" not in message:
            return
        if message["type"] == "add":
            self.queue.append(message)
        elif message["type"] == "execute":
            affected_resources = {}

            for msg in self.queue:
                service_provider_id = None
                clients = []

                if msg["subject"] == "service_provider":
                    service_provider_id = msg["id"]
                    station = Station.query.filter_by(service_provider_id=service_provider_id).first()
                    clients = [None]
                    if station:
                        orga = station.orga
                        clients = [None] + Clients.query.filter_by(orga=orga).all()
                    if msg["action"] == "delete":
                        spi_deleted(generate_service_provider_meta(
                            ServiceProvider.query.filter_by(id=service_provider_id).first()))
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
                elif msg["subject"] == "ecc" or msg["subject"] == "country_code" or msg["subject"] == "all":
                    affected_resources = select_all()
                    break
                elif msg["subject"] == "clients":
                    client = Clients.query.filter_by(id=msg["id"]).first()
                    station = Station.query.filter_by(orga=client.orga).first()
                    if station:
                        service_provider_id = station.service_provider_id
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
                elif msg["subject"] == "reload":
                    station = Station.query.filter_by(service_provider_id=msg["id"]).first()
                    service_provider_id = msg["id"]
                    clients = [None]
                    if station:
                        orga = station.orga
                        clients = [None] + Clients.query.filter_by(orga=orga).all()

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
    """
    Class to interact with the SPIGeneratorActor. By using this class you are guaranteed to have at anytime an actor that
    will execute your requests.
    """

    def __init__(self):
        self.spi_generator_actor = SPIGeneratorActor.start()

    def tell_to_actor(self, msg):
        """
        Sends a message to a SPIGeneratorActor instance. Please refer to the on_receive method of the SPIGeneratorActor
        class for more information about the messages that can be send.
        :param msg: The message to send.
        """
        if not self.spi_generator_actor.is_alive():
            self.spi_generator_actor = SPIGeneratorActor.start()
        self.spi_generator_actor.tell(msg)

    def stop(self):
        self.spi_generator_actor.stop(timeout=100)


def add_to_affected_resources(affected_resources, service_provider_id, clients):
    """
    Adds to the affected resources map a changed SPI file represented by a service provider's id and a list of client.
    The goal of this data structure is to get a list a global list of service providers along with their clients
    overrides that have changed.

    :param affected_resources: the current affected resources. A dict of the shape {"sp_id": integer, "clients": set(clients)}
    :param service_provider_id: the service provider that had one of its resources changed.
    :param clients: the clients of the service provider that have an override that has changed.
    :return: the updated affected resources dict.
    """
    try:
        affected_resources[service_provider_id]["clients"] \
            = affected_resources[service_provider_id]["clients"] | set(clients)
    except KeyError:
        affected_resources[service_provider_id] = {"sp_id": service_provider_id, "clients": set(clients)}
    finally:
        return affected_resources


def select_all():
    """
    Selects all SPI files and marks them as affected resources.

    :return: the updated affected resources dict.
    """
    service_providers = ServiceProvider.query.all()
    affected_resources = {}

    for service_provider in service_providers:
        station = Station.query.filter_by(service_provider_id=service_provider.id).first()
        if station:
            orga = station.orga
            clients = [None] + Clients.query.filter_by(orga=orga).all()
            affected_resources[service_provider.id] = {"sp_id": service_provider.id, "clients": set(clients)}
    return affected_resources


def generate_service_provider_meta(service_provider):
    return {"id": service_provider.id, "codops": service_provider.codops}


def spi_event_emitter(service_provider_meta, event_name, client=None):
    """
    Emits an event to all spi file handler listener.

    :param service_provider_meta: c
    :param event_name: Can be 'UPDATE' or 'DELETE'.
    :param client: The client if the file contains client overrides or None.
    """
    a = server.SPI_handler
    server.SPI_handler.on_event_epg_1(event_name, service_provider_meta, client)
    server.SPI_handler.on_event_epg_3(event_name, service_provider_meta, client)


def spi_changed(service_provider_meta, client=None):
    """
    Shortcut to signal that an SPI file has changed.
    :param service_provider_meta:  a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
    :param client: The client if the file contains client overrides or None.
    """
    spi_event_emitter(service_provider_meta, EVENT_SPI_UPDATED, client)


def spi_deleted(service_provider_meta):
    """
    Shortcut to signal that an SPI file has changed.
    :param service_provider_meta:  a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
    """
    spi_event_emitter(service_provider_meta, EVENT_SPI_DELETED, None)
