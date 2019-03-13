import json

from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponse, \
    HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response

from lpp import settings
from lpp.settings import PLUGIT_APP_URL


def is_address_in_network(ip, net):
    """Is an address in a network"""
    # http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
    import socket
    import struct
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    if int(bits) == 0:
        return True
    net = struct.unpack('=L', socket.inet_aton(netaddr))[0]

    mask = ((2 << int(bits) - 1) - 1)

    return (ipaddr & mask) == (net & mask)


def is_request_address_in_networks(request, networks):
    """Helper method to check if the remote real ip of a request is in a network"""
    from ipware.ip import get_real_ip, get_ip

    # Get the real IP, i.e. no reverse proxy, no nginx
    ip = get_real_ip(request)
    if not ip:
        ip = get_ip(request)
        if not ip:
            return False

    # For all networks
    for network in networks:
        if is_address_in_network(ip, network):
            return True

    return False


def gen404(base_uri, reason, project=None):
    """Return a 404 error"""
    return HttpResponseNotFound(
        render_to_response('plugIt/404.html', {'context':
            {
                'reason': reason,
                'ebuio_baseUrl': base_uri,
            },
            'project': project
        }))


def gen500(base_uri, project=None):
    """Return a 500 error"""
    return HttpResponseServerError(
        render_to_response('plugIt/500.html', {
            'context': {
                'ebuio_baseUrl': base_uri,
            },
            'project': project
        }))


def gen403(reason):
    """Return a 403 error"""
    return HttpResponseForbidden(render_to_response('plugIt/403.html', {
        'context': {
            'reason': reason,
        },
    }))


def build_context(data, request, orga):
    data['ebuio_baseUrl'] = "/"
    if request.user.is_staff:
        request.user.ebuio_orga_admin = True
    data['ebuio_u'] = request.user

    data['ebuio_orga'] = dict()
    if not orga or orga.pk == -1:
        data['ebuio_orga']['name'] = "default organization"
    else:
        data['ebuio_orga']['name'] = orga.name
    return data


def check_permissions(request, target_meta, data):
    meta_codops = data['ebu_codops'] if 'ebu_codops' in data else "default"
    user_codops = None

    if request.user.is_authenticated:
        user_codops = "default" if not request.user.organization else request.user.organization.codops

    # User must be logged ?
    if target_meta \
            and 'only_logged_user' in target_meta \
            and not request.user.is_authenticated:
        return 'only_logged_user'

    # User must be member of the orga ?
    if target_meta \
            and 'only_orga_member_user' in target_meta \
            and (
                not request.user.is_authenticated
                or not user_codops == meta_codops
            ):
        return 'only_orga_member_user'

    # User must be administrator of the orga ?
    if target_meta \
            and 'only_orga_admin_user' in target_meta \
            and (
                not request.user.is_authenticated
                or not (request.user.is_staff or request.user.is_superuser)
                or not user_codops == meta_codops
            ):
        return 'only_orga_admin_user'

    # Remote IP must be in range ?
    if target_meta \
            and 'address_in_networks' in target_meta \
            and (
                not request.user.is_authenticated
                or not is_request_address_in_networks(request, target_meta['address_in_networks'])
            ):
        return 'address_in_networks'
    return None


def check_special_cases(request, target_meta, data):
    if request.method == 'OPTIONS':
        return HttpResponse('')

    if data is None:
        return gen404(request, PLUGIT_APP_URL, 'data')

    if data.__class__.__qualname__ == 'PlugIt500':
        return gen500(request, PLUGIT_APP_URL)

    if data.__class__.__qualname__ == 'PlugItSpecialCode':
        r = HttpResponse('')
        r.status_code = data.code
        return r

    if data.__class__.__qualname__ == 'PlugItRedirect':
        return HttpResponseRedirect(("/" if not data.url.startswith("/") else "") + data.url)

    if data.__class__.__qualname__ == 'PlugItFile':
        response = HttpResponse(data.content, content_type=data.content_type)
        response['Content-Disposition'] = data.content_disposition

        return response

    if data.__class__.__qualname__ == 'PlugItNoTemplate':
        response = HttpResponse(data.content)
        return response

    if target_meta.get('json_only', None):  # Just send the json back
        # Return application/json if requested
        if 'HTTP_ACCEPT' in request.META and request.META['HTTP_ACCEPT'].find('json') != -1:
            return JsonResponse(data)

        # Return json data without html content type, since json was not
        # requiered
        result = json.dumps(data)
        return HttpResponse(result)

    if target_meta.get('xml_only', None):  # Just send the xml back
        return HttpResponse(data['xml'], content_type='application/xml')
    return None


def build_additional_headers(request, orga):
    additional_headers = {}
    if orga:
        additional_headers = {'orga_pk': str(orga.id), 'orga_name': orga.name, 'orga_codops': orga.codops,
                              'base_url': PLUGIT_APP_URL}

    if request and hasattr(request, 'META'):
        if 'REMOTE_ADDR' in request.META:
            additional_headers['remote-addr'] = request.META['REMOTE_ADDR']

        if 'HTTP_X_FORWARDED_FOR' in request.META and getattr(settings, 'HONOR_X_FORWARDED_FOR'):
            additional_headers['remote-addr'] = request.META['HTTP_X_FORWARDED_FOR']

        for meta_header, dest_header in [
            ('HTTP_IF_NONE_MATCH', 'If-None-Match'),
            ('HTTP_ORIGIN', 'Origin'),
            ('HTTP_ACCESS_CONtROL_REQUEST_METHOD', 'Access-Control-Request-Method'),
            ('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Access-Control-Request-Headers'),
        ]:
            if meta_header in request.META:
                additional_headers[dest_header] = request.META[meta_header]

    return additional_headers


def get_current_session(request):
    """Get the current session value"""

    result = {}

    for key, value in list(request.session.items()):
        if key.startswith('plugit_standalone_'):
            result[key[len('plugit_standalone_'):]] = value

    return result


def update_session(request, session_to_set):
    """Update the session with users-realted values"""

    for key, value in session_to_set.items():
        request.session['plugit_standalone_' + key] = value

