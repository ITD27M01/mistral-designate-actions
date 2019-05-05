from designateclient.v2 import client
from keystoneauth1 import session
from keystoneauth1.token_endpoint import Token
from keystoneclient import service_catalog as ks_service_catalog
from oslo_log import log


LOG = log.getLogger(__name__)


def obtain_service_catalog(context):
    service_catalog = ks_service_catalog.ServiceCatalog.factory(context.service_catalog)

    return service_catalog


def get_endpoint(context, version='v2'):
    catalog = obtain_service_catalog(context)

    endpoint = catalog.url_for(service_type='dns',
                               service_name='designate')

    endpoint = endpoint + version + '/'

    return endpoint


def get_session(context):
    if not context:
        raise AssertionError('context is mandatory')

    auth = Token(endpoint=get_endpoint(context),
                 token=context.security.auth_token)

    return session.Session(auth=auth)


def get_client(context):
    return client.Client(session=get_session(context))
