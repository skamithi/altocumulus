from netshowlib import netshowlib
import ansible.runner
import pkg_resources
import os

def get_vlan_aware_bridge():
    portlist = netshowlib.portname_list()
    for _portname in portlist:
        _iface = netshowlib.iface(_portname)
        if hasattr(iface, 'vlan_filtering') and \
                _iface.vlan_filtering() and \
                _iface.is_bridge():
                    return _iface
    return None

class CumulusML2Ansible(bridgename=_bridgename,
        vlan=_vlan_id
        port=_port_id):
    def __init__(self, bridgename=_bridgename,
            vlan=_vlan_id
            port=_port_id):
        self.vlan = vlan
        self.port = port
        self.bridgename = bridgename
        self.vlan_aware_bridge = get_vlan_aware_bridge()

    def update_bridge_vlan_aware(self):
        pass

    def update_bridge_classic_mode(self):
        pass

    def add_to_bridge(self):
        if self.in_vlan_aware_mode():
            return self.update_bridge_vlan_aware()
        else:
            return self.update_bridge_classic_mode()
