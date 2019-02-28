from flask import Response, abort

from SPI.modules.base_spi import BaseSPI
import SPI.utils
from models import Clients


class StandaloneSPI(BaseSPI):
    def on_event_epg_1(self, event_name, service_provider_meta, client=None):
        pass

    def on_event_epg_3(self, event_name, service_provider_meta, client=None):
        pass

    def on_request_epg_1(self, codops, client_identifier):
        client = Clients.query.filter_by(identifier=client_identifier).first()
        if not client:
            abort(404)
        return Response(SPI.utils.generate_spi_file(SPI.utils.get_service_provider_from_codops(codops), client,
                                                    "radioepg/servicefollowing/xml1.html"), mimetype='text/xml')

    def on_request_epg_3(self, codops, client_identifier):
        client = Clients.query.filter_by(identifier=client_identifier).first()
        if not client:
            abort(404)
        return Response(SPI.utils.generate_spi_file(SPI.utils.get_service_provider_from_codops(codops), client,
                                                    "radioepg/servicefollowing/xml3.html"), mimetype='text/xml')
