from mistral_lib import actions
from designateclient.v2 import client
from oslo_log import log

from designatev2_actions import utils


LOG = log.getLogger(__name__)


class ZoneList(actions.Action):
    """Action to get zones

    :param dict filters: An optional dict of filters to only show zones
    """
    def __init__(self, filters):
        self.filters = filters or None

    def run(self, context):
        # return your results here
        session = utils.get_session(context)
        designate = client.Client(
            session=session
        )

        zones = designate.zones.list(criterion=self.filters)

        return {'zones': zones}

    def test(self, context):
        return {'zones': []}
