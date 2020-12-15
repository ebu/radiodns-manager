# Create your views here.
from apps.si_pi.si_pi_serving_provider import get_serving_provider
from apps.si_pi.si_pi_serving_provider.utilities import get_codops_from_request


def SiThreeView(request):
    return get_serving_provider().on_request_si_3(get_codops_from_request(request), None)


def SiOneView(request):
    return get_serving_provider().on_request_xsi_1(get_codops_from_request(request), None)


def PiThreeView(request, path, date):
    return get_serving_provider().on_request_pi_3(request, path, date)


def PiOneView(request, path, date):
    return get_serving_provider().on_request_pi_1(request, path, date)
