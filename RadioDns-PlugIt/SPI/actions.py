# For Caching
import re

# For SqlAlchemy
import plugit
from flask import abort, send_from_directory, request as Request
from plugit.utils import cache

import config
from SPI.utils import make_xsi1_hostname_cache_key, make_xsi3_hostname_cache_key, \
    make_pi1_hostname_cache_key, get_codops_from_request
from actions_utils import with_client_identification
from server import SPI_handler


@plugit.app.route('/radiodns/epg/XSI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
@with_client_identification
def epg_1_xml(client_identifier):
    """Special call for EPG XSI v1.1 2013.10 RadioDNS"""

    if config.XSISERVING_ENABLED:
        return SPI_handler.on_request_epg_1(get_codops_from_request(), client_identifier)

    # Else
    abort(404)


# Override Cache Key for XSI 1
epg_1_xml.make_cache_key = make_xsi1_hostname_cache_key


@plugit.app.route('/radiodns/spi/3.1/SI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
@with_client_identification
def epg_3_xml(client_identifier):
    """Special call for EPG SI vV3.1.1 2015.01 ETSI xml"""

    if config.XSISERVING_ENABLED:
        return SPI_handler.on_request_epg_3(get_codops_from_request(), client_identifier)

    # Else
    abort(404)


# Override Cache Key for XSI 3
epg_3_xml.make_cache_key = make_xsi3_hostname_cache_key


@plugit.app.route('/radiodns/logo/<int:id>/<int:w>/<int:h>/logo.png')
@plugit.utils.cache(time=config.IMG_CACHE_TIMEOUT)
def logo(id, w, h):
    """Return a logo for a station"""

    from models import Station
    import os

    station = Station.query.filter(Station.id == id).first()

    if not station:
        abort(404)

    dest_file = 'media/uploads/radioepg/cache/S%s_W%s_H%s_L%s.png' % (
        str(int(id)), str(int(w)), str(int(h)), str(station.epg_picture_id) if station.epg_picture_id else 'B')

    if not os.path.isfile(dest_file):
        from PIL import Image
        size = (w, h)
        image = Image.open(
            station.epg_picture.filename if station.epg_picture else 'media/uploads/radioepg/default.png')
        image.thumbnail(size, Image.ANTIALIAS)
        background = Image.new('RGBA' if station.epg_picture else 'RGB', size, (255, 255, 255, 0))
        background.paste(image, ((size[0] - image.size[0]) / 2, (size[1] - image.size[1]) / 2))

        background.save(dest_file)

    return send_from_directory(".", dest_file)


@plugit.app.route('/radiodns/epg/<path:path>/<int:date>_PI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
def epg_sch_1_xml(path, date):
    """Special call for EPG scheduling xml"""

    #        chrts.epg.radio.ebu.io >> XSI for all CHRTS Channels
    # la1ere.chrts.epg.radio.ebu.io >> XSI for La1ere only in CHRTS

    if config.XSISERVING_ENABLED:
        from models import Station, Channel, Ecc, ServiceProvider
        from flask import render_template, Response
        import datetime
        time_format = '%Y-%m-%dT%H:%M:%S%z'

        channels = None

        # Find out what stations to serve if by codops or station
        regex = re.compile('((?P<station>[^\.]+?)\.)?(?P<provider>[^\.]+?)\.' + config.XSISERVING_DOMAIN)
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
            station = station_channel[0].station

            import datetime
            time_format = '%Y-%m-%dT%H:%M:%S%z'

            today = datetime.date.today()
            start_date = datetime.datetime.combine(today - datetime.timedelta(days=today.weekday()), datetime.time())
            end_date = start_date + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

            # Filter by date
            date_to_filter = datetime.datetime.strptime(str(date), "%Y%m%d").date()
            real_start_date = datetime.datetime.combine(date_to_filter, datetime.time())
            real_end_date = start_date + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

            list = []

            for elem in station.schedules.all():
                elem.start_date = start_date

                if elem.date_of_start_time.date() == date_to_filter:
                    list.append(elem.json)

            return Response(render_template('radioepg/schedule/xml1.html', schedules=list,
                                            start_time=real_start_date.strftime(time_format),
                                            end_time=real_end_date.strftime(time_format),
                                            creation_time=datetime.datetime.now().strftime(time_format)),
                            mimetype='text/xml')

    abort(404)
    # return 'Not enabled'


# Override Cache Key for PI 1
epg_sch_1_xml.make_cache_key = make_pi1_hostname_cache_key
