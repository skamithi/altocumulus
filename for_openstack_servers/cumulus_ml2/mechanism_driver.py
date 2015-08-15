"""  This module contains the ML2 mechanism driver for Cumulus Linux
"""
from oslo.config import cfg
from oslo_log import log as logging
import requests

from neutron.extensions import portbindings
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
        self.url_prefix = 'https:'
        self.protocol_port = cfg.CONF.ml2_cumulus.protocol_port

    def bind_port(self, context):
        """ What does this do??
        """
        if context.binding_levels:
            return  # we've already got a top binding

        # assign a dynamic vlan
        next_segment = context.allocate_dynamic_segment(
            {'id': context.network.current, 'network_type': 'vlan'}
        )

        context.continue_binding(
            context.segments_to_bind[0]['id'],
            [next_segment]
        )

    @property
    def agent_list(self, context):
        """ parse through all linux agents. return only those
        that have switch information set. Other linux bridge agents can exist
        like in Rackspace private cloud, linux bridge agent is setup on L3 agent lxc
        container
        Returns:
            list of linux agents with connecting switch information
        """
        _linuxagent_with_switch_info = []
        all_linux_agents = context.host_agents(LINUXBRIDGE_AGENT)
        for _agent in all_linux_agents:
            if _agent['configurations'].get('switches'):
                _linuxagent_with_switch_info.append(_agent)

        return _linuxagent_with_switch_info

    def create_network_postcommit(self, context):
        """action to take on cumulus switch after a network is added to neutron
        create bridge from cumulus, if necessary and add the switch port connecting
        to the agent (compute node) to the bridge.
        """
        if context.segments_to_bind:
            agents = self.agent_list(context)
            for _agent in agents:
                self._add_to_switch(_agent, context)

    def delete_network_postcommit(self, context):
        """action to take on cumulus switch after a network is deleted from neutron
        delete the bridge from cumulus
        """
        if context.segments_to_bind:
            agents = self.agent_list(context)
            for _agent in agents:
                self._remove_from_switch(_agent, context)

    def _add_to_switch(self, agent, context):
        port = context.current
        device_id = port['device_id']
        device_owner = port['device_owner']
        host = port[portbindings.HOST_ID]
        network_id = port['network_id']
        vlan = context.bottom_bound_segment['segmentation_id']

        if not (host and device_id and device_owner):
            LOG.info(
                _LI('host: %s device_id: %s device_owner %s. One is blank'),
                host, device_id, device_owner)
            return

        switches = agent['configurations']['switches']
        for _switchname, _switchport in switches.items():
            subiface = '.'.join([_switchport, vlan])
            _request = requests.put(
                BRIDGE_PORT_URL.format(url_prefix=self.url_prefix,
                                       switch_name_or_ip=_switchname,
                                       network=network_id,
                                       port_id=subiface)
            )
            LOG.info(
                _LI('Sending the following api call to switch %s'),
                _request
            )
            if _request.status_code != requests.codes.ok:
                raise MechanismDriverError()

    def _remove_from_switch(self, context):
        port = context.current
        device_id = port['device_id']
        device_owner = port['device_owner']
        host = port[portbindings.HOST_ID]
        network_id = port['network_id']
        vlan = context.bottom_bound_segment['segmentation_id']

        LOG.info(
            _LI('In _remove_from_switch')
        )
