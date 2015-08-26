from netshowlib import netshowlib
from netshowlib.linux.common import create_range
import pkg_resources
import os
import ansible


def get_vlan_aware_bridge():
    """ checks if Cumulus switch has vlan aware bridge
    Returns:
        True if vlan aware bridge is present
    """
    portlist = netshowlib.portname_list()
    for _portname in portlist:
        _iface = netshowlib.iface(_portname)
        if hasattr(_iface, 'vlan_filtering') and \
                _iface.vlan_filtering and \
                _iface.is_bridge():
                    return _iface
    return None


def update_config_via_ansible(self, modname, modargs_str):
    install_location = pkg_resources.require('cumulus-ml2-service')[0].location
    _library = os.path.join(install_location, '..', '..', '..',
                            -                            'ansible_modules', 'library')
    inv = ansible.inventory.Inventory(['localhost'])
    results = ansible.runner.Runner(
        module_name=modname,
        module_path=_library,
        become=True,
        transport='local',
        module_args=modargs_str, inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']
    itworked = results.get('contacted')
    # if the change actually occurred reload the config
    if itworked['localhost'].get('changed'):
        return reload_config()


def reload_config():
    """ run ifreload -a to push the changes into the persistent config
    """
    inv = ansible.inventory.Inventory(['localhost'])
    results = ansible.runner.Runner(
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
        self.vlan_aware_bridge = get_vlan_aware_bridge()
        self.port_vids = None
        self.bridge_vids = None
        self.delete_vlan = delete_vlan

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
        modargs_str = 'name=%s vids=%s' % (self.port, ','.join(self.port_vids))
        return update_config_via_ansible(modname, modargs_str)

    def update_vlan_aware_bridge_config(self):
        """ runs function to add/remove vlan from bridge vlan list then
        sends appropriate module and module arguments to ansible to make the
        config change
        """
        self.update_bridge_vlan_list()
        modname = 'cl_bridge'
        modargs_str = 'name=%s vids=%s' % (
            self.vlan_aware_bridge.name, ','.join(self.bridge_vids))
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
        """ delete vlan from vlan aware bridge
        Returns:
            error string if failed
        """
        errmsg = self.update_vlan_aware_port_config()
        if errmsg:
            return errmsg

        errmsg = self.update_vlan_aware_bridge_config()
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
