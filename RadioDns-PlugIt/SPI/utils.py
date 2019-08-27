import copy
import datetime
import re

import plugit
from flask import abort, request as Request, render_template
from sqlalchemy import or_, text

import config
from models import Station, LogoImage, ServiceProvider, Channel, Ecc, GenericServiceFollowingEntry, Schedule
from stations.utils import station_fields

import logging
logger = logging.getLogger(__name__)

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

def get_codops_from_request():
    """
    Tries to read a service provider's codops from the Flask request context.
    :return: the codops or None.
    """
    regex = re.compile('((?P<provider>[^\.]+?)\.).+\.' + config.SPISERVING_DOMAIN)
    r = regex.search(Request.host)
    if r:
        return r.groupdict()['provider']
    return None


def get_service_provider_from_codops(codops):
    """
    Returns a service provider from a codops.

    :param codops: the service provider codops.
    :return: The service provider if any else the default service provider if any else None.
    """
    if codops:
        # We have a station based query
        sp = ServiceProvider.query.filter_by(codops=codops).first()
    else:
        sp = ServiceProvider.query.filter_by(codops="EBU").first()
    return sp


def generate_si_data(sp, client):
    """
    Retrieves data for the xml SI generation.

    :param sp: The service provider.
    :param client: The client if the request wants a station override.
    :return: The resulting data: (List<station>, ServiceProvider)
    """

    if not sp and not config.DEBUG and not config.STANDALONE:
        abort(404)

    if sp:
        stations = Station.query.filter_by(service_provider_id=sp.id, radioepg_enabled=True)  # , fqdn_prefix=station)
    else:
        stations = Station.query.filter_by(radioepg_enabled=True)

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


def generate_si_file(service_provider, client, template_uri):
    """
    Renders the template for this SI file.

    :param service_provider: The service provider.
    :param client: The client if the file contains client overrides or None.
    :param template_uri: The template uri.
    :return: The rendered XML file.
    """
    with plugit.app.app_context():
        time_format = '%Y-%m-%dT%H:%M:%S%z'
        logger.debug('generating si file: service_provider=%s, client=%s', service_provider, client)
        data, sp = generate_si_data(service_provider, client)

        return render_template(template_uri, stations=data, service_provider=sp,
                               creation_time=datetime.datetime.now().strftime(time_format))


def generate_pi_data(station, date):
    """
    Retrieves data for the xml PI generation.

    :param station: The station.
    :param date: the requested date. The date is of the shape <YEAR><MONTH><DAY>.
    - <YEAR> is a four digit number representing the current year, eg: 2019
    - <MONTH> is a two digit number representing the current month in the current year, eg: 01
    - <DAY> is a two digit number representing the current day in the current month, eg: 01
    :return: The resulting data: (List(string), date, date)
    """
    import datetime

    today = datetime.date.today()
    start_of_the_week = datetime.datetime.combine(today - datetime.timedelta(days=today.weekday()), datetime.time())

    # Filter by date
    date_to_filter = datetime.datetime.strptime(str(date), "%Y%m%d").date()
    real_start_date = datetime.datetime.combine(date_to_filter, datetime.time())
    end_of_the_week = start_of_the_week + datetime.timedelta(hours=23, minutes=59, seconds=59)

    json_schedules = []

    for schedule in Schedule.query.filter_by(station_id=station.id).all():
        # for schedule in station.schedules.all():
        schedule.start_date = start_of_the_week

        if schedule.date_of_start_time.date() == date_to_filter:
            json_schedules.append(schedule.json)

    return json_schedules, real_start_date, end_of_the_week


