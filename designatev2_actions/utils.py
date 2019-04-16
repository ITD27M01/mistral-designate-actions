from jmespath import search
from keystoneauth1 import session
from keystoneauth1.token_endpoint import Token
from oslo_log import log


LOG = log.getLogger(__name__)


def get_session(context):
    """Get designate session
    :param context: action context
    :return: session object
    """

    if not context:
        raise AssertionError('context is mandatory')

    catalog = context.security.service_catalog['catalog']
    auth_token = context.security.auth_token

    endpoints = search('[?type == `dns`].endpoints[]', catalog)
    endpoint = search('[?interface == `public`].url', endpoints)[0]

    endpoint = endpoint + 'v2/'
    auth = Token(endpoint=endpoint,
                 token=auth_token)

    return session.Session(auth=auth)

