from sqlalchemy import event

from SPI.executor_actor import SPIGeneratorManager
from models import ServiceProvider, Station, Ecc, CountryCode, Clients, Channel, Picture, Show, Schedule, \
    PictureForEPG, LogoImage, GenericServiceFollowingEntry

"""
List of events listener bound to the events of the SQLAlchemy engine.
"""

spi_generator_manager = SPIGeneratorManager()


@event.listens_for(ServiceProvider, 'after_insert')
@event.listens_for(ServiceProvider, 'after_update')
def service_provider_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "action": "update", "subject": "service_provider", "id": target.id})


@event.listens_for(ServiceProvider, 'before_delete')
def service_provider_delete_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "action": "delete", "subject": "service_provider", "id": target.id})


@event.listens_for(Station, 'after_insert')
@event.listens_for(Station, 'after_update')
def station_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "station", "id": target.id})


@event.listens_for(Channel, 'after_insert')
@event.listens_for(Channel, 'after_update')
def channel_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "channel", "id": target.id})


@event.listens_for(Ecc, 'after_insert')
@event.listens_for(Ecc, 'after_update')
def ecc_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "ecc", "id": target.id})


@event.listens_for(CountryCode, 'after_insert')
@event.listens_for(CountryCode, 'after_update')
def country_code_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "country_code", "id": target.id})


@event.listens_for(Clients, 'after_insert')
@event.listens_for(Clients, 'after_update')
def client_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "clients", "id": target.id})


@event.listens_for(Picture, 'after_insert')
@event.listens_for(Picture, 'after_update')
def picture_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "picture", "id": target.id})


@event.listens_for(Show, 'after_insert')
@event.listens_for(Show, 'after_update')
def show_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "show", "id": target.id})


@event.listens_for(Schedule, 'after_insert')
@event.listens_for(Schedule, 'after_update')
def schedule_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "schedule", "id": target.id})


@event.listens_for(GenericServiceFollowingEntry, 'after_insert')
@event.listens_for(GenericServiceFollowingEntry, 'after_update')
def gsfe_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "gsfe", "id": target.id})


@event.listens_for(PictureForEPG, 'after_insert')
@event.listens_for(PictureForEPG, 'after_update')
def pic_epg_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "picture_epg", "id": target.id})


# TODO find a way to update only the concerned clients files.
@event.listens_for(LogoImage, 'after_insert')
@event.listens_for(LogoImage, 'after_update')
def logo_image_update_event_listener(mapper, connection, target):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "logo_image", "id": target.id})
