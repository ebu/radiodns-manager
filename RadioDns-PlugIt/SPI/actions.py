# For Caching
import re

# For SqlAlchemy
import plugit
from flask import abort, send_from_directory, request as Request
from plugit.utils import cache

import config
import server
from SPI.utils import make_xsi1_hostname_cache_key, make_xsi3_hostname_cache_key, \
    make_pi1_hostname_cache_key, get_codops_from_request
from actions_utils import with_client_identification


@plugit.app.route('/radiodns/epg/XSI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
@with_client_identification
def epg_1_xml(client_identifier):
    """Special call for EPG XSI v1.1 2013.10 RadioDNS"""

    if not config.XSISERVING_ENABLED:
        abort(501)
    return server.SPI_handler.on_request_epg_1(get_codops_from_request(), client_identifier)


# Override Cache Key for XSI 1
epg_1_xml.make_cache_key = make_xsi1_hostname_cache_key


@plugit.app.route('/radiodns/spi/3.1/SI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
@with_client_identification
def epg_3_xml(client_identifier):
    """Special call for EPG SI vV3.1.1 2015.01 ETSI xml"""

    if not config.XSISERVING_ENABLED:
        abort(501)
    return server.SPI_handler.on_request_epg_3(get_codops_from_request(), client_identifier)


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


# FIXME - BROKEN
@plugit.app.route('/radiodns/epg/<path:path>/<int:date>_PI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
def epg_sch_1_xml(path, date):
    """Special call for EPG scheduling xml"""

    #        chrts.epg.radio.ebu.io >> XSI for all CHRTS Channels
    # la1ere.chrts.epg.radio.ebu.io >> XSI for La1ere only in CHRTS

    a = config.XSISERVING_ENABLED
    if not config.XSISERVING_ENABLED:
        abort(501)

    return server.SPI_handler.on_request_schedule_1(path, date)

# Override Cache Key for PI 1
epg_sch_1_xml.make_cache_key = make_pi1_hostname_cache_key

# @plugit.app.route('/radiodns/spi/3.1/<path:service_identifier>/<int:date>_PI.xml')
# @plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
# def epg_sch_1_xml(service_identifier, date):
#
#
