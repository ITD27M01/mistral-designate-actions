from mistral_lib import actions
from oslo_log import log

from designate_actions.utils import get_client


LOG = log.getLogger(__name__)


class ZonesList(actions.Action):
    """Action to get zones
    :param dict filters: An optional dict of filters to only show zones
    :param bool all_projects: Allows admins (or users with the right role)
                              to view and edit zones / recordsets for all projects
    :return: A list of zones in project
    """
    def __init__(self, filters=None, all_projects=False):
        self.filters = filters
        self.all_projects = all_projects

    def run(self, context):
        LOG.debug("Running zone_list action")

        designate = get_client(context, self.all_projects)

        LOG.debug("List zones by filters: %s" % self.filters)
        zones = list(designate.zones.list(criterion=self.filters))
        return zones

    def test(self, context):
        LOG.debug("Running zone_list action in dry-run mode")
        return []


class ZoneCreate(actions.Action):
    """Action to get zones
    :param str name: A name for new zone
    :param str email: Email of root for new zone
    :param str ttl: The time to live for cached records
    :param str description: Optional description for zone (can be used as filters for list)
    :param list masters: Mandatory for secondary zones. The servers to slave from to get DNS information
    :param str zone_type: Type of zone. Defaults to PRIMARY
    :param dict attributes: Key:Value pairs of information about this zone
    :param bool all_projects: Allows admins (or users with the right role)
                              to view and edit zones / recordsets for all projects
    :return: A list of zones in project
    """
    def __init__(self, name, email, ttl=None,
                 description=None,
                 masters=None,
                 zone_type=None,
                 attributes=None,
                 all_projects=False):
        self.name = name
        self.email = email
        self.ttl = ttl
        self.description = description
        self.masters = masters
        self.zone_type = zone_type
        self.attributes = attributes
        self.all_projects = all_projects

    def run(self, context):
        LOG.debug("Running zone_create action")

        designate = get_client(context, self.all_projects)

        LOG.debug("Create zone %s" % self.name)
        zone = dict(designate.zones.create(name=self.name,
                                           email=self.email,
                                           ttl=self.ttl,
                                           type_=self.zone_type, masters=self.masters,
                                           attributes=self.attributes, description=self.description))

        return zone

    def test(self, context):
        LOG.debug("Running zone_list action in dry-run mode")
        LOG.debug("Create zone %s" % self.name)
        return {}