def extract_pi_data_from_path(path, date):
    """
    Retrieves data for the xml PI generation from a specified path.

    :param path: the service identifier of the requested file. The service identifier is described here:
        https://www.etsi.org/deliver/etsi_ts/102800_102899/102818/03.01.01_60/ts_102818v030101p.pdf
    :param date: the requested date. The date is of the shape <YEAR><MONTH><DAY>.
    - <YEAR> is a four digit number representing the current year, eg: 2019
    - <MONTH> is a two digit number representing the current month in the current year, eg: 01
    - <DAY> is a two digit number representing the current day in the current month, eg: 01
    :return: The resulting data: (List(string), date, date)
    """

    from models import Station, Channel, Ecc, ServiceProvider
    channels = None

    # Find out what stations to serve if by codops or station
    regex = re.compile('((?P<station>[^\.]+?)\.)?(?P<provider>[^\.]+?)\.' + config.SPISERVING_DOMAIN)
    r = regex.search(Request.host)
    if r:

        station = r.groupdict()['station']
        provider = r.groupdict()['provider']

        if provider:
            # We have a station based query
            sp = ServiceProvider.query.filter_by(codops=provider).order_by(ServiceProvider.codops).first()
            if sp:
                channels = Channel.query.join(Station).filter(Station.service_provider_id == sp.id,
                                                              Station.radioepgpi_enabled).all()

        if station and channels:
            # TODO FIX Filtering by property does not workin in SQLAlchemy, thus using regular python to filter
            channels = filter(lambda x: x.station.fqdn_prefix == station, channels)

    else:
        channels = Channel.query.join(Station).filter(Station.radioepgpi_enabled).all()

    if not channels:
        abort(404)

    station = None
    topiced_path = '/topic/' + path
    station_channel = filter(lambda x: x.topic_no_slash == topiced_path, channels)
    if not station_channel:
        # Check for country code if FM
        csplitter = path.split('/')
        eccstr = ''
        if csplitter[0] == 'fm':
            # Find correct ECC
            ecc = Ecc.query.filter_by(iso=csplitter[1].upper()).first()
            if ecc:
                eccstr = ('%s%s' % (ecc.pi, ecc.ecc)).lower()
                csplitter[1] = eccstr
                topiced_ecc_path = '/'.join(csplitter)
                station_channel = filter(lambda x: x.topic_no_slash == topiced_ecc_path, channels)
            else:
                eccstr = csplitter[1]

        if not station_channel:
            # Still no station so check with wildcard as well
            splitter = path.split('/')
            if eccstr:
                splitter[1] = eccstr
            splitter[3] = '*'
            wild_ecc_path = '/topic/' + '/'.join(splitter)
            station_channel = filter(lambda x: x.topic_no_slash == wild_ecc_path, channels)

        if not station_channel:
            # Choose first with same PI
            psplitter = path.split('/')
            psplitter[3] = ''
            if eccstr:
                psplitter[1] = eccstr
            best_path = '/topic/' + '/'.join(psplitter)
            station_channel = filter(lambda x: x.topic_no_slash.startswith(best_path), channels)

    if station_channel:
        # Found station
        return generate_pi_data(station_channel[0].station, date)

    return None


def generate_pi_file(date, template_path, path=None, station=None):
    """
    Renders a PI file.

    Note: You can only provide a path or a station not both at the same time and not none of both.

    :param date: the requested date. The date is of the shape <YEAR><MONTH><DAY>.
    - <YEAR> is a four digit number representing the current year, eg: 2019
    - <MONTH> is a two digit number representing the current month in the current year, eg: 01
    - <DAY> is a two digit number representing the current day in the current month, eg: 01
    :param template_path: reference to the internal template path
    :param path: (Optional) The requested path or service identifier of the requested file. If provided, the
    generation will extract the requested station scheduling from the path.
    The path or service identifier is described here:
        https://www.etsi.org/deliver/etsi_ts/102800_102899/102818/03.01.01_60/ts_102818v030101p.pdf
    :param station: (Optional) The station that holds the requested scheduling.

    :return: The rendered XML file.
    """
    if path is None:
        data = generate_pi_data(station, date)
    else:
        data = extract_pi_data_from_path(path, date)
    if not data:
        return None

    json_schedules = data[0]
    real_start_date = data[1]
    real_end_date = data[2]
    time_format = '%Y-%m-%dT%H:%M:%S%z'
    with plugit.app.app_context():
        return render_template(template_path, schedules=json_schedules,
                               start_time=real_start_date.strftime(time_format),
                               end_time=real_end_date.strftime(time_format),
                               creation_time=datetime.datetime.now().strftime(time_format))
