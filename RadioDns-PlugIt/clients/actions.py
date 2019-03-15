# -*- coding: utf-8 -*-

# Utils
import re

from plugit.utils import action, only_orga_member_user, json_only
from sqlalchemy.exc import IntegrityError

from actions_utils import get_orga_service_provider, with_json_validated_and_decoded, error_boundary, with_model_from_db
from db_utils import db
from models import Clients

# Json validation schema of a client creation / update.
client_schema = {
    'name': {
        'type': 'string',
        'minLength': 1,
        'maxLength': 255
    },
    'email': {
        'type': 'string',
        'minLength': 1,
        'maxLength': 255,
        'pattern': '^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$'
    },
    'identifier': {
        'type': 'string',
        'pattern': '^[a-zA-Z0-9]{16,128}$'
    },
}


def client_or_identifier_already_exists_handler(e):
    """
    Callback for the error_boundary decorator. Handles the exception catched by the boundary.
    :param e: The received exception.
    :return: {error: string, status: number}
    """
    result = re.compile('.*(?P<name>\'.*\').*(?P<type>\'.*\')').search(e.message)
    if result.groupdict()['type'] == '\'clients_name_uindex\'':
        type = "name"
    else:
        type = "identifier"
    return {
        'error': """A client with this {type} already exists.""".format(type=type),
        'status': 409,
    }


@action(route="/clients/", template="clients/home.html", methods=['GET'])
@only_orga_member_user()
def client_home(request):
    """
    Return the view of the "shell" of the clients module.

    :param request: The flask request.
    :return: The home view for the clients.
    """

    orga, sp = get_orga_service_provider(request)

    return {
        'ebu_codops': orga.codops,
        'serviceprovider': sp.json if sp else None
    }


@action(route="/clients/list", methods=['GET'])
@json_only()
@only_orga_member_user()
def client_list(request):
    """
    REST Endpoint that returns a json representation of the clients.
    :param request: The flask request.
    :return: json object with the clients.
    """

    orga = int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))
    return {
        'clients': map(lambda client: client.json, Clients.query.filter_by(orga=orga).all())
    }


@action(route="/clients/add", methods=['POST'])
@only_orga_member_user()
@json_only()
@with_json_validated_and_decoded(client_schema)
@error_boundary(IntegrityError, client_or_identifier_already_exists_handler)
def client_create(request, decoded):
    """
    REST endpoint to create a client.

    :param request: The flask request.
    :param decoded: The decoded json value from the with_json decorator.
    :return: json of the newly created client.
    """
    orga = int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    client = Clients()
    client.orga = orga
    client.email = decoded['email']
    client.name = decoded['name']
    client.identifier = decoded['identifier']

    db.session.add(client)
    db.session.commit()
    return {'client': client.json}


@action(route="/clients/delete/<id>", methods=['DELETE'])
@only_orga_member_user()
@json_only()
@with_model_from_db(Clients, ['id'])
def client_delete(_, client, id):
    """
    REST endpoint to delete a client.

    :param _: [UNUSED] the flask request.
    :param client: the client returned from the with_model_from_db decorator.
    :param id: the id of the client.
    :return: json with the id of the deleted client.
    """
    db.session.delete(client)
    db.session.commit()
    return {'id': int(id)}


@action(route="/clients/patch/<id>", methods=['POST'])
@only_orga_member_user()
@json_only()
@with_json_validated_and_decoded(client_schema)
@with_model_from_db(Clients, ['id'])
@error_boundary(IntegrityError, client_or_identifier_already_exists_handler)
def client_update(request, decoded, client, id):
    """
    REST endpoint to update a client.

    :param request: The flask request.
    :param decoded: The decoded json value from the with_json decorator.
    :param client: the client returned from the with_model_from_db decorator.
    :param id: the id of the client.
    :return: json of the updated client.
    """
    client.email = decoded['email']
    client.name = decoded['name']
    client.identifier = decoded['identifier']

    db.session.commit()

    return {'client': client.json}
