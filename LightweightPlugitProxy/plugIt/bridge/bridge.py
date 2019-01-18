import random
import string
from datetime import datetime

import requests
from dateutil import parser
from dateutil.tz import tzutc
from django.core.cache import cache
from requests import Response
from requests_toolbelt import MultipartEncoder


class PlugItRedirect:
    """Object to perform a redirection"""

    def __init__(self, url, no_prefix=False):
        self.url = url
        self.no_prefix = no_prefix


class PlugItFile:
    """Object to send a file"""

    def __init__(self, content, content_type, content_disposition=''):
        self.content = content
        self.content_type = content_type
        self.content_disposition = content_disposition


class PlugItNoTemplate:
    """Object to display content without a template"""

    def __init__(self, content):
        self.content = content


class PlugIt500:
    """Object to return a 500"""
    pass


class PlugItSpecialCode:
    """Object to return a special status code"""

    def __init__(self, code):
        self.code = code


class Bridge:
    """Manage access to a specific server. Use caching for templates and meta information..."""

    PI_API_VERSION = '1'
    PI_API_NAME = 'EBUio-PlugIt'

    def __init__(self, base_uri, check_availability=False):
        """Instance a new plugIt instance. Need the base URI of the server"""
        self.base_uri = base_uri
        self.cacheKey = 'lpp'

        if check_availability:
            # Check if everything is ok
            if not self.ping():
                raise Exception("Server doesn't reply to ping !")

    def do_query(self, url, method='GET', query_string=None, body=None, files=None, additional_headers=None,
                 session=None):
        """
        Submit a GET or POST request to a PlugIt application with the PlugIt protocol.

        :param url: the url to call.
        :param method: 'GET' or 'POST'.  Raises ValueError exception if this argument is not 'GET' or 'POST'.
        :param query_string: Query string parameters.
        :param body: Request body: dict that will be interpreted as json object.
        :param files: Files for the request.
        :param additional_headers: Additional headers that will be converted as PlugIt headers.
        That basically consist of appening the name of the header to the 'X-Plugitsession-' string and setting its
        value with one you provided.
        :param session:
        :return: The Request's result.
        """

        try:
            # Build headers
            headers = {}

            for key, value in (additional_headers or {}).items():
                # Fixes #197 for values with utf-8 chars to be passed into plugit
                headers['X-Plugit-' + key] = value.encode('utf-8') if isinstance(value, str) else value

            for key, value in (session or {}).items():
                headers['X-Plugitsession-' + key] = value
                if 'Cookie' not in headers:
                    headers['Cookie'] = ''
                headers['Cookie'] += key + '=' + str(value) + '; '

            if method == 'POST':
                body = body or {}
                if files:
                    data = []

                    # Add the rest of the body.
                    for key, value in body.items():
                        if type(value) is int:
                            body[key] = str(value)

                        if isinstance(body[key], list):
                            for elem in body[key]:
                                data.append((key, elem))
                        else:
                            data.append((key, body[key]))

                    # Add buffered readers for files.
                    for key, f in files.items():
                        data.append((key, (f.name, open(f.temporary_file_path(), 'rb'), 'application/octet-stream')))

                    # Multipart body construction.
                    body = MultipartEncoder(fields=data)

                    # Set correct Content-Type for multipart query.
                    headers['Content-Type'] = body.content_type
                response = requests.post(self.base_uri + '/' + url, params=query_string, data=body, stream=True,
                                         headers=headers)
            else:
                # Call the function based on the method.
                response = requests.request(method.upper(), self.base_uri + '/' + url, params=query_string, stream=True,
                                            headers=headers, allow_redirects=True)

            return response
        except requests.exceptions.ConnectionError:
            response = Response()
            response.status_code = 500
            return response

    def ping(self):
        """Return true if the server successfully pinged"""

        random_token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))

        try:
            response = self.do_query('ping?data=' + random_token)
        except requests.exceptions.ConnectionError:
            return False

        return response.status_code == 200 and response.json()['data'] == random_token

    def new_mail(self, data, message):
        """
        Send a mail to a PlugIt server.

        :param data: Data for the email. FIXME WHAT IS THIS DATA?
        :param message: The email contents.
        :return: True if the email was send successfully, false otherwise.
        """
        response = self.do_query('mail', method='POST', body={'response_id': str(data), 'message': str(message)})

        if response.status_code == 200:
            data = response.json()
            return data['result'] == 'Ok'

        return False

    def get_media(self, uri):
        """
        Return a tuple with a media and his content-type. Don't cache anything !

        :param uri: The uri of the media. The media should be located under the /media route.
        :return: The response's content, the content type and the cache control if any (None otherwise).
        """

        response = self.do_query('media/' + uri)

        if response.status_code != 200:
            return None, None, None

        if 'content-type' in response.headers:
            content_type = response.headers['content-type']
        else:
            content_type = 'application/octet-stream'

        if 'cache-control' in response.headers:
            cache_control = response.headers['cache-control']
        else:
            cache_control = None

        return response.content, content_type, cache_control

    def get_meta(self, uri):
        """
        Returns meta information about an action. Cache the result as specified by the queried server.

        :param uri: The uri of the action.
        :return: the meta.
        """

        media_key = (self.cacheKey + '_meta_' + uri).replace(' ', '__')
        meta = cache.get(media_key, None)

        # Nothing found -> Retrieve it from the server and cache it
        if not meta:
            response = self.do_query('meta/' + uri)

            if response.status_code == 200:  # Get the content if there is not problem. Otherwise the template will stay to None
                meta = response.json()

            if 'expire' not in response.headers:
                expire = 5 * 60  # 5 minutes of cache if the server didn't specified anything
            else:
                expire = int((parser.parse(response.headers['expire']) - datetime.now(
                    tzutc())).total_seconds())  # Use the server value for cache

            if expire > 0:  # is caching requested by the server ?
                cache.set(media_key, meta, expire)

        return meta

    def get_template(self, uri, meta=None):
        """
        Returns the template for an action.

        Caches the result. Can use an optional meta parameter with meta information.

        :param uri: The uri of the template. FIXME Anything special about this uri?
        :param meta: The optional meta parameter. FIXME What does this meta do?
        :return: The template.
        """

        if not meta:
            meta_key = self.cacheKey + '_templatesmeta_cache_' + uri

            meta = cache.get(meta_key, None)

            if not meta:
                meta = self.get_meta(uri)
                cache.set(meta_key, meta, 15)

        if not meta:  # No meta, can return a template
            return None

        template_key = self.cacheKey + '_templates_' + uri + '_' + meta['template_tag']
        template = cache.get(template_key, None)

        # Nothing found -> Retrieve it from the server and cache it
        if not template:
            response = self.do_query('template/' + uri)

            if response.status_code == 200:  # Get the content if there is not problem. If there is, template will stay to None
                template = response.content

            cache.set(template_key, template, None)  # None = Cache forever

        return template if type(template) is str else template.decode('utf-8')

    def do_action(self, uri, method='GET', query_string=None, body=None, files=None, additional_headers=None,
                  session=None):
        """

        :param uri: the uri to call. FIXME does this url requires a special format?
        :param method: 'GET' or 'POST'. Raises ValueError exception if this argument is not 'GET' or 'POST'.
        :param query_string: Query string parameters.
        :param body: Request body: dict that will be interpreted as json object.
        :param files: Files for the request.
        :param additional_headers: Additional headers that will be converted as PlugIt headers.
        That basically consist of appening the name of the header to the 'X-Plugitsession-' string and setting its
        value with one you provided.
        :param session
        :return: The Request's result with the session and headers to set.
        """

        response = self.do_query('action/' + uri, method=method, query_string=query_string, body=body,
                                 files=files, additional_headers=additional_headers, session=session)

        if response.status_code == 500:
            return PlugIt500(), {}, {}
        if response.status_code in [429, 404, 403, 401, 304]:
            return PlugItSpecialCode(response.status_code), {}, {}
        if response.status_code != 200:
            return None, {}, {}

        session_to_set = {}

        for key, value in response.headers.items():
            attr = 'ebuio-plugit-setsession-'
            if key.lower().startswith(attr):
                session_to_set[key[len(attr):]] = value

        # Build list of headers to forward
        headers_to_set = {}

        for header in [
            'ETag',
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Credentials',
            'Access-Control-Expose-Headers',
            'Access-Control-Max-Age',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]:
            if header in response.headers:
                headers_to_set[header] = response.headers[header]

        if 'ebuio-plugit-redirect' in response.headers:
            no_prefix = False

            if 'ebuio-plugit-redirect-noprefix' in response.headers:
                no_prefix = response.headers['ebuio-plugit-redirect-noprefix'] == 'True'

            return PlugItRedirect(response.headers['ebuio-plugit-redirect'], no_prefix), session_to_set, headers_to_set

        if 'ebuio-plugit-itafile' in response.headers:

            if 'content-disposition' in response.headers:
                content_disposition = response.headers['content-disposition']
            else:
                content_disposition = ''

            return (
                PlugItFile(response.content, response.headers['Content-Type'], content_disposition), session_to_set,
                headers_to_set)

        if 'ebuio-plugit-notemplate' in response.headers:
            return PlugItNoTemplate(response.content), session_to_set, headers_to_set

        return response.json(), session_to_set, headers_to_set

    def check_version(self):
        """Check if the server use the same version of our protocol"""

        response = self.do_query('version')

        if response.status_code == 200:
            data = response.json()

            if data['result'] == 'Ok' and data['version'] == self.PI_API_VERSION and data['protocol'] == self.PI_API_NAME:
                return True
        return False
