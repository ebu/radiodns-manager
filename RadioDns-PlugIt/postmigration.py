import logging
import sys
from time import sleep

import plugit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

import config
from aws.awsutils import update_or_create_cname, get_or_create_mainzone, verify_srv_records
from models import ServiceProvider, Station
from stations.utils import update_station_srv

# Script that is meant to be run after the current version (11 november 2018) to add to all stations additional
# spi entries to the database and srv records in route 53.

mysqlAlchemyUrl = """mysql://root:{password}@127.0.0.1:3306/radiodns""".format(password=sys.argv[1])
engine = create_engine(mysqlAlchemyUrl)
logging.info("Waiting database to come online. Use CTRL + C to interrupt at any moment.")
conn = None

# Check connection to database
while conn is None:
    try:
        conn = engine.connect()
    except OperationalError as e:
        logging.warning("""Couldn't connect to the database: {error}""".format(error=e))
        sleep(1)
conn.close()

plugit.app.config['SQLALCHEMY_DATABASE_URI'] = mysqlAlchemyUrl
plugit.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(plugit.app)

services_providers = ServiceProvider.query.all()
mainzone = get_or_create_mainzone()

stations_to_update = []

print("Collecting stations...")
for service_provider in services_providers:
    stations = Station.query.filter_by(service_provider_id=service_provider.id, radioepg_enabled=True, radiospi_enabled=None).all()
    update_or_create_cname(mainzone, service_provider.spi_fqdn, config.RADIOSPI_DNS)
    update_or_create_cname(mainzone, service_provider.epg_fqdn, config.RADIOEPG_DNS)
    update_or_create_cname(mainzone, service_provider.vis_fqdn, config.RADIOVIS_DNS)
    update_or_create_cname(mainzone, service_provider.tag_fqdn, config.RADIOTAG_DNS)

    for station in stations:
        stations_to_update.append((service_provider, station))

i = 1
imax = len(stations_to_update)
for sp_station in stations_to_update:
    service_provider, station = sp_station
    print("""Updating srv records for station #{i}/{imax}..."""
          .format(i=i, imax=imax))

    station.radiospi_enabled = True
    station.radiospi_service = """{codops}.{spi_service}""" \
        .format(codops=service_provider.codops.lower(), spi_service=config.RADIOSPI_SERVICE_DEFAULT.lower())
    station.radioepg_service = """{codops}.{epg_service}""" \
        .format(codops=service_provider.codops.lower(), epg_service=config.RADIOEPG_SERVICE_DEFAULT.lower())

    if station.radiotag_enabled:
        station.radiotag_service = """{codops}.{radiotag_service}""" \
            .format(codops=service_provider.codops.lower(), radiotag_service=config.RADIOTAG_SERVICE_DEFAULT.lower())

    if station.radiovis_enabled:
        station.radiovis_service = """{codops}.{radiovis_service}""" \
            .format(codops=service_provider.codops.lower(), radiovis_service=config.RADIOVIS_SERVICE_DEFAULT.lower())

    db.session.merge(station)

    update_station_srv(station)
    i += 1
db.session.commit()

print("Verifying srv records...")
verify_srv_records()
