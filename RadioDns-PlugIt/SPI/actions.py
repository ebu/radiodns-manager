import plugit
from flask import abort, send_from_directory
from plugit.utils import cache

import config
import server
from SPI.utils import *
from actions_utils import with_client_identification


@plugit.app.route('/radiodns/epg/XSI.xml')
@with_client_identification
def xsi_1_xml(client_identifier):
    """
    Route for RadioEPG 1.1 XSI file

    :param client_identifier: The client identifier if any.
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

    if not config.SPISERVING_ENABLED:
        abort(501)

    codops = get_codops_from_request()
    if not codops and not config.DEBUG:
        abort(404)
    return server.SPI_handler.on_request_xsi_1(codops, client_identifier)

@plugit.app.route('/radiodns/spi/3.1/SI.xml')
@with_client_identification
def si_3_xml(client_identifier):
    """
    Route for SPI 3.1 SI file
    :param client_identifier: The client identifier if any.
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

    if not config.SPISERVING_ENABLED:
        abort(501)

    codops = get_codops_from_request()
    if not codops and not config.DEBUG:
        abort(404)
    return server.SPI_handler.on_request_si_3(codops, client_identifier)

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
def pi_1_xml(path, date):
    """
    Route for RadioEPG 1.1 PI file

    :param path: the service identifier of the requested file. The service identifier is described
                    in the RadioDNS Lookup specification
    :param date: date in format YYYYMMDD
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

    if not config.SPISERVING_ENABLED:
        abort(501)

    return server.SPI_handler.on_request_pi_1(path, date)

@plugit.app.route('/radiodns/spi/3.1/<path:path>/<int:date>_PI.xml')
def pi_3_xml(path, date):
    """
    Route for RadioEPG 1.1 PI file

    :param path: the service identifier of the requested file. The service identifier is described
                    in the RadioDNS Lookup specification
    :param date: date in format YYYYMMDD
    :return: The requested file or its location if the SI/PI service is enabled. 404 if the requested resource was
     not found. 501 otherwise.
    """

    if not config.SPISERVING_ENABLED:
        abort(501)

    return server.SPI_handler.on_request_pi_3(path, date)
