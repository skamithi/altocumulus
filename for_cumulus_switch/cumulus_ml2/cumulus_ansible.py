from netshowlib import netshowlib
from netshowlib.linux.common import create_range


def get_vlan_aware_bridge():
    portlist = netshowlib.portname_list()
    for _portname in portlist:
        _iface = netshowlib.iface(_portname)
        if hasattr(_iface, 'vlan_filtering') and \
                _iface.vlan_filtering() and \
                _iface.is_bridge():
                    return _iface
    return None


class CumulusML2Ansible(object):
    def __init__(self, bridgename, vlan_id, port_id):
        self.port = port_id
        self.bridgename = bridgename
        self.vlan = vlan_id
        self.vlan_aware_bridge = get_vlan_aware_bridge()

    def update_port_vlan_list(self):
        """ removes or adds vlans to the bridge vlan list.
        """
        port_vlan_list = netshowlib.iface(self.port).vlan_list
        port_vlan_list.append(self.vlan)
        return create_range('', set(port_vlan_list))

    def update_bridge_vlan_list(self):
        """ get a list of all vlans found on the vlan aware bridge
        """
        vlan_list = []
        bridgemems = self.vlan_aware_bridge.members.values()
        for _member in bridgemems:
            vlan_list += (_member.vlan_list)

        return create_range('', set(vlan_list))

    def update_bridge_classic_mode(self):
        pass

    def add_to_bridge(self):
        if self.in_vlan_aware_mode():
            return self.add_to_bridge_vlan_aware()
        else:
            return self.add_to_bridge_classic_mode()
