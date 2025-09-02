from flask import current_app
from flask import request, g
from flask_login import current_user
from flask_principal import RoleNeed

from invenio_requests.proxies import current_requests_service
from invenio_access.permissions import system_identity

from invenio_requests.views.decorators import pass_request
from invenio_records_resources.proxies import current_service_registry

from pprint import pprint


def has_admin_permissions():
    return RoleNeed('admin') in g.identity.provides

def is_record_owner(record_user_id):
    return record_user_id == g.identity.id

def has_permissions(record_user_id):
    return is_record_owner(record_user_id) or has_admin_permissions()

@pass_request(expand=True)
def  get_expanded_data(request_pid_value, **kwargs):

    request_data = kwargs['request']

    expanded_request = request_data.to_dict()

    return expanded_request


def get_comments_data_for_record_id(record_id):

    search_params = { "q": f"topic.record:{record_id} AND is_closed:true" }
    result = current_requests_service.search(
                          identity=system_identity,
                          params=search_params
                         )
    requests =  result.to_dict()['hits']
    return requests


def get_record_id_of_first_version(record_id):

    rdm_record_service = current_service_registry.get("records")
    versions = rdm_record_service.search_versions(system_identity, record_id)
    versions_dict  =  versions.to_dict()['hits']['hits']

    first_version =  None
    for version in versions_dict:
        if version['versions']['index'] ==  1:
            first_version =  version
            break

    if first_version:
        return first_version['id']
    else:
        return None


def get_comments_data(record_id, community_slug=None):

    if not current_user.is_authenticated:
        return None

    if not community_slug:
        return None

    disabled =  current_app.config.get("COMMUNITY_CONVERSATION_DISABLED", [])
    if community_slug in disabled:
        return None

    check_permission = False

    requests = get_comments_data_for_record_id(record_id)
    if requests['total'] ==  0:
        first_version_id = get_record_id_of_first_version(record_id)
        if first_version_id is None:
            return None
        else:
           current_app.logger.info(f"FIRST VERSION OF RECORD:  ID: {first_version_id}")
           requests = get_comments_data_for_record_id(first_version_id)

    if requests['total'] > 0:
        record_user_id = requests['hits'][0]['created_by']['user']
        if (not check_permission) or has_permissions(record_user_id):
            request_id = requests['hits'][0]['id']
            expanded_data  = get_expanded_data(request_pid_value=request_id)
            return {'request': expanded_data }
        else:
            return None
    else:
        return None


def register_filters(app):
    app.jinja_env.filters['comments_data'] = get_comments_data
