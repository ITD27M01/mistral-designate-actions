from mistral_lib import actions
from oslo_log import log

from designate_actions.utils import get_client


LOG = log.getLogger(__name__)


class RecordsetsList(actions.Action):
    """Action to get recordsets from zone

    :param str zone: The name or id of zone to list recordsets
    :param dict filters: An optional dict of filters to only list recordsets
    :param bool all_projects: Allows admins (or users with the right role)
                              to view and edit zones / recordsets for all projects
    :return: A list of recordsets in zone
    """
    def __init__(self, zone, filters=None, all_projects=False):
        self.zone = zone
        self.filters = filters
        self.all_projects = all_projects

    def run(self, context):
        LOG.debug("Running recordsets_list action")
        designate = get_client(context, self.all_projects)

        LOG.debug("List recordsets in zone {} by filters: {}".format(self.zone, self.filters))
        recordsets = list(designate.recordsets.list(zone=self.zone, criterion=self.filters))

        return recordsets

    def test(self, context):
        return []


class RecordsetCreate(actions.Action):
    """Action to create the recordset

    :param str zone: The name or id of zone to create recordset
    :param list records: The list data of recordset to create
    :param str name: The name of recordset to create
    :param str rrtype: The type of recordset to create. The default is A resource record type
    :param str description: Optional string described the created recordset
    :param bool all_projects: Allows admins (or users with the right role)
                              to view and edit zones / recordsets for all projects
    :return: A new recordset dict object
    """
    def __init__(self, zone, name, records, rrtype='A', description=None, all_projects=False):
        self.zone = zone
        self.name = name
        self.records = records
        self.rrtype = rrtype
        self.description = str(description)
        self.all_projects = all_projects

    def run(self, context):
        LOG.debug("Running recordset_create action")
        designate = get_client(context, self.all_projects)

        LOG.debug("Create recordset {} in zone {} with data {} and type {}".format(self.name,
                                                                                   self.zone,
                                                                                   self.records,
                                                                                   self.rrtype))
        recordset = dict(designate.recordsets.create(zone=self.zone,
                                                     name=self.name,
                                                     records=self.records,
                                                     type_=self.rrtype,
                                                     description=self.description))

        return recordset

    def test(self, context):
        return {}


class RecordsetDelete(actions.Action):
    """Action to delete the recordset

    :param str zone: The name or id of zone to delete recordset
    :param str recordset: The name or id of recordset to delete
    :param bool all_projects: Allows admins (or users with the right role)
                              to view and edit zones / recordsets for all projects
    :return: Deleted recordset dict object
    """
    def __init__(self, zone, recordset, all_projects=False):
        self.zone = zone
        self.recordset = recordset
        self.all_projects = all_projects

    def run(self, context):
        LOG.debug("Running recordset_delete action")
        designate = get_client(context, self.all_projects)

        LOG.debug("Delete recordset {} from zone {}".format(self.recordset, self.zone))
        recordset = dict(designate.recordsets.delete(zone=self.zone,
                                                     recordset=self.recordset))

        return recordset

    def test(self, context):
        return {}


class RecordsetUpdate(actions.Action):
    """Action for update the recordset

    :param str recordset: The name of recordset to update
    :param str zone: The name or id of zone to create update
    :param dict values: The dict data of recordset to update (records, ttl, etc...)
    :param bool all_projects: Allows admins (or users with the right role)
                              to view and edit zones / recordsets for all projects
    :return: Updated recordset dict object
    """
    def __init__(self, zone, recordset, values, all_projects=False):
        self.zone = zone
        self.recordset = recordset
        self.values = values
        self.all_projects = all_projects

    def run(self, context):
        LOG.debug("Running recordset_update action")
        designate = get_client(context, self.all_projects)

        LOG.debug("Update recordset {} in zone {} with new data: {}".format(self.recordset,
                                                                            self.zone, self.values))

        if 'description' in self.values.keys():
            self.values['description'] = str(self.values['description'])

        recordset = dict(designate.recordsets.update(zone=self.zone,
                                                     recordset=self.recordset,
                                                     values=self.values))
        return recordset

    def test(self, context):
        return {}
