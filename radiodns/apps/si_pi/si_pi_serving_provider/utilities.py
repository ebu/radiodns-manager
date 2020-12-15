import datetime
import re

from django.forms import model_to_dict
from django.http import Http404
from django.template.loader import render_to_string

from apps.channels.models import Channel
from apps.localization.models import Ecc
from apps.manager.models import Organization
from apps.stations.models import Station
from config.settings.base import SI_PI_SERVING_DOMAIN, ETSI_SPEC


def get_codops_from_request(request):
    """
    Tries to read a service provider's codops from the Django request context.
    :return: the codops or raise 404.
    """
    hostname = request.META['HTTP_HOST']
    pattern = re.compile("([a-z0-9]{1,255})\..*" + SI_PI_SERVING_DOMAIN)

    matched = pattern.match(hostname)
    if matched is None:
        raise Http404("Invalid hostname please see " + ETSI_SPEC)
    else:
        return matched.group(1)


def generate_si_file(codops, client, template_name):
    """
        Renders the template for this SI file.
        :param codops: codops of the service provider.
        :param client: The client if the file contains client overrides or None.
        :param template_name: The template uri.
        :return: The rendered XML file.
        """
    service_provider = Organization.objects.select_related().get(codops=codops)
    return render_to_string(template_name, context={
        "service_provider": service_provider,
        "stations": generate_si_data(service_provider, client),
        "service_provider_images": service_provider.logoimage_set.first(),
        "media_root": "/media/"  # FIXME media_root from base settings
    })


def generate_si_data(sp, client):
    """
    Retrieves data for the xml SI generation.
    :param sp: The service provider.
    :param client: The client if the request wants a station override.
    :return: The resulting data: (List<station>, ServiceProvider)
    """

    if sp:
        stations = Station.objects.filter(organization__id=sp.id, radioepg_enabled=True)
    else:
        stations = Station.objects.filter(radioepg_enabled=True)

    result = []

    if stations:
        for station in stations:
            channels = station.channel_set.filter(station__id=station.id).order_by("name").all()
            station_instance = station.stationinstance_set.filter(
                client__id=client.id if client is not None else None).first()

            json_channels = []

            # Channels
            for channel in channels:
                for servicefollowingentry in channel.genericservicefollowingentry_set.all():
                    if channel.type_id == 'fm' and servicefollowingentry.active:  # For FM, also add with the country code
                        fm_channel = model_to_dict(channel.servicefollowingentry)

                        # Split the URI
                        uri_dp = fm_channel['uri'].split(':', 2)
                        uri_p = uri_dp[1].split('.')

                        pi_code = uri_p[0]

                        # Get the ISO code form the picode
                        ecc = Ecc.objects.filter(pi=pi_code[0].upper(), ecc=pi_code[1:].upper()).first()

                        uri_p[0] = ecc.iso.lower()

                        # Update the new URL
                        fm_channel['uri'] = uri_dp[0] + ':' + '.'.join(uri_p)

                        # Add the service
                        json_channels.append(fm_channel)
                    else:
                        json_channels.append(model_to_dict(servicefollowingentry))
            result.append([{**model_to_dict(station),
                            **model_to_dict(station_instance),
                            "default_image": model_to_dict(station.default_image),
                            "genres_list": station_instance.genres_list,
                            "fqdn": station_instance.fqdn,
                            "service_identifier": station_instance.service_identifier},
                           json_channels])

    return result


def generate_pi_file(hostname, date, template_name, path=None, station=None):
    """
    Renders a PI file.
    Note: You can only provide a path or a station not both at the same time and not none of both.
    :param hostname: Hostname of the request (Host header).
    :param date: the requested date. The date is of the shape <YEAR><MONTH><DAY>.
    - <YEAR> is a four digit number representing the current year, eg: 2019
    - <MONTH> is a two digit number representing the current month in the current year, eg: 01
    - <DAY> is a two digit number representing the current day in the current month, eg: 01
    :param template_name: reference to the internal template.
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
        data = extract_pi_data_from_path(hostname, path, date)
    if not data:
        return None

    json_schedules = data[0]
    real_start_date = data[1]
    real_end_date = data[2]
    time_format = "%Y-%m-%dT%H:%M:%S%z"

    return render_to_string(template_name, context={
        "schedules": json_schedules,
        "start_time": real_start_date.strftime(time_format),
        "end_time": real_end_date.strftime(time_format),
        "creation_time": datetime.datetime.now().strftime(time_format)
    })


def generate_pi_data(events, date):
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

    # Compute start and end of week
    start_of_the_week = datetime.datetime.combine(today - datetime.timedelta(days=today.weekday()), datetime.time())
    end_of_the_week = start_of_the_week + datetime.timedelta(hours=23, minutes=59, seconds=59)

    # Filter by date
    date_to_filter = datetime.datetime.strptime(str(date), "%Y%m%d").date()
    real_start_date = datetime.datetime.combine(date_to_filter, datetime.time())

    json_schedules = []

    for schedule in events:
        schedule.start_date = start_of_the_week

        if schedule.date_of_start_time.date() == date_to_filter:
            json_schedules.append(schedule.json)

    return json_schedules, real_start_date, end_of_the_week


def extract_pi_data_from_path(hostname, path, date):
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

    channels = None

    # Find out what stations to serve if by codops or station
    pattern = re.compile("([a-z0-9]{1,255})\.([a-z0-9]{1,255})\..*" + SI_PI_SERVING_DOMAIN)
    matched = pattern.match(hostname)
    if matched is not None:

        station = matched.group(1)
        provider = matched.group(2)

        if provider:
            # We have a station based query
            sp = Organization.objects.filter(codops=provider).order_by("codops").first()
            if sp:
                channels = Channel.objects.filter(station__organization__id=sp.id, station__radioepgpi_enabled=True)

        if station and channels:
            channels = filter(lambda x: x.station.fqdn_prefix == station, channels)

    else:
        channels = Channel.objects.filter(station__radioepgpi_enabled=True)

    if not channels:
        raise Http404("Invalid hostname please see " + ETSI_SPEC)

    topiced_path = '/topic/' + path
    station_channel = filter(lambda x: x.topic_no_slash == topiced_path, channels)
    if not station_channel:
        # Check for country code if FM
        csplitter = path.split('/')
        eccstr = ''
        if csplitter[0] == 'fm':
            # Find correct ECC
            ecc = Ecc.objects.filter(iso=csplitter[1].upper()).first()
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
