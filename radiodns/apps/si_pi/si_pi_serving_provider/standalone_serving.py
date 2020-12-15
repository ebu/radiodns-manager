from django.http import HttpResponse

from apps.clients.models import Client
from apps.si_pi.si_pi_serving_provider.base_serving import BaseServing
from apps.si_pi.si_pi_serving_provider.utilities import generate_si_file, generate_pi_file


class StandaloneServing(BaseServing):
    """
    Implements BaseServing by generating and serving the SI/PI files for each request. Useful for debug.
    """

    def on_si_resource_changed(self, event_name, service_provider, client=None):
        pass

    def on_pi_resource_changed(self, event_name, station):
        pass

    def on_request_xsi_1(self, codops, client_identifier):
        return StandaloneServing._render_si(codops, client_identifier, "servicefollowing/xml1.html")

    def on_request_si_3(self, codops, client_identifier):
        return StandaloneServing._render_si(codops, client_identifier, "servicefollowing/xml3.html")

    def on_request_pi_1(self, request, path, date):
        return StandaloneServing._render_pi(request, path, date, "schedule/xml1.html")

    def on_request_pi_3(self, request, path, date):
        return StandaloneServing._render_pi(request, path, date, "schedule/xml3.html")

    @staticmethod
    def _render_si(codops, client_identifier, template_name):
        client = Client.objects.filter(identifier=client_identifier).first()
        return HttpResponse(generate_si_file(codops, client, template_name), content_type='text/xml')

    @staticmethod
    def _render_pi(request, date, path, template_name):
        hostname = request.META['HTTP_HOST']
        return HttpResponse(generate_pi_file(hostname, date, template_name, path), content_type='text/xml')
