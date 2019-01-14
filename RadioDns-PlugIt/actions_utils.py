import re
from functools import wraps

import simplejson
from flask import request, make_response
from jsonschema import validate, ValidationError, SchemaError
from plugit.api import PlugItAPI
from simplejson import JSONDecodeError

import config
from models import ServiceProvider, Clients


def json_form_extractor(form_keys, known_keys):
    """
    Utility to extract a json value from a PlugIt proxy forwarded JSON request. Works by filtering the form
    object of its known keys and and return the rest as a list of potentials json values that could be parsed.

    :param form_keys: The keys of the flask request.form dictionary.
    :param known_keys: The list of the known keys.
    :return: a filtered request.form's keys list.
    """
    filtered = filter(lambda key: key not in known_keys, form_keys)
    if len(filtered) == 0:
        raise ValidationError("No json found in request.")
    return filtered


def kwargs_extractor(fields, kwargs):
    """
    Utility function to extract keywords arguments.

    :param fields: List of keys that the extractor will try to use to get their corresponding values in a function kwargs.
    :param kwargs: The kwargs from where to extract.
    :return: Extracted kwargs.
    """
    querykwargs = {}
    for field in fields:
        querykwargs[field] = kwargs[field]
    return querykwargs


def with_json_validated_and_decoded(schema):
    """
    Decorator factory for PlugIt controllers. Look for a json value in the flask request.form object and validates it
    against the specified json validation schema. Returns an error if more than one json string value
    is found in the request.form object or if the json is invalid.

    :param schema: Json validation schema.
    :return: decorated function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                json_strings = json_form_extractor(args[0].form.keys(), ["ebuio_orgapk"])
                if len(json_strings) != 1:
                    return {
                        'error': """Too many json strings to decode: {len}""".format(len=len(json_strings)),
                        'status': 422,
                    }
                decoded = simplejson.loads(json_strings[0])
                validate(decoded, schema)
                new_args = args + (decoded,)
                return f(*new_args, **kwargs)
            except (ValidationError, SchemaError, JSONDecodeError) as e:
                return {
                    'error': e.message,
                    'status': 422,
                }

        return decorated_function

    return decorator


def error_boundary(exception, handler):
    """
    Decorator factory for PlugIt controllers. Error boundary (exception catcher) of any specified exceptions thrown by
    the function. Returns the return value of the handler as a json response if any specified exception was caught.

    :param exception: The exception or a tuple of exceptions class that the error boundary will catch.
    :param handler: Callback to handle the exception. Takes the exception as parameter, must return a dictionary of the
    shape: {error: string, status: number}
    :return: decorated function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            try:
                return f(*args, **kwargs)
            except exception as e:
                return handler(e)

        return decorated_function

    return decorator


def with_model_from_db(model_class, fields):
    """
    Decorator factory for PlugIt controllers. Fetches and add to the decorated function parameters a database object
    instance.
    Uses the provided kwargs of the decorated function and the specified fields to build the query filter
    parameters.

    Returns a 404 error if the requested resource was not found.

    :param model_class: SqlAlchemy model class that will be used for the query.
    :param fields: The fields from the decorated function kwargs that will be used in order to perform the query.
    :return: decorated function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            query_kwargs = kwargs_extractor(fields, kwargs)

            entity = model_class.query.filter_by(**query_kwargs).first()
            if entity is None:
                return {
                    'error': '''Resource not found: {id}({class_name})'''
                        .format(id=id, class_name=model_class.__class__.__name__),
                    'status': 404,
                }
            new_args = args + (entity,)
            return f(*new_args, **kwargs)

        return decorated_function

    return decorator


def with_client_identification(f):
    """
    Flask controller decorator. Implements the ETSI TS 103 270 V1.3.1 client identification header validation. Will
    try to find a client identifier in the request's headers and add its corresponding client to the decorated function
    arguments if the request is secure and has the correct header.
    
    :param f: The function to be decorated.
    :return: decorated function.
    """
    @wraps(f)
    def decorator():

        if "Authorization" not in request.headers:
            return f(None)

        if not request.is_secure and not config.DEBUG and not config.STANDALONE:
            return make_response("You must use HTTPS in order to use the client identifier feature.",
                                 401, {"WWW-Authenticate": "ClientIdentifier"})

        identifier = request.headers.get("Authorization")

        if re.compile(r'^ClientIdentifier [a-zA-Z0-9]{16,128}').match(identifier) is None:
            return make_response("Invalid/missing authentication scheme.",
                                 401, {"WWW-Authenticate": "ClientIdentifier"})

        client = Clients.query \
            .filter_by(identifier=identifier.replace('ClientIdentifier ', '')) \
            .first()

        if client is None:
            return make_response("Invalid authentication credentials.", 403)

        return f(client)

    return decorator


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
