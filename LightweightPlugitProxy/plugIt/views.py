import json

import requests
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Template, RequestContext
from django.views.decorators.cache import cache_control

from lpp.settings import PLUGIT_APP_URL
from lpp_core.models import Organization
from plugIt.bridge.bridge import Bridge
from plugIt.bridge.query_string_parameters import build_parameters
from plugIt.bridge.utilities import gen500, build_context, check_permissions, check_special_cases, \
    build_additional_headers, get_current_session, update_session


def main(request, query):
    bridge = Bridge(PLUGIT_APP_URL)

    if not bridge.ping():
        return render_to_response('plugIt/error_plugit_app_dead.html')

    target_meta = bridge.get_meta(query)

    # ================ BUILD ACTION PARAMETERS AND HEADERS ======
    # FIXME current orga must be return either from session or from first orga of user.
    orga = request.user.organization if request.user.is_authenticated and request.user.organization else None
    additional_headers = build_additional_headers(request, orga)
    session = get_current_session(request)

    query_string, body, files = build_parameters(request, target_meta, orga)

    data, session_to_set, headers_to_set = bridge.do_action(
        uri=query,
        additional_headers=additional_headers,
        query_string=query_string,
        method=request.method,
        body=body,
        files=files,
        session=session,
    )

    update_session(request, session_to_set)

    # ================ SPECIAL CASES HANDLING ===============
    check_result = check_special_cases(request, target_meta, data)
    if check_result is not None:
        for header, value in headers_to_set.items():
            check_result[header] = value
        return check_result

    # ================ AUTHORIZATION ================
    check_result = check_permissions(request, target_meta, data)
    if check_result is not None:
        return check_result

    # ================ RENDER PLUGIT TEMPLATE =======
    target_template = bridge.get_template(query, target_meta)
    target_menu_template = bridge.get_template("menubar", target_meta)

    data = build_context(data, request, orga)
    target_context = RequestContext(request, data)

    result = render_to_response("plugIt/plugItBase.html", context={
        'plugit_content': Template(target_template).render(target_context),
        'plugit_menu': Template(target_menu_template).render(target_context),
        **data,
    })

    for header, value in headers_to_set.items():
        result[header] = value

    return result


@cache_control(public=True, max_age=3600)
def media(request, path):
    """Ask the server for a media and return it to the client browser. Forward cache headers."""

    bridge = Bridge(PLUGIT_APP_URL)

    try:
        media, content_type, cache_control = bridge.get_media(path)
    except Exception:
        return gen500(request, PLUGIT_APP_URL)

    if not media:  # No media returned
        raise Http404

    response = HttpResponse(media)
    response['Content-Type'] = content_type
    response['Content-Length'] = len(media)

    if cache_control:
        response['Cache-Control'] = cache_control

    return response


def api_home(request):
    """Show the home page for the API with all methods"""

    return render_to_response('plugIt/api.html')


def api_orga(request, orga_pk):
    """Return information about an organization"""
    retour = {}

    if orga_pk == '-1':
        retour['ebuio_orgapk'] = -1
        retour['pk'] = -1
        retour['name'] = "default"
        retour['codops'] = "default"
    else:
        orga = get_object_or_404(Organization, pk=orga_pk)

        retour['ebuio_orgapk'] = orga.pk
        retour['pk'] = orga.pk
        retour['name'] = orga.name
        retour['codops'] = orga.codops

    return HttpResponse(json.dumps(retour), content_type="application/json")
