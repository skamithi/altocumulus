from netshowlib import netshowlib
from netshowlib.linux.common import create_range, group_ports
import pkg_resources
import os
import ansible.runner as ansible_runner
import ansible.inventory as ansible_inventory


def get_vlan_aware_bridge():
    """ checks if Cumulus switch has vlan aware bridge
    Returns:
        True if vlan aware bridge is present
    """


def update_config_via_ansible(modname, modargs_str):
    """ update config via cumulus ansible modules using ansible command line options
    not ansible-playbook options. If a change occurs, it will call the reload_config()
    function
    Args:
        modname(str): name of the ansible module to clal
        modargs_str(str): module arguments
    Returns:
        an error message is something goes wrong.
    """
    install_location = pkg_resources.require('cumulus-ml2-service')[0].location
    _library = os.path.join(install_location,
                            '..', '..', '..',
                            'ansible_modules', 'library')
    inv = ansible_inventory.Inventory(['localhost'])
    results = ansible_runner.Runner(
        module_name=modname,
        module_path=_library,
        become=True,
        transport='local',
        module_args=modargs_str, inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']
    itmayhaveworked = results.get('contacted')
    if itmayhaveworked.get('localhost') and \
            itmayhaveworked.get('localhost').get('failed'):
        return itmayhaveworked['localhost']['msg']
    # if the change actually occurred reload the config
    if itmayhaveworked['localhost'].get('changed'):
        return reload_config()


def reload_config():
    """ run ifreload -a to push the changes into the persistent config
    Returns:
        an error message if something goes wrong
    """
    inv = ansible_inventory.Inventory(['localhost'])
    results = ansible_runner.Runner(
        module_name='shell',
        become=True,
        transport='local',
        module_args="/sbin/ifreload -a", inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']


class CumulusML2Ansible(object):
    def __init__(self, bridgename, vlan_id, port_id, delete_vlan):
        self.port = port_id
        self.bridgename = bridgename
        self.vlan = vlan_id
        self._vlan_aware_bridge = None
        self._bridge_ports = None
        self.port_vids = None
        self.bridge_vids = None
        self.delete_vlan = delete_vlan

    @property
    def vlan_aware_bridge(self):
        if self._vlan_aware_bridge:
            return self._vlan_aware_bridge

        portlist = netshowlib.portname_list()
        for _portname in portlist:
            _iface = netshowlib.iface(_portname)
            if hasattr(_iface, 'vlan_filtering') and \
                    _iface.vlan_filtering and \
                    _iface.is_bridge():
                self._vlan_aware_bridge = _iface

        return self._vlan_aware_bridge

    @property
    def bridge_ports(self):
        if self._bridge_ports:
            return self._bridge_ports
        if not self.vlan_aware_bridge:
            return None
        self._bridge_ports = sorted(self.vlan_aware_bridge.members.keys())
        return self._bridge_ports

    def update_port_vlan_list(self):
        """ removes or adds vlans to the vlan aware bridge member vlans
        """
        port_vlan_list = netshowlib.iface(self.port).vlan_list
        if self.delete_vlan:
            port_vlan_list.remove(self.vlan)
        else:
            port_vlan_list.append(self.vlan)
        self.port_vids = create_range('', set(port_vlan_list))

    def update_bridge_vlan_list(self):
        """ removes or adds vlans to the vlan aware bridge list
        """
        vlan_list = []
        bridgemems = self.vlan_aware_bridge.members.values()
        for _member in bridgemems:
            vlan_list += (_member.vlan_list)

        if self.delete_vlan:
            vlan_list.remove(self.vlan)
        else:
            vlan_list.append(self.vlan)

        self.bridge_vids = create_range('', set(vlan_list))

    def in_vlan_aware_mode(self):
        """ check if switch is in vlan aware mode
        Returns:
            True if in vlan aware mode
        """
        if self.vlan_aware_bridge:
            return True
        return False

    def update_bridge_classic_mode(self):
        pass

    def update_vlan_aware_port_config(self):
        """ runs function to add/remove vlan from port vlan list then sends
        appropriate module and module arguments to ansible to make the config change
        """
        self.update_port_vlan_list()
        modname = 'cl_interface'
        modargs_str = 'name=%s vids=%s mstpctl_bpduguard=yes' % (self.port, ','.join(self.port_vids))
        return update_config_via_ansible(modname, modargs_str)

    def update_vlan_aware_bridge_config(self):
        """ runs function to add/remove vlan from bridge vlan list then
        sends appropriate module and module arguments to ansible to make the
        config change
        """
        self.update_bridge_vlan_list()
        modname = 'cl_bridge'
        modargs_str = 'name=%s ports=%s vids=%s' % (
            self.vlan_aware_bridge.name,
            ','.join(group_ports(self.bridge_ports)),
            ','.join(self.bridge_vids))
        return update_config_via_ansible(modname, modargs_str)

    def add_to_bridge_vlan_aware(self):
        """ add vlan to bridge in vlan aware mode. adds vlan to port found plus
        global bridge so that uplink ports gets the same config
        Returns:
            error string if failed
        """
        errmsg = self.update_vlan_aware_port_config()
        if errmsg:
            return errmsg

        errmsg = self.update_vlan_aware_bridge_config()
        if errmsg:
            return errmsg

    def delete_from_bridge_vlan_aware(self):
        """ delete vlan from vlan aware bridge port. do not delete on interswitch links
        deleting the vlan from the interswitch link may cause failures.
        Returns:
            error string if failed
        """
        errmsg = self.update_vlan_aware_port_config()
        if errmsg:
            return errmsg

    def add_to_bridge_classic_mode(self):
        """ add or create bridge with port in classic mode.
        """
        pass

    def add_to_bridge(self):
        """ generic function to add a vlan(and/or) port to a bridge. checks if switch is running
        in vlan aware mode or classic mode and adds to the appropriate bridge and/or port.
        """
        if self.in_vlan_aware_mode():
            return self.add_to_bridge_vlan_aware()
        else:
            return self.add_to_bridge_classic_mode()

    def delete_from_bridge(self):
        """ generic function to remove a vlan(and/or) port from  a bridge. checks if switch
        is running in vlan aware mode or classic mode and removes the appropriate
        port/vlan from the bridge
        """
        if self.in_vlan_aware_mode():
            return self.delete_from_bridge_vlan_aware()
        else:
            return self.delete_from_bridge_class_mode()
