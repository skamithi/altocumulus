"""  This module contains the ML2 mechanism driver for Cumulus Linux
"""
from oslo.config import cfg
from oslo_log import log as logging
import requests
from requests.exceptions import ConnectionError

from neutron.i18n import _LI, _LE
from neutron.plugins.ml2.common.exceptions import MechanismDriverError
from neutron.plugins.ml2.driver_api import MechanismDriver

LOG = logging.getLogger(__name__)
BRIDGE_PORT_URL = '{url_prefix}://{switch_name_or_ip}:{port}/networks/{network_id}/{vlan}/{port_id}'
LINUXBRIDGE_AGENT = 'Linux bridge agent'

"""
Example for non vlan aware mode.
host lists are separated by commas
port listings are separated using semicolons
192.168.20.20 lists 2 ports "bond0" and "peerlink"
192.168.20.19 lists "bond0" and "peerlink".


    [ml2_cumulus]
    switches = 192.168.20.20:bond0;bond1;bond2;peerlink

Example for vlan aware mode. only mention the link that connects to the compute nodes
it can be added as a list of ports.
    [ml2_cumulus]
    switches = 192.168.20.20:bond0;bond1;bond2

[TODO]
Would be nice to just do  "switches = 192.168.20.20:bond0-10".
the code to manage this exists in
netshow-lib..but for now will just leave it like this for quick testing.
I can now see the value of a dynamic lldp solution from the switch side.
But again, need to get lldp working with Redhat consistently
and document this cause redhat site doesn't help at all.
also if it continues causes crashes on PTM, get ptm fixed
to prevent further issues.
"""

CONFIG = [
    cfg.StrOpt('protocol_port', default='8140',
               help=_('port to send API request to cumulus switch')),
    cfg.ListOpt('switches', default=[],
                help=_('list of switch name/ip and remote switch port connected to this compute node'))

]

cfg.CONF.register_opts(CONFIG, "ml2_cumulus")


class CumulusMechanismDriver(MechanismDriver):

    """Mechanism driver for Cumulus Linux that manages connectivity between switches
    and (compute) hosts using the Altocumulus API
    Inspired by the Arista ML2 mechanism driver
    """

    def initialize(self):
        # right now for early dev, using http
        self.url_prefix = 'http'
        self.protocol_port = cfg.CONF.ml2_cumulus.protocol_port
        self.switches = self.process_switch_config(cfg.CONF.ml2_cumulus.switches)
        if self.switches:
            LOG.info(_LI('switches found in ml2_conf files %s'), self.switches)
        else:
            LOG.info(_LI('no switches in ml2_conf files'))

    def process_switch_config(self, switch_list):
        """ take the ini switch list config and convert it to a dict that looks
        like this

          { '192.168.20.20': ['bond0', 'peerlink'],
            'sw25': ['bond0', 'peerlink'] }
        Args:
            switch_list(string): String from ml2_conf.ini config that has list
            of switches and ports that need to be dynamically provisioned
        Returns:
            array of switches, each switch has contains a name and port list
        """
        final_switch_list = []
        for _switchentry in switch_list:
            _switcharr = _switchentry.split(':')
            if len(_switcharr) == 2:
                _ports = _switcharr[1]
                _ports = _ports.split(';')
            else:
                _ports = ['none']
            _hostname = _switcharr[0]
            final_switch_list.append({'name': _hostname,
                                      "ports": _ports})
        return final_switch_list

    def create_network_postcommit(self, context):
        """action to take on cumulus switch after a network is added to neutron
        create bridge from cumulus, if necessary and add the switch port connecting
        to the agent (compute node) to the bridge.
        """
        for _switch in self.switches:
            self._add_to_switch(_switch, context)

    def delete_network_postcommit(self, context):
        """action to take on cumulus switch after a network is deleted from neutron
        delete the bridge from cumulus
        """
        for _switch in self.switches:
            self._remove_from_switch(_switch, context)

    def _add_to_switch(self, _switch, context):
        """ Send REST PUT call to cumulus switch to add a vlan
        [TODO] Send https call with  some kind of authentication
        """
        _network = context.current['id']
        _vlanid = context.current['provider:segmentation_id']

        # BRIDGE_PORT_URL = '{url_prefix}://{switch_name_or_ip}:{port}/networks/{vlan}/{network_id}/{port_id}'
        for _switchport in _switch.get('ports'):
            try:
                _request = requests.put(
                    BRIDGE_PORT_URL.format(url_prefix=self.url_prefix,
                                           port=self.protocol_port,
                                           switch_name_or_ip=_switch.get('name'),
                                           vlan=unicode(_vlanid),
                                           network_id=_network,
                                           port_id=_switchport)
                )
                LOG.info(
                    _LI('Sending PUT API Call to Switch %s'),
                    _request.url
                )
                if _request.status_code != requests.codes.ok:
                    LOG.error(
                        _LE("Failed To Provision Switch %s"), _request.text)
                    raise MechanismDriverError()
            except ConnectionError:
                LOG.error(
                    _LE('Failed to connect to switch %s'),
                    _request.url
                )

    def _remove_from_switch(self, _switch, context):
        """Send REST DELETE call to Cumulus switch to delete a vlan
        [TODO] send https call with some kind of authentication
        """
        _network = context.current['id']
        _vlanid = context.current['provider:segmentation_id']

        # BRIDGE_PORT_URL = '{url_prefix}://{switch_name_or_ip}:{port}/networks/{vlan}/{network_id}/{port_id}'
        for _switchport in _switch.get('ports'):
            _request = requests.delete(
                BRIDGE_PORT_URL.format(url_prefix=self.url_prefix,
                                       port=self.protocol_port,
                                       switch_name_or_ip=_switch.get('name'),
                                       vlanid=unicode(_vlanid),
                                       _network_id=_network,
                                       port_id=_switchport)
            )
            LOG.info(
                _LI('Sending DELETE API Call to Switch %s'),
                _request.url
            )
            if _request.status_code != requests.codes.ok:
                LOG.error(
                    _LE("Failed To Provision Switch %s"), _request.text)
                raise MechanismDriverError()
