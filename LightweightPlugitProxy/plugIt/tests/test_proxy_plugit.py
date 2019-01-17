import json
import uuid
from unittest import TestCase

from plugIt.bridge.bridge import Bridge


class TestPlugIt(TestCase):

    def setUp(self):

        self.plugIt = Bridge('http://0.0.0.0/')

        _self = self

        def _do_query(url, method='GET', query_string=None, body=None, files=None, additional_headers=None,
                 session=None):
            _self.last_do_query_call = {'url': url, 'method': method, 'query_string': query_string,
                                        'body': body, 'files': files, 'additional_headers': additional_headers,
                                        'session': session}

            class DummyResponse:
                def json(self):
                    return _self.plugIt.toReplyJson()

                @property
                def status_code(self):
                    return _self.plugIt.toReplyStatusCode()

                @property
                def headers(self):
                    return _self.plugIt.toReplyHeaders()

                @property
                def content(self):
                    return json.dumps(self.json())

            return DummyResponse()

        self.plugIt.do_query = _do_query

    def test_ping(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'data': self.last_do_query_call['url'].split('data=', 1)[1]}

        assert (self.plugIt.ping())

        self.plugIt.toReplyStatusCode = lambda: 404

        assert (not self.plugIt.ping())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'data': self.last_do_query_call['url'].split('data=', 1)[1] * 2}

        assert (not self.plugIt.ping())

        assert (self.last_do_query_call['url'].startswith('ping'))

    def test_check_version(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION,
                                           'protocol': self.plugIt.PI_API_NAME}

        assert (self.plugIt.check_version())
        assert (self.last_do_query_call['url'] == 'version')

        self.plugIt.toReplyJson = lambda: {'result': 'poney', 'version': self.plugIt.PI_API_VERSION,
                                           'protocol': self.plugIt.PI_API_NAME}
        assert (not self.plugIt.check_version())

        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION * 2,
                                           'protocol': self.plugIt.PI_API_NAME}
        assert (not self.plugIt.check_version())

        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION,
                                           'protocol': self.plugIt.PI_API_NAME * 2}
        assert (not self.plugIt.check_version())

        self.plugIt.toReplyStatusCode = lambda: 201
        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION,
                                           'protocol': self.plugIt.PI_API_NAME}

        assert (not self.plugIt.check_version())

    def test_new_mail(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'result': 'Ok'}

        message_id = str(uuid.uuid4())
        message = str(uuid.uuid4())

        assert (self.plugIt.new_mail(message_id, message))
        assert (self.last_do_query_call['url'] == 'mail')
        assert (self.last_do_query_call['body'].get('response_id') == message_id)
        assert (self.last_do_query_call['body'].get('message') == message)

        self.plugIt.toReplyStatusCode = lambda: 201
        assert (not self.plugIt.new_mail(message_id, message))

    def test_media(self):
        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        media = str(uuid.uuid4())

        data, content_type, cache_control = self.plugIt.get_media(media)

        assert (data == '{}')
        assert (content_type == 'application/octet-stream')
        assert (self.last_do_query_call['url'] == 'media/{}'.format(media))
        assert (not cache_control)

        self.plugIt.toReplyHeaders = lambda: {'content-type': 'test', 'cache-control': 'public, max-age=31536000'}

        data, content_type, cache_control = self.plugIt.get_media(media)

        assert (data == '{}')
        assert (content_type == 'test')
        assert (cache_control == 'public, max-age=31536000')

        self.plugIt.toReplyStatusCode = lambda: 201
        data, content_type, cache_control = self.plugIt.get_media(media)
        assert (not data)
        assert (not content_type)

    def test_meta(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'expire': 'Wed, 21 Oct 2015 07:28:00 GMT'}

        data = self.plugIt.get_meta(path)
        assert (self.last_do_query_call['url'] == 'meta/{}'.format(path))
        assert (data['k'] == k)

        # Data should not be cached
        self.plugIt.toReplyJson = lambda: {'k2': k}
        data = self.plugIt.get_meta(path)
        assert (data['k2'] == k)

    def test_meta_fail(self):
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 201
        self.plugIt.toReplyHeaders = lambda: {}
        assert (not self.plugIt.get_meta(path))

    def test_meta_cache(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {}

        # Data should be cached
        data = self.plugIt.get_meta(path)
        self.plugIt.toReplyJson = lambda: {'k2': k}
        data = self.plugIt.get_meta(path)
        assert (data['k'] == k)

    def test_template(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k, 'template_tag': '-'}
        self.plugIt.toReplyHeaders = lambda: {}

        data = json.loads(self.plugIt.get_template(path))
        assert (self.last_do_query_call['url'] == 'template/{}'.format(path))
        assert (data['k'] == k)

        # Data should be cached
        self.plugIt.toReplyJson = lambda: {'k2': k, 'template_tag': '-'}
        data = json.loads(self.plugIt.get_template(path))
        assert (data['k'] == k)

    def test_template_fail(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 201
        self.plugIt.toReplyHeaders = lambda: {}
        assert (not self.plugIt.get_template(path))

    def test_template_no_meta_no_template(self):
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}
        assert (not self.plugIt.get_template(path))

    def test_do_action_normal_mode(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        assert (self.plugIt.do_action(path) == ({}, {}, {}))
        assert (self.last_do_query_call['url'] == 'action/{}'.format(path))

    def test_do_action_proxy_mode(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        assert self.plugIt.do_action(path) == ({}, {}, {})
        assert self.last_do_query_call['url'] == "action/" + path

    def test_do_action_proxy_mode_no_remplate(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-notemplate': True}

        r, __, __ = self.plugIt.do_action('')

        assert (r.__class__.__name__ == 'PlugItNoTemplate')
        assert (json.loads(r.content)['k'] == k)

    def test_do_action_data(self):

        path = str(uuid.uuid4())
        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {}

        assert (self.plugIt.do_action(path) == ({'k': k}, {}, {}))

    def test_do_action_500(self):
        self.plugIt.toReplyStatusCode = lambda: 500
        assert (self.plugIt.do_action('')[0].__class__.__name__ == 'PlugIt500')

    def test_do_action_fail(self):
        self.plugIt.toReplyStatusCode = lambda: 501
        assert (self.plugIt.do_action('') == (None, {}, {}))

    def test_do_action_special_codes(self):

        special_codes = [429, 404, 403, 401, 304]

        for x in range(200, 500):
            self.plugIt.toReplyStatusCode = lambda: x
            self.plugIt.toReplyHeaders = lambda: {}
            self.plugIt.toReplyJson = lambda: {}
            r, __, __ = self.plugIt.do_action('')

            if x in special_codes:
                assert (r.__class__.__name__ == 'PlugItSpecialCode')
                assert (r.code == x)
            else:
                assert (r.__class__.__name__ != 'PlugItSpecialCode')

    def test_do_action_session(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'Ebuio-PlugIt-SetSession-k': k}
        assert (self.plugIt.do_action('') == ({}, {'k': k}, {}))

    def test_do_action_redirect(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-redirect': k}
        r, session, headers = self.plugIt.do_action('')

        assert (r.__class__.__name__ == 'PlugItRedirect')
        assert (r.url == k)
        assert (not r.no_prefix)
        assert (session == {})
        assert (headers == {})

    def test_do_action_redirect_noprefix(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-redirect': k, 'ebuio-plugit-redirect-noprefix': "True"}
        r, session, headers = self.plugIt.do_action('')

        assert (r.__class__.__name__ == 'PlugItRedirect')
        assert (r.url == k)
        assert (r.no_prefix)
        assert (session == {})
        assert (headers == {})

    def test_do_action_file(self):

        k = str(uuid.uuid4())
        content_type = str(uuid.uuid4())
        content_disposition = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-itafile': k, 'Content-Type': content_type}
        r, session, headers = self.plugIt.do_action('')

        assert (r.__class__.__name__ == 'PlugItFile')
        assert (json.loads(r.content)['k'] == k)
        assert (r.content_type == content_type)
        assert (r.content_disposition == '')
        assert (session == {})
        assert (headers == {})

        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-itafile': k, 'Content-Type': content_type,
                                              'content-disposition': content_disposition}
        r, __, __ = self.plugIt.do_action('')
        assert (r.content_disposition == content_disposition)

    def test_do_action_etag(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ETag': k}
        r, session, headers = self.plugIt.do_action('')

        assert (headers == {'ETag': k})

    def test_do_action_crossdomain(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}

        for header in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials',
                       'Access-Control-Expose-Headers', 'Access-Control-Max-Age', 'Access-Control-Allow-Methods',
                       'Access-Control-Allow-Headers']:
            self.plugIt.toReplyHeaders = lambda: {header: k}
            r, session, headers = self.plugIt.do_action('')

            assert (headers == {header: k})
