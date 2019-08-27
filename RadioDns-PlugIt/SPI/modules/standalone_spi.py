from flask import Response, abort

from SPI.modules.base_spi import BaseSPI
import SPI.utils
from models import Clients


class StandaloneSPI(BaseSPI):
    """
    Implements BaseSPI by generating and serving the SI/PI files for each request. Useful for debug.
    """

    def on_si_resource_changed(self, event_name, service_provider, client=None):
        pass

    def on_pi_resource_changed(self, event_name, station):
        pass

    def on_request_xsi_1(self, codops, client_identifier):
        client = Clients.query.filter_by(identifier=client_identifier).first()
        return Response(SPI.utils.generate_si_file(SPI.utils.get_service_provider_from_codops(codops), client,
                                                    "radioepg/servicefollowing/xml1.html"), mimetype='text/xml')

    def on_request_si_3(self, codops, client_identifier):
        client = Clients.query.filter_by(identifier=client_identifier).first()
        return Response(SPI.utils.generate_si_file(SPI.utils.get_service_provider_from_codops(codops), client,
                                                    "radioepg/servicefollowing/xml3.html"), mimetype='text/xml')

    def on_request_pi_1(self, path, date):
        return Response(SPI.utils.generate_pi_file(date, "radioepg/schedule/xml1.html", path=path), mimetype='text/xml')

    def on_request_pi_3(self, path, date):
        return Response(SPI.utils.generate_pi_file(date, "radioepg/schedule/xml3.html", path=path), mimetype='text/xml')        
