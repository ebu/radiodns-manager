# -*- coding: utf-8 -*-
import time

import pykka

import config
import server
from SPI.modules.base_spi import EVENT_SI_PI_UPDATED, EVENT_SI_PI_DELETED
from db_utils import db
from models import Station, Clients, ServiceProvider, Channel, Picture, Show, Schedule, GenericServiceFollowingEntry, \
    LogoImage


class SPIGeneratorActor(pykka.ThreadingActor):
    """
    Actor (Thread) that handles the SPI file generation and upload to the AWS cloudfront CDN (file itself is stored
    on a s3 bucket).

    For performance reasons this actor will batch updates and execute the said batch every x seconds, x being the
    time configured from the config.SPI_GENERATION_INTERVAL variable.

    It is highly advised to no use this class directly but rather interact with this actor trough the SPIGeneratorManager
    class.
    """

    def __init__(self):
        super(SPIGeneratorActor, self).__init__()
        self.queue = []

    def on_start(self):
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

            for i in range(0, 2):
                affected_si_resources = {}
                affected_pi_resources = {}
                current_action = "delete" if i == 0 else "update"

                for msg in list(filter(lambda m: m["action"] == current_action, self.queue)):
                    service_provider_id = None
                    clients = []
                    delete_flag = False

                    if msg["subject"] == "service_provider":
                        service_provider_id = msg["id"]
                        station = Station.query.filter_by(service_provider_id=service_provider_id).first()
                        clients = [None]
                        if station:
                            orga = station.orga
                            clients += Clients.query.filter_by(orga=orga).all()
                        if msg["action"] == "delete":
                            service_provider = ServiceProvider.query.filter_by(id=service_provider_id).first()
                            server.SPI_handler.on_si_resource_changed(EVENT_SI_PI_DELETED,
                                                                      {"id": msg["id"],
                                                                       "codops": service_provider.codops})
                            continue

                    elif msg["subject"] == "station":
                        station = db.session.query(Station).filter_by(id=msg["id"]).first()
                        service_provider_id = station.service_provider_id
                        clients = [station.client]

                        if current_action == "delete":
                            affected_pi_resources = add_to_affected_pi_resources(
                                affected_pi_resources,
                                station.id,
                                msg["action"])

                    elif msg["subject"] == "channel":
                        channel = Channel.query.filter_by(id=msg["id"]).first()
                        station = Station.query.filter_by(id=channel.station_id).first()
                        service_provider_id = station.service_provider_id
                        clients = [channel.client]
                        affected_pi_resources = add_to_affected_pi_resources(affected_pi_resources, station,
                                                                             "update")

                    elif msg["subject"] == "ecc" or msg["subject"] == "country_code" or msg["subject"] == "all":
                        affected_si_resources = select_all_si()
                        affected_pi_resources = select_all_pi()
                        break

                    elif msg["subject"] == "clients":
                        client = Clients.query.filter_by(id=msg["id"]).first()
                        station = Station.query.filter_by(orga=client.orga).first()
                        if station:
                            service_provider_id = station.service_provider_id
                            clients = [client if current_action == "update" else client.identifier]
                            delete_flag = current_action == "delete"

                    elif msg["subject"] == "picture":
                        picture = Picture.query.filter_by(id=msg["id"]).first()
                        for channel in picture.channels:
                            station = Station.query.filter_by(id=channel.station_id).first()
                            service_provider_id = station.service_provider_id
                            clients = [channel.client]
                            affected_si_resources = add_to_affected_si_resources(affected_si_resources,
                                                                                 service_provider_id, clients)

                    elif msg["subject"] == "show":
                        show = Show.query.filter_by(id=msg["id"]).first()
                        station = Station.query.filter_by(id=show.station_id).first()
                        if station:
                            service_provider_id = station.service_provider_id
                            clients = [None]
                            affected_pi_resources = add_to_affected_pi_resources(affected_pi_resources, station,
                                                                                 "update")

                    elif msg["subject"] == "schedule":
                        schedule = Schedule.query.filter_by(id=msg["id"]).first()
                        station = Station.query.filter_by(id=schedule.station_id).first()
                        if station:
                            service_provider_id = station.service_provider_id
                            clients = [None]
                            affected_pi_resources = add_to_affected_pi_resources(affected_pi_resources,
                                                                                 station, "update")

                    elif msg["subject"] == "gsfe":
                        gsfe = GenericServiceFollowingEntry.query.filter_by(id=msg["id"]).first()
                        if gsfe.station_id:
                            station = Station.query.filter_by(id=gsfe.station_id).first()
                            service_provider_id = station.service_provider_id
                            clients = [station.client]

                    # elif msg["subject"] == "picture_epg":
                    #     picture_peg = PictureForEPG.query.filter_by(id=msg["id"]).first()
                    #     service_provider_id = Station.query.filter_by(orga=picture_peg.orga).first().service_provider_id
                    #     clients = [None] + Clients.query.filter_by(orga=picture_peg.orga).all()

                    elif msg["subject"] == "logo_image":
                        logo_image = LogoImage.query.filter_by(id=msg["id"]).first()
                        for station in logo_image.stations:
                            service_provider_id = station.service_provider_id
                            clients = [station.client]
                            affected_si_resources = add_to_affected_si_resources(affected_si_resources,
                                                                                 service_provider_id,
                                                                                 clients)

                    elif msg["subject"] == "reload":
                        stations = Station.query.filter_by(service_provider_id=msg["id"]).all()
                        service_provider_id = msg["id"]
                        clients = [None]
                        for station in stations:
                            clients += Clients.query.filter_by(orga=station.orga).all()
                            affected_pi_resources = add_to_affected_pi_resources(affected_pi_resources,
                                                                                 station, "update")

                    affected_si_resources = add_to_affected_si_resources(affected_si_resources, service_provider_id,
                                                                         clients, delete_flag)

                if current_action == "delete" and len(self.queue) != 0:
                    db.session.commit()

                for _, value in affected_si_resources.iteritems():
                    for client in list(value["clients"]):
                        server.SPI_handler.on_si_resource_changed(
                            value["action"],
                            ServiceProvider.query.filter_by(id=value["sp_id"]).first(),
                            client)

                for _, value in affected_pi_resources.iteritems():
                    server.SPI_handler.on_pi_resource_changed(value["action"], value["station"])
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


