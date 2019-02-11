import copy
import re

from flask import abort, request as Request
from sqlalchemy import or_, text

import config
from models import Station, LogoImage
from stations.utils import station_fields


def apply_overrides(client, station):
    """
    Clones a station and returns it with its overrides for a specific client.
    :param client: The client.
    :param station: The station.
    :return: A clone of the original station with its overrides.
    """
    if client:
        overrides = Station.query.filter_by(parent=station.id, fk_client=client.id).first()
        if overrides:
            station = copy.copy(station)
            for field in station_fields + ['genres', 'default_logo_image_id']:
                if station[field] != overrides[field] and overrides[field] is not None:
                    setattr(station, field, overrides[field])

            if overrides.default_logo_image_id:
                setattr(station, "default_logo_image",
                        LogoImage.query.filter_by(id=overrides.default_logo_image_id).first())

    return station


def make_xsi1_hostname_cache_key(*args, **kwargs):
    """Generates a cachekey containing the hostname"""
    hostname = Request.host
    args = str(hash(frozenset(Request.args.items())))
    return (hostname + '_xsi1_' + args).encode('utf-8')


def make_pi1_hostname_cache_key(*args, **kwargs):
    """Generates a cachekey containing the hostname"""
    hostname = Request.host
    path = Request.path
    args = str(hash(frozenset(Request.args.items())))
    return (hostname + '_pi1_' + path + '_' + args).encode('utf-8')


def make_xsi3_hostname_cache_key(*args, **kwargs):
    """Generates a cachekey containing the hostname"""
    hostname = Request.host
    args = str(hash(frozenset(Request.args.items())))
    return (hostname + '_xsi3_' + args).encode('utf-8')


def retrieve_spi_data(client):
    """
    Retrieves data for the xml spi generation.
    :param client: The client if the request wants a station override.
    :return: The resulting data: (List<station>, ServiceProvider)
    """
    from models import Station, Channel, GenericServiceFollowingEntry, Ecc, ServiceProvider

    sp = None
    stations = None

    regex = re.compile('((?P<provider>[^\.]+?)\.).+\.' + config.XSISERVING_DOMAIN)
    r = regex.search(Request.host)
    if r:
        provider = r.groupdict()['provider']

        if provider:
            # We have a station based query
            sp = ServiceProvider.query.filter_by(codops=provider).order_by(ServiceProvider.codops).first()
            if sp:
                stations = Station.query.filter_by(service_provider_id=sp.id,
                                                   radioepg_enabled=True)  # , fqdn_prefix=station)
    else:
        sp = ServiceProvider.query.filter_by(codops="EBU").order_by(ServiceProvider.codops).first()
        stations = Station.query.filter_by(radioepg_enabled=True)

    if not sp and not config.DEBUG and not config.STANDALONE:
        abort(404)

    result = []

    if stations:
        for station in stations:

            station = apply_overrides(client, station)

            json_channels = []

            # Channels
            for channel in station.channels \
                    .filter(or_(Channel.fk_client == None, Channel.fk_client == client.id if client else text('0'))) \
                    .order_by(Channel.name) \
                    .all():
                if channel.servicefollowingentry.active:
                    json_channels.append(channel.servicefollowingentry.json)

                    if channel.type_id == 'fm':  # For FM, also add with the country code
                        try:
                            fm_channel = channel.servicefollowingentry.json

                            # Split the URI
                            uri_dp = fm_channel['uri'].split(':', 2)
                            uri_p = uri_dp[1].split('.')

                            pi_code = uri_p[0]

                            # Get the ISO code form the picode
                            ecc = Ecc.query.filter_by(pi=pi_code[0].upper(), ecc=pi_code[1:].upper()).first()

                            uri_p[0] = ecc.iso.lower()

                            # Update the new URL
                            fm_channel['uri'] = uri_dp[0] + ':' + '.'.join(uri_p)

                            # Add the service
                            json_channels.append(fm_channel)

                        except:
                            pass

            # Custom entries
            for channel in station.servicefollowingentries.order_by(GenericServiceFollowingEntry.channel_uri).all():
                if channel.active:
                    json_channels.append(channel.json)

            result.append([station.json, json_channels])

    return result, sp
