import json

from aws import awsutils
from models import db, Clients, Station

# Map of every genres with their text representation.
genres_map = {
    '3.1.1': 'News',
    '3.1.1.11': 'Local/Regional',
    '3.6': 'Other Music',
    '3.6.1': 'Classical music',
    '3.6.1.5': 'Light Classical music',
    '3.6.1.2': 'Serious Classical',
    '3.6.2': 'Jazz',
    '3.6.3': 'Background music',
    '3.6.3.2': 'Easy Listening',
    '3.6.3.5': 'Oldies',
    '3.6.4': 'Pop-rock',
    '3.6.4.1': 'Pop',
    '3.6.4.11': 'Seasonal/Holiday',
    '3.6.4.14': 'Rock',
    '3.6.4.14.2': 'Metal',
    '3.6.4.17': 'Singer/Songwriter',
    '3.6.5': 'Blues/RnB/Soul/Gospel/Spiritual',
    '3.6.6': 'Country and Western',
    '3.6.7': 'Rap/Hip Hop/Reggae',
    '3.6.8': 'Electronic/Club/Urban/Dance/DJ',
    '3.6.8.3': 'Techno/Industrial',
    '3.6.8.4': 'House/Techno House',
    '3.6.9': 'World/Traditional/Folk (PTy 26/28 - National/Folk Music)',
    '3.6.10': 'Hit-Chart/Song Requests',
    '1.2': 'Information',
    '2.1.4': 'Documentary',
    '2.1.8': 'Phone-In',
    '3.1': 'Non-fiction',
    '3.1.1.6': 'National/Politics',
    '3.1.1.12': 'Traffic',
    '3.1.1.13': 'Weather forecasts',
    '3.1.1.14': 'Service information',
    '3.1.1.16': 'Current Affairs',
    '3.1.2.1': 'Religious/Philisophies',
    '3.1.3.2': 'Social',
    '3.1.3.5': 'Finance',
    '3.1.3.6': 'Education',
    '3.1.4': 'Arts and Media',
    '3.1.6': 'Sciences',
    '3.2': 'Sports',
    '3.3': 'Leisure',
    '3.3.5': 'Travel',
    '3.4': 'Fiction',
    '3.6.13': 'Spoken',
    '4.2.1': 'Children',
}

# Stations form fields.
station_fields = [
    'name',
    'short_name',
    'medium_name',
    'long_name',
    'short_description',
    'long_description',
    'url_default',
    'ip_allowed',
    'postal_name',
    'street',
    'city',
    'zipcode',
    'phone_number',
    'sms_number',
    'sms_body',
    'sms_description',
    'keywords',
    'email_address',
    'email_description',
    'default_language',
    'location_country',
    'radiovis_enabled',
    'radiovis_service',
    'radioepg_enabled',
    'radioepg_service',
    'radiospi_service',
    'radioepgpi_enabled',
    'radiotag_enabled',
    'radiotag_service',
]


def gen_default_client():
    """
    Generates the default client.
    :return: The default client.
    """
    default_client = Clients()
    default_client.id = 0
    default_client.name = "default"
    return default_client


def update_station_srv(station):
    """
    Updates a station SRV records. This include the vis, epg, spi, tag services.

    :param station: The station.
    :return: None
    """
    if station.radiovis_enabled:
        awsutils.update_or_create_vissrv_station(station)
    else:
        awsutils.remove_vissrv_station(station)

    if station.radioepg_enabled:
        awsutils.update_or_create_epgsrv_station(station)
    else:
        awsutils.remove_epgsrv_station(station)

    if station.radiospi_service:
        awsutils.update_or_create_spisrv_station(station)
    else:
        awsutils.remove_spisrv_station(station)

    if station.radiotag_enabled:
        awsutils.update_or_create_tagsrv_station(station)
    else:
        awsutils.remove_tagsrv_station(station)


def save_or_update_station(sp, request, errors, station_instance=None, client=None, parent_station=None):
    """
    Saves or updates a station based on the request form values.

    :param sp: The service provider.
    :param request: The fask request.
    :param errors: The error list instance.
    :param station_instance: The station instance if any. If this is a new station leave this paramter to None.
    :param client: The client instance if this is an override for a client. If this is a new station leave this
        parameter to None.
    :param parent_station: The parent station of this station if this is a
    :return: the save/updated/same station instance and the errors list.
    """
    if not client:
        client = Clients()
        client.id = 0
        client.name = "default"

    is_override = "True" == request.form.get("is_client_override_" + str(client.id))
    if not is_override and client.id != 0:
        return station_instance, errors

    if not station_instance:
        station_instance = Station(int(request.form.get('ebuio_orgapk')))
    station_instance.service_provider_id = sp.id

    for field in station_fields:
        field_value = request.form.get(field + '_' + str(client.id))

        if parent_station and field_value == parent_station[field]:
            field_value = None
        setattr(station_instance, field, field_value)

    if not is_override and station_instance.name == "":
        errors.append("Please set a name")
        return station_instance, errors

    # handle special fields
    station_instance.radiovis_enabled = 'radiovis_enabled_' + str(client.id) in request.form
    station_instance.radioepg_enabled = station_instance.radiospi_enabled = 'radioepg_enabled_' + str(
        client.id) in request.form
    station_instance.radiotag_enabled = 'radiotag_enabled_' + str(client.id) in request.form
    station_instance.radioepgpi_enabled = 'radioepgpi_enabled_' + str(client.id) in request.form

    # handle genres
    clientid = str(client.id) if is_override else '0'
    genre_href = map(lambda key: request.form[key],
                     filter(lambda key: key.startswith('genrehref[]_' + clientid + "_") and request.form[key] != '',
                            request.form.keys()))
    genre_href = sorted(genre_href)
    genres = []

    for h in genre_href:
        genre_id = h.split(':')[-1]
        if genre_id != '':
            genres.append({'href': h, 'name': genres_map[genre_id]})

    station_instance.genres = json.dumps(genres)

    if is_override:
        station_instance.parent = parent_station.id
        station_instance.fk_client = client.id

    # save
    if (is_override or client.id == 0) and not station_instance.id:
        station_instance.gen_random_password()
        db.session.add(station_instance)

    return station_instance, errors


def get_client_and_station(request, id):
    """
    Utility to reduce boilerplate and return the list of the clients (including default) and the list of a station
    and its overrides.

    :param request: The fask request.
    :param id: The id of the station.
    :return: the client and station lists.
    """
    orga = int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))
    clients = [gen_default_client()] + Clients.query.filter_by(orga=orga).order_by(Clients.id).all()

    if id == '-':
        stations = [Station(orga)] * len(clients)
    else:
        stations = [Station.query.filter_by(orga=orga, id=int(id)).first()] + \
                   Station.query.filter_by(orga=orga, parent=int(id)).order_by(Station.fk_client).all()

    return clients, stations


def combine_client_and_station(request, clients, stations, fill=True):
    """
    Combines a client with its existing station's overrides.

    :param request: The flask Request.
    :param clients: The clients list.
    :param stations: The stations list.
    :param fill: If true, any client left without a station will be set with a new empty station in the result list.
    If false, the client will be ignored.
    :return: A list of tuple of the shape List<(client, station)>
    """
    orga = int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))
    clients_stations = [(clients[0], stations[0])]

    for client in clients[1:]:
        filtered_stations = filter(lambda s: s.fk_client == client.id, stations[1:])
        if len(filtered_stations) != 0:
            clients_stations.append((client, filtered_stations[0]))
        elif fill:
            clients_stations.append((client, Station(orga)))

    return map(lambda x: (x[0].json, x[1].json), clients_stations)