def add_to_affected_si_resources(affected_resources, service_provider_id, clients, delete_flag=False):
    """
    Adds to the affected resources map a changed SPI file represented by a service provider's id and a list of client.
    The goal of this data structure is to get a list a global list of service providers along with their clients
    overrides that have changed.

    :param affected_resources: the current affected resources. A dict of the shape {"sp": ServiceProvider, "clients": set(clients)}
    :param service_provider_id: the service provider that had one of its resources changed.
    :param clients: the clients of the service provider that have an override that has changed.
    :return: the updated affected resources dict.
    """
    if service_provider_id is None:
        return affected_resources
    try:
        affected_resources[service_provider_id]["clients"] \
            = affected_resources[service_provider_id]["clients"] | set(clients)
    except KeyError:
        affected_resources[service_provider_id] = {
            "sp_id": service_provider_id,
            "action": EVENT_SI_PI_DELETED if delete_flag else EVENT_SI_PI_UPDATED,
            "clients": set(clients)
        }
    finally:
        return affected_resources


def add_to_affected_pi_resources(affected_resources, station, action):
    affected_resources[station.id if isinstance(station, Station) else station] = {"station": station,
                                                                                   "action": EVENT_SI_PI_DELETED if action == "delete" else EVENT_SI_PI_UPDATED}
    return affected_resources


def select_all_si():
    """
    Selects all SPI files and marks them as affected resources.

    :return: the updated affected resources dict.
    """
    service_providers = ServiceProvider.query.all()
    affected_resources = {}

    for service_provider in service_providers:
        clients = [None]
        station = Station.query.filter_by(service_provider_id=service_provider.id).first()
        if station:
            orga = station.orga
            clients += Clients.query.filter_by(orga=orga).all()
        affected_resources[service_provider.id] = {"sp_id": service_provider.id, "clients": set(clients),
                                                   "action": EVENT_SI_PI_UPDATED}
    return affected_resources


def select_all_pi():
    service_providers = ServiceProvider.query.all()
    affected_resources = {}

    for service_provider in service_providers:
        stations = Station.query.filter_by(service_provider_id=service_provider.id).all()
        for station in stations:
            affected_resources = add_to_affected_pi_resources(affected_resources, station, "update")
    return affected_resources


def generate_service_provider_meta(service_provider):
    return {"id": service_provider.id, "codops": service_provider.codops}
