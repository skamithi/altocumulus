"""linux agent switch discovery

This modules takes static remote switch configuration listed in
/etc/neutron/ml2/ml2_conf.ini

This driver is executed on the compute node running a linux bridge agent.

switch discovery in the ``ml2_conf.ini`` has 1 option.

``switch_name:port_id``: its a list of switch names and port ids
that the compute node is connected to.

Example:

    [linux_agent_switch_discovery]
    switches=['10.1.1.1:bond0']

and copies it into the linux agent ``configuration`` hash

   $ neutron net-show [ID]
   [OUTPUT]

In the ``etc`` directory of this project, there are examples
of how to execute this agent using systemd, upstart and SysV(/etc/init.d)

"""
import sys

from oslo_config import cfg
from oslo_log import log as logging
from neutron.common import utils as neutron_utils
from neutron.common import config as common_config
from neutron.i18n import _LI
from neutron.plugins.linuxbridge.agent import linuxbridge_neutron_agent as lna


LOG = logging.getLogger(__name__)


CONFIG = [
    cfg.ListOpt('switches', default=[],
                help=_('list of switch name/ip and remote switch port connected to this compute node'))
]

cfg.CONF.register_opts(CONFIG, "linux_agent_switch_discovery")


class LinuxBridgeSwitchDiscoveryNeutronAgentRPC(lna.LinuxBridgeNeutronAgentRPC):
    def __init__(self, interface_mapping, polling_interval):
        """ read the ml2 config and add each remote switch details to the neutron DB"""
        super(LinuxBridgeSwitchDiscoveryNeutronAgentRPC, self).__init__(
            interface_mapping,
            polling_interval
        )

        switches = cfg.CONF.linux_agent_switch_discovery.switches
        # reset switches entry in the linux bridge DB
        self.agent_state['configurations']['switches'] = {}
        for _switch in switches:
            switchlist = self.agent_state['configurations']['switches']
            (_switchname, _remoteport) = _switch.split(':')
            switchlist[_switchname] = _remoteport
            LOG.info(_LI('Linux Bridge Switch Discovery adding %s : %s to Neutron L2 Agent DB'),
                     _switchname, _remoteport)


def main():
    """ used by console-scripts helper to generate a script that is executed using
    SysV, systemd or upstart
    """
    common_config.init(sys.argv[1:])
    common_config.setup_logging()
    polling_interval = cfg.CONF.AGENT.polling_interval
    interface_mappings = neutron_utils.parse_mappings(
        cfg.CONF.LINUX_BRIDGE.physical_interface_mappings)
    agent = LinuxBridgeSwitchDiscoveryNeutronAgentRPC(interface_mappings,
                                                      polling_interval)
    LOG.info(_LI("Agent initialized successfully, now running... "))
    agent.daemon_loop()
    sys.exit(0)
