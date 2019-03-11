# For Caching

# For SqlAlchemy
import plugit
from flask import abort, send_from_directory
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
    """
    Route for EPG XSI v1.1 2013.10 RadioDNS.

    :param client_identifier: The client identifier if any.
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

    if not config.XSISERVING_ENABLED:
        abort(501)
    return server.SPI_handler.on_request_epg_1(get_codops_from_request(), client_identifier)


# Override Cache Key for XSI 1
epg_1_xml.make_cache_key = make_xsi1_hostname_cache_key


@plugit.app.route('/radiodns/spi/3.1/SI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
@with_client_identification
def epg_3_xml(client_identifier):
    """
    Route for SPI SI vV3.1.1 2015.01 ETSI xml.

    :param client_identifier: The client identifier if any.
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

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


# FIXME - BROKEN, see issue #121 of the github repository.
@plugit.app.route('/radiodns/epg/<path:path>/<int:date>_PI.xml')
@plugit.utils.cache(time=config.XML_CACHE_TIMEOUT)
def epg_sch_1_xml(path, date):
    """
    Route for SPI/EPG scheduling xml.

    :param path: The specified path of the requested resource.
    It is of the shape /radiodns/epg/service_identifier>/<date>_PI.xml.
    - The <service_identifier> is defined in this specification:
        https://www.etsi.org/deliver/etsi_ts/103200_103299/103270/01.02.01_60/ts_103270v010201p.pdf

    :param date: The date is of the shape <YEAR><MONTH><DAY>.
    - <YEAR> is a four digit number representing the current year, eg: 2019
    - <MONTH> is a two digit number representing the current month in the current year, eg: 01
    - <DAY> is a two digit number representing the current day in the current month, eg: 01
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

    if not config.XSISERVING_ENABLED:
        abort(501)

    return server.SPI_handler.on_request_schedule_1(path, date)


# Override Cache Key for PI 1
epg_sch_1_xml.make_cache_key = make_pi1_hostname_cache_key
