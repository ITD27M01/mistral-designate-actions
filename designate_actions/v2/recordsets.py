from mistral_lib import actions
from designateclient.v2 import client
from oslo_log import log

from designate_actions import utils


LOG = log.getLogger(__name__)


class RecordsetsList(actions.Action):
    """Action to get recordsets from zone

    :param str zone: The name or id of zone to list recordsets
    :param dict filters: An optional dict of filters to only list recordsets
    :return: A list of recordsets in zone
    """
    def __init__(self, zone, filters=None):
        self.zone = zone
        self.filters = filters

    def run(self, context):
        LOG.debug("Running recordsets_list action")
        session = utils.get_session(context)
        designate = client.Client(
            session=session
        )

        LOG.debug("List recordsets in zone {} by filters: {}".format(self.zone, self.filters))
        recordsets = designate.recordsets.list(zone=self.zone, criterion=self.filters)

        return list(recordsets)

    def test(self, context):
        return []


class RecordsetCreate(actions.Action):
    """Action to create the recordset

    :param str zone: The name or id of zone to create recordset
    :param list records: The list data of recordset to create
    :param str name: The name of recordset to create
    :param str rrtype: The type of recordset to create. The default is A resource record type
    :param str description: Optional string described the created recordset
    :return: A new recordset dict object
    """
    def __init__(self, zone, name, records, rrtype='A', description=None):
        self.zone = zone
        self.name = name
        self.records = records
        self.rrtype = rrtype
        self.description = description

    def run(self, context):
        LOG.debug("Running recordset_create action")
        session = utils.get_session(context)
        designate = client.Client(
            session=session
        )

        LOG.debug("Create recordset {} in zone {} with data {} and type {}".format(self.name,
                                                                                   self.zone,
                                                                                   self.records,
                                                                                   self.rrtype))
        recordset = designate.recordsets.create(zone=self.zone,
                                                name=self.name,
                                                records=self.records,
                                                type_=self.rrtype,
                                                description=self.description)

        return dict(recordset)

    def test(self, context):
        return {}


class RecordsetDelete(actions.Action):
    """Action to delete the recordset

    :param str zone: The name or id of zone to delete recordset
    :param str recordset: The name or id of recordset to delete
    :return: Deleted recordset dict object
    """
    def __init__(self, zone, recordset):
        self.zone = zone
        self.recordset = recordset

    def run(self, context):
        LOG.debug("Running recordset_delete action")
        session = utils.get_session(context)
        designate = client.Client(
            session=session
        )

        LOG.debug("Delete recordset {} from zone {}".format(self.recordset, self.zone))
        recordset = designate.recordsets.delete(zone=self.zone,
                                                recordset=self.recordset)

        return dict(recordset)

    def test(self, context):
        return {}


class RecordsetUpdate(actions.Action):
    """Action for update the recordset

    :param str recordset: The name of recordset to update
    :param str zone: The name or id of zone to create update
    :param dict values: The dict data of recordset to update (records, ttl, etc...)
    :return: Updated recordset dict object
    """
    def __init__(self, zone, recordset, values):
        self.zone = zone
        self.recordset = recordset
        self.values = values

    def run(self, context):
        LOG.debug("Running recordset_update action")
        session = utils.get_session(context)
        designate = client.Client(
            session=session
        )

        LOG.debug("Update recordset {} in zone {} with new data: {}".format(self.recordset,
                                                                            self.zone, self.values))

        recordset = designate.recordsets.update(zone=self.zone,
                                                recordset=self.recordset,
                                                values=self.values)
        return dict(recordset)

    def test(self, context):
        return {}
