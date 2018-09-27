from plugit.api import PlugItAPI

import config
from models import ServiceProvider


def get_orga_service_provider(request):
    """
    Returns the service provider and the organisation of the request if any present in body or url.
    :param request: The flask request.
    :return: The service provider and the organisation if any, (None, None) otherwise.
    """
    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
    return orga, sp
