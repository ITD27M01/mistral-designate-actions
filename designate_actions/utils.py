from designateclient.v2 import client as designate_client
from keystoneauth1 import loading
from keystoneauth1 import session as ks_session
from keystoneauth1.token_endpoint import Token
from keystoneclient import service_catalog as ks_service_catalog
from keystoneclient.v3 import client as ks_client
from keystoneclient.v3 import endpoints as ks_endpoints
from oslo_config import cfg
from oslo_log import log
import six

from mistral import context
from mistral import exceptions

CONF = cfg.CONF
LOG = log.getLogger(__name__)

def client():
    ctx = context.ctx()
    auth_url = ctx.auth_uri or CONF.keystone_authtoken.www_authenticate_uri

    cl = ks_client.Client(
        user_id=ctx.user_id,
        token=ctx.auth_token,
        tenant_id=ctx.project_id,
        auth_url=auth_url
    )

    cl.management_url = auth_url

    return cl


def _determine_verify(ctx):
    if ctx.insecure:
        return False
    elif ctx.auth_cacert:
        return ctx.auth_cacert
    else:
        return True


def get_session(ctx):
    """Get session and auth parameters.

    :param ctx: action context
    :return: session object for dns service
    """

    if not ctx:
        raise AssertionError('context is mandatory')

    endpoint = get_endpoint(version='v2')

    auth = Token(endpoint=endpoint, token=ctx.auth_token)

    session = ks_session.Session(
        auth=auth,
        verify=_determine_verify(ctx)
    )

    return session


def _admin_client(trust_id=None):
    if CONF.keystone_authtoken.auth_type is None:
        auth_url = CONF.keystone_authtoken.www_authenticate_uri
        project_name = CONF.keystone_authtoken.admin_tenant_name

        # You can't use trust and project together

        if trust_id:
            project_name = None

        cl = ks_client.Client(
            username=CONF.keystone_authtoken.admin_user,
            password=CONF.keystone_authtoken.admin_password,
            project_name=project_name,
            auth_url=auth_url,
            trusts=trust_id
        )

        cl.management_url = auth_url

        return cl
    else:
        kwargs = {}

        if trust_id:
            # Remove domain_id, domain_name, project_name and project_id,
            # since we need a trust scoped auth object
            kwargs['domain_id'] = None
            kwargs['domain_name'] = None
            kwargs['project_name'] = None
            kwargs['project_domain_name'] = None
            kwargs['project_id'] = None
            kwargs['trust_id'] = trust_id

        auth = loading.load_auth_from_conf_options(
            CONF,
            'keystone_authtoken',
            **kwargs
        )
        sess = loading.load_session_from_conf_options(
            CONF,
            'keystone',
            auth=auth
        )

        return ks_client.Client(session=sess)


def client_for_admin():
    return _admin_client()


def get_endpoint(service_name='designate', service_type='dns',
                 region_name=None, version='v2'):
    if service_name is None and service_type is None:
        raise exceptions.MistralException(
            "Either 'service_name' or 'service_type' must be provided."
        )

    ctx = context.ctx()

    service_catalog = obtain_service_catalog(ctx)

    # When region_name is not passed, first get from context as region_name
    # could be passed to rest api in http header ('X-Region-Name'). Otherwise,
    # just get region from mistral configuration.
    region = (region_name or ctx.region_name)
    if service_name == 'keystone':
        # Determining keystone endpoint should be done using
        # keystone_authtoken section as this option is special for keystone.
        region = region or CONF.keystone_authtoken.region_name
    else:
        region = region or CONF.openstack_actions.default_region

    service_endpoints = service_catalog.get_endpoints(
        service_name=service_name,
        service_type=service_type,
        region_name=region
    )

    endpoint = None
    os_actions_endpoint_type = CONF.openstack_actions.os_actions_endpoint_type

    for endpoints in six.itervalues(service_endpoints):
        for ep in endpoints:
            # is V3 interface?
            if 'interface' in ep:
                interface_type = ep['interface']
                if os_actions_endpoint_type in interface_type:
                    endpoint = ks_endpoints.Endpoint(
                        None,
                        ep,
                        loaded=True
                    )
                    break
            # is V2 interface?
            if 'publicURL' in ep:
                endpoint_data = {
                    'url': ep['publicURL'],
                    'region': ep['region']
                }
                endpoint = ks_endpoints.Endpoint(
                    None,
                    endpoint_data,
                    loaded=True
                )
                break

    if not endpoint:
        raise exceptions.MistralException(
            "No endpoints found [service_name=%s, service_type=%s,"
            " region_name=%s]"
            % (service_name, service_type, region)
        )
    else:
        return endpoint.url + version + '/'


def obtain_service_catalog(ctx):
    token = ctx.auth_token

    if ctx.is_trust_scoped and is_token_trust_scoped(token):
        if ctx.trust_id is None:
            raise Exception(
                "'trust_id' must be provided in the admin context."
            )

        # trust_client = client_for_trusts(ctx.trust_id)
        # Using trust client, it can't validate token
        # when cron trigger running because keystone policy
        # don't allow do this. So we need use admin client to
        # get token data
        token_data = _admin_client().tokens.get_token_data(
            token,
            include_catalog=True
        )
        response = token_data['token']
    else:
        response = ctx.service_catalog

        # Target service catalog may not be passed via API.
        # If we don't have the catalog yet, it should be requested.
        if not response:
            response = client().tokens.get_token_data(
                token,
                include_catalog=True
            )['token']

    if not response:
        raise exceptions.UnauthorizedException()

    service_catalog = ks_service_catalog.ServiceCatalog.factory(response)

    return service_catalog


def is_token_trust_scoped(auth_token):
    return 'OS-TRUST:trust' in client_for_admin().tokens.validate(auth_token)


def get_client(ctx, all_projects=False):
    return designate_client.Client(session=get_session(ctx=ctx), all_projects=all_projects)
