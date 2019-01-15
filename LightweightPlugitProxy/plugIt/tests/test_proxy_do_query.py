import os
import tempfile
import uuid
from unittest import TestCase
from unittest import mock

from plugIt.bridge.bridge import Bridge
from plugIt.tests.helpers.files_utilities import build_file
from plugIt.tests.helpers.mocked_responses import BASE_HOST, mocked_requests


class TestPlugItBridgeDoQueryTest(TestCase):

    def setUp(self):
        self.plugit = Bridge(BASE_HOST)

    @mock.patch('plugIt.bridge.bridge.requests.request', side_effect=mocked_requests)
    def test_get(self, _):
        result = self.plugit.do_query("test_get").json()
        assert result['method'] == 'GET'

    @mock.patch('plugIt.bridge.bridge.requests.request', side_effect=mocked_requests)
    def test_404(self, _):
        result = self.plugit.do_query("_")
        assert not result

    @mock.patch('plugIt.bridge.bridge.requests.request', side_effect=mocked_requests)
    def test_get_param(self, _):
        p = str(uuid.uuid4())
        result = self.plugit.do_query("test_get", query_string={'get_param': p}).json()
        assert result['method'] == 'GET'
        assert result['get_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post(self, _):
        result = self.plugit.do_query("test_post", method='POST').json()
        assert result['method'] == 'POST'

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post_param(self, _):
        p = str(uuid.uuid4())
        result = self.plugit.do_query("test_post", method='POST', body={'post_param': p}).json()
        assert result['method'] == 'POST'
        assert result['post_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post_param_list(self, _):
        p = [str(uuid.uuid4()), str(uuid.uuid4())]
        result = self.plugit.do_query("test_post_list", method='POST', body={'post_param': p}).json()
        assert result['method'] == 'POST'
        assert result['post_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post_getparam(self, _):
        p = str(uuid.uuid4())
        result = self.plugit.do_query("test_post", method='POST', query_string={'get_param': p}).json()
        assert result['method'] == 'POST'
        assert result['get_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.request', side_effect=mocked_requests)
    def test_additional_headers_get(self, _):
        p = str(uuid.uuid4())

        result = self.plugit.do_query("test_additional_headers", method='GET', additional_headers={'test': p}).json()
        assert result['x-plugit-test'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_additional_headers_post(self, _):
        p = str(uuid.uuid4())

        result = self.plugit.do_query("test_additional_headers", method='POST', additional_headers={'test': p}).json()
        assert result['x-plugit-test'] == p

    @mock.patch('plugIt.bridge.bridge.requests.request', side_effect=mocked_requests)
    def test_additional_headers_bytes_get(self, _):
        p = str(uuid.uuid4()).encode('utf-8')

        result = self.plugit.do_query("test_additional_headers", method='GET', additional_headers={'test': p}).json()
        assert result['x-plugit-test'] == p.decode("utf8")

    @mock.patch('plugIt.bridge.bridge.requests.request', side_effect=mocked_requests)
    def test_session_get(self, _):
        p = str(uuid.uuid4())

        result = self.plugit.do_query("test_session", method='GET', session={'test': p}).json()
        assert result['x-plugitsession-test'] == p
        assert result['cookie-test'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_session_post(self, _):
        p = str(uuid.uuid4())

        result = self.plugit.do_query("test_session", method='POST', session={'test': p}).json()
        assert result['x-plugitsession-test'] == p
        assert result['cookie-test'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_fileupload(self, _):
        p = str(uuid.uuid4())
        (handle, tmpfile) = tempfile.mkstemp()
        handle = open(tmpfile, 'wb')
        handle.write(p.encode("utf8"))
        handle.close()

        class FileObj:
            def temporary_file_path(self):
                return tmpfile

            name = 'test'

        result = self.plugit.do_query("test_fileupload", method='POST', files={'test': FileObj()}).json()

        os.unlink(tmpfile)

        assert (result['file-test'] == p)

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post_param_with_files(self, _):
        fname, fobj = build_file()

        p = str(uuid.uuid4())
        result = self.plugit.do_query("test_post", method='POST', body={'post_param': p}, files={'test': fobj}).json()

        os.unlink(fname)

        assert result['method'] == 'POST'
        assert result['post_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post_getparam_with_files(self, _):
        fname, fobj = build_file()
        p = str(uuid.uuid4())
        result = self.plugit.do_query("test_post", method='POST', query_string={'get_param': p},
                                      files={'test': fobj}).json()
        os.unlink(fname)
        assert result['method'] == 'POST'
        assert result['get_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_post_postparam_list_with_files(self, _):
        fname, fobj = build_file()
        p = [str(uuid.uuid4()), str(uuid.uuid4())]
        result = self.plugit.do_query("test_post_list", method='POST', body={'post_param': p},
                                      files={'test': fobj}).json()
        os.unlink(fname)
        assert result['method'] == 'POST'
        assert result['post_param'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_additional_headers_post_with_files(self, _):
        fname, fobj = build_file()
        p = str(uuid.uuid4())

        result = self.plugit.do_query("test_additional_headers", method='POST', additional_headers={'test': p},
                                      files={'test': fobj}).json()
        os.unlink(fname)
        assert result['x-plugit-test'] == p

    @mock.patch('plugIt.bridge.bridge.requests.post', side_effect=mocked_requests)
    def test_session_post_with_files(self, _):
        fname, fobj = build_file()
        p = str(uuid.uuid4())

        result = self.plugit.do_query("test_session", method='POST', session={'test': p}, files={'test': fobj}).json()
        os.unlink(fname)
        assert result['x-plugitsession-test'] == p
        assert result['cookie-test'] == p
