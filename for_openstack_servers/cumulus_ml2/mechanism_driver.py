"""  This module contains the ML2 mechanism driver for Cumulus Linux
"""
from oslo.config import cfg
from oslo_log import log as logging
import requests

from neutron.i18n import _LI, _LE
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
        self.url_prefix = 'http'
        self.protocol_port = cfg.CONF.ml2_cumulus.protocol_port

    def agent_list(self, context):
        """ parse through all linux agents. return only those
        that have switch information set. Other linux bridge agents can exist
        like in Rackspace private cloud, linux bridge agent is setup on L3 agent lxc
        container
        Returns:
            list of linux agents with connecting switch information
        """
        _linuxagent_with_switch_info = []
        all_linux_agents = context._plugin.get_agents(
            context._plugin_context,
            filters={'agent_type': [LINUXBRIDGE_AGENT]}
        )
        for _agent in all_linux_agents:
            # try 10 times to get the linux switch from DB. There is a sync
            # issue between linux switch discovery agent and linux bridge agent.
            # When linux bridge agent update DB it overwrites the
            # "configurations" dict. This cause switch info to be deleted. the linux bridge
            # agent needs to not overwrite the configuration dict each time it
            # executes its polling interval. Patch may be in order to address
            # this.
            retries = 10
            while retries > 0:
                if _agent['configurations'].get('switches'):
                    _linuxagent_with_switch_info.append(_agent)
                    retries = 0
                retries -= 1
        if not _linuxagent_with_switch_info:
            LOG.error(_LE('Failed to find linux agent with switch info. Could \
                    be its not configured on compute node or due to sync issue \
                    between linuxbridge agent and linux switch discovery agent'))
            raise MechanismDriverError()

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
        """This sends a Rest call to the Cumulus switch to add the
        switch port to the bridge with same name as the one on the
        openstack server. This adds the same vlan to the trunk to all switches
        listed in the ``switches`` dict.
        Args:
            agent(dict): This has a dict with the switches compute nodes
                        connects to
            context(object): This has information about the vlan id to assign
                        on the switch port
        """
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
                _LI('Sending REST API Call to Switch %s'),
                _request.url
            )
            if _request.status_code != requests.codes.ok:
                LOG.error(
                    _LE("Failed To Provision Switch %s"), _request.text)
                raise MechanismDriverError()

    def _remove_from_switch(self, agent, context):
        """ Removes a port from the bridge with the same name as the one
        on the compute node. If it is the last port in the bridge, it deletes
        the bridge
        Args:
            agent(dict): This has a dict with the switches compute nodes
                        connects to
            context(object): This has information about the vlan id to assign
                        on the switch port

        """
        network_id = context.current['id']
        vlan = context.current['provider:segmentation_id']

        switches = agent['configurations']['switches']
        for _switchname, _switchport in switches.items():
            subiface = '.'.join([_switchport, unicode(vlan)])
            _request = requests.delete(
                BRIDGE_PORT_URL.format(url_prefix=self.url_prefix,
                                       port=self.protocol_port,
                                       switch_name_or_ip=_switchname,
                                       network=network_id,
                                       port_id=subiface)
            )
            LOG.info(
                _LI('Sending REST API Call to Switch %s'),
                _request.url
            )
            if _request.status_code != requests.codes.ok:
                LOG.error(
                    _LE("Failed To Provision Switch %s"), _request.text)
                raise MechanismDriverError()
