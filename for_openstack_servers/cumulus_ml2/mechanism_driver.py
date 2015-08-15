"""  This module contains the ML2 mechanism driver for Cumulus Linux
"""
from oslo.config import cfg
from oslo_log import log as logging
import requests

from neutron.i18n import _LI
from neutron.plugins.ml2.common.exceptions import MechanismDriverError
from neutron.plugins.ml2.driver_api import MechanismDriver

LOG = logging.getLogger(__name__)
BRIDGE_PORT_URL = '{url_prefix}://{switch_name_or_ip}:{port}/networks/{network}/{port_id}'
LINUXBRIDGE_AGENT = 'Linux bridge agent'


CONFIG = [
    cfg.StrOpt('protocol_port', default='8140',
               help=_('port to send API request to cumulus switch'))
]

cfg.CONF.register_opts(CONFIG, "ml2_cumulus")


class CumulusMechanismDriver(MechanismDriver):

    """Mechanism driver for Cumulus Linux that manages connectivity between switches
    and (compute) hosts using the Altocumulus API
    Inspired by the Arista ML2 mechanism driver
    """

    def initialize(self):
        self.url_prefix = 'https'
        self.protocol_port = cfg.CONF.ml2_cumulus.protocol_port

    def agent_list(self, context):
        """ parse through all linux agents. return only those
        that have switch information set. Other linux bridge agents can exist
        like in Rackspace private cloud, linux bridge agent is setup on L3 agent lxc
        container
        Returns:
            list of linux agents with connecting switch information
        """
        LOG.info(_LI('context dict %s'), context.__dict__)  # DELETE
        LOG.info(_LI('context current %s'), context.current)  # DELETE
        _linuxagent_with_switch_info = []
        all_linux_agents = context._plugin.get_agents(
            context._plugin_context,
            filters={'agent_type': [LINUXBRIDGE_AGENT]}
        )
        for _agent in all_linux_agents:
            if _agent['configurations'].get('switches'):
                _linuxagent_with_switch_info.append(_agent)

        return _linuxagent_with_switch_info

    def create_network_postcommit(self, context):
        """action to take on cumulus switch after a network is added to neutron
        create bridge from cumulus, if necessary and add the switch port connecting
        to the agent (compute node) to the bridge.
        """
        agents = self.agent_list(context)
        for _agent in agents:
            self._add_to_switch(_agent, context)

    def delete_network_postcommit(self, context):
        """action to take on cumulus switch after a network is deleted from neutron
        delete the bridge from cumulus
        """
        agents = self.agent_list(context)
        for _agent in agents:
            self._remove_from_switch(_agent, context)

    def _add_to_switch(self, agent, context):
        network_id = context.current['id']
        vlan = context.current['provider:segmentation_id']

        switches = agent['configurations']['switches']
        for _switchname, _switchport in switches.items():
            subiface = '.'.join([_switchport, unicode(vlan)])
            _request = requests.put(
                BRIDGE_PORT_URL.format(url_prefix=self.url_prefix,
                                       port=self.protocol_port,
                                       switch_name_or_ip=_switchname,
                                       network=network_id,
                                       port_id=subiface)
            )
            LOG.info(
                _LI('Sending the following api call to switch %s'),
                _request.__dict__
            )
            if _request.status_code != requests.codes.ok:
                raise MechanismDriverError()

    def _remove_from_switch(self, agent, context):
        LOG.info(
            _LI('In _remove_from_switch')
        )
