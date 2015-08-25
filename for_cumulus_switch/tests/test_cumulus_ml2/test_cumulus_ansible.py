from asserts import assert_equals
from cumulus_ml2 import cumulus_ansible
import mock


class TestCumulusML2Ansible(object):

    @mock.patch('cumulus_ml2.cumulus_ansible.get_vlan_aware_bridge')
    def setup(self, mock_vlan_aware):
        mock_vlan_aware.return_value = None
        self.myobject = cumulus_ansible.CumulusML2Ansible(bridgename='brq11111',
                                                          vlan_id='123', port_id='bond11')

    def test_add_to_bridge_vlan_aware_works(self):
        self.myobject.in_vlan_aware_mode = mock.MagicMock(return_value=True)
        self.myobject.add_to_bridge_vlan_aware = mock.MagicMock(
            return_value='exec bridge vlan aware func')
        assert_equals(self.myobject.add_to_bridge(), 'exec bridge vlan aware func')

    def test_add_to_bridge_classic_mode(self):
        self.myobject.in_vlan_aware_mode = mock.MagicMock(return_value=False)
        self.myobject.add_to_bridge_classic_mode = mock.MagicMock(
            return_value='exec bridge vlan classic mode')
        assert_equals(self.myobject.add_to_bridge(), 'exec bridge vlan classic mode')

    @mock.patch('cumulus_ml2.cumulus_ansible.netshowlib.iface')
    def test_update_port_vlan_list(self, mock_iface):
        instance = mock_iface.return_value
        instance.vlan_list = ['1', '2', '3']
        self.myobject.vlan = '4'
        assert_equals(self.myobject.update_port_vlan_list(), ['1-4'])

    @mock.patch('cumulus_ml2.cumulus_ansible.netshowlib.iface')
    def test_update_bridge_vlan_list(self, mock_iface):
        main_bridge = mock_iface.return_value
        member1 = mock.MagicMock()
        member1.vlan_list = ['1', '2']
        member2 = mock.MagicMock()
        member2.vlan_list = ['3', '4']
        main_bridge.members = {'member1': member1, 'member2': member2}
        self.myobject.vlan_aware_bridge = main_bridge
        assert_equals(self.myobject.update_bridge_vlan_list(), ['1-4'])
