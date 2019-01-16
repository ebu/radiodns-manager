import re
from io import BufferedReader

from requests_toolbelt import MultipartEncoder

BASE_HOST = "http://127.0.0.1:62314"


def get_query_string_param(url, query_strings, route_name, param_name):
    res = re.compile("""^http://.+\/{}\?{}=(?P<param>.+)$""".format(route_name, param_name)) \
        .search(url + query_strings)

    param_value = ""
    if res and "param" in res.groupdict():
        param_value = res.groupdict()["param"]
    return param_value


def parse_body(body):
    parsed_value = dict()

    if type(body["data"]) is MultipartEncoder:
        for key, value in body["data"].fields:
            if value is BufferedReader:
                parsed_value[key] = value.read().decode("utf8")
            elif key in parsed_value:
                parsed_value[key] = [parsed_value[key], value]
            else:
                parsed_value[key] = value
    else:
        for key, value in body["data"].items():
            parsed_value[key] = value

    if body["params"]:
        for key, value in body["params"].items():
            parsed_value[key] = value
    return parsed_value


def cookie_extractor(kwargs):
    cookies = re.split("; |=|;", kwargs["headers"]['Cookie'])[:-1]
    return dict(cookies[i:i + 2] for i in range(0, len(cookies), 2))


# This method will be used by the mock to replace requests.get
def mocked_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    query_strings = ""

    if "params" in kwargs and kwargs["params"]:
        query_strings += "?"
        for key, value in kwargs["params"].items():
            query_strings += key + "=" + value + "&"
        query_strings = query_strings[:-1]

    if args[0] == "GET":
        if args[1] == BASE_HOST + '/_':
            return None
        elif args[1] == BASE_HOST + "/test_get":
            return MockResponse(
                {
                    'method': 'GET',
                    "get_param": get_query_string_param(args[1], query_strings, "test_get", "get_param")
                },
                200)
        elif args[1] == BASE_HOST + "/test_additional_headers":
            return MockResponse({"x-plugit-test": kwargs["headers"]['X-Plugit-test'].decode("utf8")}, 200)
        elif args[1] == BASE_HOST + "/test_session":
            return MockResponse(
                {
                    "x-plugitsession-test": kwargs["headers"]['X-Plugitsession-test'],
                    "cookie-test": cookie_extractor(kwargs)["test"],
                },
                200,
            )

    if args[0] == BASE_HOST + '/test_post':
        return MockResponse(
            {
                'method': 'POST',
                "get_param": get_query_string_param(args[0], query_strings, "test_post", "get_param"),
                **parse_body(kwargs),
            },
            200)
    elif args[0] == BASE_HOST + "/test_post_list":
        return MockResponse(
            {
                **parse_body(kwargs),
                'method': 'POST',
            },
            200)
    elif args[0] == BASE_HOST + "/test_additional_headers":
        return MockResponse({"x-plugit-test": kwargs["headers"]['X-Plugit-test'].decode("utf8")}, 200)
    elif args[0] == BASE_HOST + "/test_session":
        return MockResponse(
            {
                "x-plugitsession-test": kwargs["headers"]['X-Plugitsession-test'],
                "cookie-test": cookie_extractor(kwargs)["test"],
            },
            200,
        )
    elif args[0] == BASE_HOST + "/test_fileupload":
        return MockResponse(
            {
                'file-test': kwargs["data"].fields[0][1][1].read().decode("utf8")
            },
            200,
        )

    return MockResponse(None, 404)
