import plugit
from flask_sqlalchemy import models_committed

from SPI.executor_actor import SPIGeneratorManager
from models import ServiceProvider, Station, Channel, Ecc, CountryCode, Clients, Picture, Show, Schedule, \
    GenericServiceFollowingEntry, LogoImage

spi_generator_manager = SPIGeneratorManager()


@models_committed.connect_via(plugit.app)
def sqlalchemy_signal_event_listener(*args, **kwargs):
    for operation in kwargs["changes"]:
        obj = operation[0]
        op_name = operation[1]
        if op_name == "insert":
            op_name = "update"

        if isinstance(obj, ServiceProvider):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "service_provider", "id": obj.id})
        elif isinstance(obj, Station):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "station", "id": obj.id})
        elif isinstance(obj, Channel):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "channel", "id": obj.id})
        elif isinstance(obj, Ecc):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "ecc", "id": obj.id})
        elif isinstance(obj, CountryCode):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "country_code", "id": obj.id})
        elif isinstance(obj, Clients):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "clients", "id": obj.id})
        elif isinstance(obj, Picture):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "picture", "id": obj.id})
        elif isinstance(obj, Show):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "show", "id": obj.id})
        elif isinstance(obj, Schedule):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "schedule", "id": obj.id})
        elif isinstance(obj, GenericServiceFollowingEntry):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "gsfe", "id": obj.id})
        # elif isinstance(obj, PictureForEPG):
        #     spi_generator_manager.tell_to_actor({"type": "add", "subject": "picture_epg", "id": obj.id})
        elif isinstance(obj, LogoImage):
            spi_generator_manager.tell_to_actor({"type": "add", "action": op_name, "subject": "logo_image", "id": obj.id})
