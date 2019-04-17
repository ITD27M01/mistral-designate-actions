from jmespath import search
from designateclient.v2 import client
from keystoneauth1 import session
from keystoneauth1.token_endpoint import Token
from oslo_log import log


LOG = log.getLogger(__name__)


def get_endpoint(context, version='v2'):
    catalog = context.security.service_catalog['catalog']

    endpoints = search('[?type == `dns`].endpoints[]', catalog)
    endpoint = search('[?interface == `public`].url', endpoints)[0]

    endpoint = endpoint + version + '/'

    return endpoint


def get_session(context):
    if not context:
        raise AssertionError('context is mandatory')

    auth = Token(endpoint=get_endpoint(context),
                 token=context.security.auth_token)

    return session.Session(auth=auth)


def get_client(context):
    designate_client = client.Client(
            session=get_session(context)
    )

    return designate_client
