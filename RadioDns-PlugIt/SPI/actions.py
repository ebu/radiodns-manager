# For Caching
import re

# For SqlAlchemy
import plugit
from flask import abort, send_from_directory, request as Request

import config


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


@plugit.app.route('/radiodns/epg/XSI.xml')
def epg_1_xml():
    """Special call for EPG XSI v1.1 2013.10 RadioDNS"""
    # Specified by v1.1 2013.10 /radiodns/epg/XSI.xml
    # http://<host>:<port>/radiodns/epg/XSI.xml
    # http://radiodns.org/wp-content/uploads/2013/10/REPG01-v1.1.pdf

    #        chrts.epg.radio.ebu.io >> XSI for all CHRTS Channels
    # la1ere.chrts.epg.radio.ebu.io >> XSI for La1ere only in CHRTS

    if config.XSISERVING_ENABLED:

        from models import Station, Channel, GenericServiceFollowingEntry, Ecc, ServiceProvider
        from flask import render_template, Response
        import datetime
        time_format = '%Y-%m-%dT%H:%M:%S%z'

        sp = None
        stations = None

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
                    stations = Station.query.filter_by(service_provider_id=sp.id,
                                                       radioepg_enabled=True)  # , fqdn_prefix=station)

            if station:
                # TODO FIX Filtering by property does not workin in SQLAlchemy, thus using regular python to filter
                stations = filter(lambda x: x.fqdn_prefix == station, stations)

        else:
            sp = ServiceProvider.query.filter_by(codops="EBU").order_by(ServiceProvider.codops).first()
            stations = Station.query.filter_by(radioepg_enabled=True)

        if not sp and not config.STANDALONE:
            abort(404)

        list = []

        if stations:
            for elem in stations:

                entries = []

                # Channels
                for elem2 in elem.channels.order_by(Channel.name).all():
                    if elem2.servicefollowingentry.active:
                        entries.append(elem2.servicefollowingentry.json)

                        if elem2.type_id == 'fm':  # For FM, also append with the country code
                            try:
                                data2 = elem2.servicefollowingentry.json

                                # Split the URI
                                uri_dp = data2['uri'].split(':', 2)
                                uri_p = uri_dp[1].split('.')

                                pi_code = uri_p[0]

                                # Get the ISO code form the picode
                                ecc = Ecc.query.filter_by(pi=pi_code[0].upper(), ecc=pi_code[1:].upper()).first()

                                uri_p[0] = ecc.iso.lower()

                                # Update the new URL
                                data2['uri'] = uri_dp[0] + ':' + '.'.join(uri_p)

                                # Add the service
                                entries.append(data2)

                            except:
                                pass

                # Custom entries
                for elem2 in elem.servicefollowingentries.order_by(GenericServiceFollowingEntry.channel_uri).all():
                    if elem2.active:
                        entries.append(elem2.json)

                if entries:
                    list.append([elem.json, entries])

        return Response(render_template('radioepg/servicefollowing/xml1.html', stations=list, service_provider=sp,
                                        creation_time=datetime.datetime.now().strftime(time_format)),
                        mimetype='text/xml')

    # Else
    abort(404)


# Override Cache Key for XSI 1
epg_1_xml.make_cache_key = make_xsi1_hostname_cache_key


@plugit.app.route('/radiodns/spi/3.1/SI.xml')
def epg_3_xml():
    """Special call for EPG SI vV3.1.1 2015.01 ETSI xml"""
    # Specified by 3.1.1 /radiodns/spi/3.1/SI.xml
    # http://<host>:<port>/radiodns/spi/3.1/SI.xml
    # http://www.etsi.org/deliver/etsi_ts/102800_102899/102818/03.01.01_60/ts_102818v030101p.pdf

    #        chrts.epg.radio.ebu.io >> XSI for all CHRTS Channels
    # la1ere.chrts.epg.radio.ebu.io >> XSI for La1ere only in CHRTS

    if config.XSISERVING_ENABLED:

        from models import Station, Channel, GenericServiceFollowingEntry, Ecc, ServiceProvider
        from flask import render_template, Response
        import datetime
        time_format = '%Y-%m-%dT%H:%M:%S%z'

        sp = None
        stations = None

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
                    stations = Station.query.filter_by(service_provider_id=sp.id,
                                                       radioepg_enabled=True)  # , fqdn_prefix=station)

            if station:
                # TODO FIX Filtering by property does not workin in SQLAlchemy, thus using regular python to filter
                stations = filter(lambda x: x.fqdn_prefix == station, stations)

        else:
            sp = ServiceProvider.query.filter_by(codops="EBU").order_by(ServiceProvider.codops).first()
            stations = Station.query.filter_by(radioepg_enabled=True)

        if not sp and not config.STANDALONE:
            abort(404)

        list = []

        if stations:
            for station in stations:

                entries = []

                # Channels
                for channel in station.channels.order_by(Channel.name).all():
                    if channel.servicefollowingentry.active:
                        entries.append(channel.servicefollowingentry.json)

                        if channel.type_id == 'fm':  # For FM, also add with the country code
                            try:
                                data2 = channel.servicefollowingentry.json

                                # Split the URI
                                uri_dp = data2['uri'].split(':', 2)
                                uri_p = uri_dp[1].split('.')

                                pi_code = uri_p[0]

                                # Get the ISO code form the picode
                                ecc = Ecc.query.filter_by(pi=pi_code[0].upper(), ecc=pi_code[1:].upper()).first()

                                uri_p[0] = ecc.iso.lower()

                                # Update the new URL
                                data2['uri'] = uri_dp[0] + ':' + '.'.join(uri_p)

                                # Add the service
                                entries.append(data2)

                            except:
                                pass

                # Custom entries
                for channel in station.servicefollowingentries.order_by(GenericServiceFollowingEntry.channel_uri).all():
                    if channel.active:
                        entries.append(channel.json)

                # List station anyway
                list.append([station.json, entries])

        return Response(render_template('radioepg/servicefollowing/xml3.html', stations=list, service_provider=sp,
                                        creation_time=datetime.datetime.now().strftime(time_format)),
                        mimetype='text/xml')

    # Else
    abort(404)


# Override Cache Key for XSI 3
epg_3_xml.make_cache_key = make_xsi3_hostname_cache_key


@plugit.app.route('/radiodns/logo/<int:id>/<int:w>/<int:h>/logo.png')
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
def epg_sch_1_xml(path, date):
    """Special call for EPG scheduling xml"""

    #        chrts.epg.radio.ebu.io >> XSI for all CHRTS Channels
    # la1ere.chrts.epg.radio.ebu.io >> XSI for La1ere only in CHRTS

    if config.XSISERVING_ENABLED:
        from models import Station, Channel, GenericServiceFollowingEntry, Ecc, ServiceProvider
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

            if station:
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
