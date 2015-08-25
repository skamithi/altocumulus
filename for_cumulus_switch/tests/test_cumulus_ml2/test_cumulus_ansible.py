from nose.tools import assert_equals
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
    self.myobject.update_bridge_vlan_aware = mock.MagicMock(
        return_value='exec bridge vlan aware func')
    assert_equals(self.myobject.add_to_bridge(), 'exec bridge vlan aware func')

  def test_add_to_bridge_classic_mode(self):
    self.myobject.in_vlan_aware_mode = mock.MagicMock(return_value=False)
    self.myobject.update_bridge_classic_mode = mock.MagicMock(
        return_value='exec bridge vlan classic mode')
    assert_equals(self.myobject.add_to_bridge(), 'exec bridge vlan classic mode')
