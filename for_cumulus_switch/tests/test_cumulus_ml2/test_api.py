from cumulus_ml2.api import app
from cumulus_ml2 import api
import mock
from nose.tools import assert_equals
from flask import Response


def test_setting_bridge_name_name_too_short():
  # bridgename length less than 12
  assert_equals(api.bridge_name('111'), None)

def test_setting_bridge_unicode():
  # for py2. for py3, which is not support for openstack just check for string
  assert_equals(api.bridge_name(u'111dffffffffffffffffffdf2'), 'brq111dfffffff')


class TestApi(object):
    def setup(self):
        self.app = app.test_client()


    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible')
    @mock.patch('cumulus_ml2.api.Response')
    def test_add_port_to_bridge_failure_occurred(self, mock_response,
        mock_cumulus_ansible):
      network_id = '111122223333444'
      vlan_id = '2222'
      port_id = 'bond0'
      instance = mock_cumulus_ansible.return_value
      mock_cumulus_ansible.assert_called_with('')
      instance.add_to_bridge = MagicMock(return_value='something bad happend')
      response = self.app.put(
          '/networks/%s/%s/%s' % (network_id, vlan_id, port_id))
      mock_response.assert_called_with('')



#        network_id = '1111222333323434'
#        mock_400_fail.return_value = Response(status=400)
#        mock_200_ok.return_value = Response(status=200)
#        # if ansible generates an error message
#        mock_using_ansible.return_value = 'error_msg'
#        response = self.app.delete('/networks/%s' % (network_id))
#        assert_equals(response.status_code, 400)
#        mock_using_ansible.assert_called_with('brq11112223333')
#        # if ansible generates no errors
#        mock_using_ansible.return_value = None
#        response = self.app.delete('/networks/%s' % (network_id))
#        assert_equals(response.status_code, 200)
#
#    @mock.patch('cumulus_ml2.ansible_cumulus.netshowlib.iface')
#    @mock.patch('cumulus_ml2.ansible_cumulus.update_bridge')
#    @mock.patch('cumulus_ml2.api.send_400_fail')
#    @mock.patch('cumulus_ml2.api.send_200_ok')
#    def test_add_to_bridge_first_member(self, mock_200_ok, mock_400_fail,
#                                        mock_update_bridge, mock_iface):
#        network_id = '1111222333323434'
#        port_id = 'swp1'
#        mock_400_fail.return_value = Response(status=400)
#        mock_200_ok.return_value = Response(status=200)
#        mymock = mock.MagicMock()
#        mymock.exists = mock.MagicMock(return_value=False)
#        mock_iface.return_value = mymock
#        mock_update_bridge.return_value = None
#        response = self.app.put('/networks/%s/%s' % (network_id, port_id))
#        mock_update_bridge.assert_called_with('brq11112223333', ['swp1'])
#        assert_equals(response.status_code, 200)
#        # if update_bridge returns an error
#        mock_update_bridge.return_value = 'error msg'
#        response = self.app.put('/networks/%s/%s' % (network_id, port_id))
#        assert_equals(response.status_code, 400)
#
#    @mock.patch('cumulus_ml2.ansible_cumulus.netshowlib.iface')
#    @mock.patch('cumulus_ml2.ansible_cumulus.update_bridge')
#    @mock.patch('cumulus_ml2.api.send_400_fail')
#    @mock.patch('cumulus_ml2.api.send_200_ok')
#    def test_add_to_bridge_other_members_exist(self, mock_200_ok, mock_400_fail,
#                                               mock_update_bridge, mock_iface):
#        network_id = '1111222333323434'
#        port_id = 'swp1'
#        mock_400_fail.return_value = Response(status=400)
#        mock_200_ok.return_value = Response(status=200)
#        mymock = mock.MagicMock()
#        mymock.exists = mock.MagicMock(return_value=True)
#        mymock.members = {'eth1': '',
#                          'eth2.1': '',
#                          'eth4.3': ''
#                          }
#        mock_iface.return_value = mymock
#        mock_update_bridge.return_value = None
#        response = self.app.put('/networks/%s/%s' % (network_id, port_id))
#        mock_update_bridge.assert_called_with('brq11112223333',
#                                              sorted(['eth2.1', 'eth4.3',
#                                                      'eth1', 'swp1']))
#        assert_equals(response.status_code, 200)
#
#        # if port already exists in member list
#        port_id = 'eth2.1'
#        response = self.app.put('/networks/%s/%s' % (network_id, port_id))
#        mock_update_bridge.assert_called_with('brq11112223333',
#                                              sorted(['eth2.1', 'eth4.3', 'eth1']))
#        assert_equals(response.status_code, 200)
#
#    @mock.patch('cumulus_ml2.ansible_cumulus.update_bridge')
#    @mock.patch('cumulus_ml2.ansible_cumulus.netshowlib.iface')
#    @mock.patch('cumulus_ml2.api.send_400_fail')
#    @mock.patch('cumulus_ml2.api.send_200_ok')
#    def test_delete_from_bridge(self, mock_200_ok, mock_400_fail,
#                                mock_iface,
#                                mock_update_bridge):
#        network_id = '1111222333323434'
#        port_id = 'eth2.1'
#        mock_400_fail.return_value = Response(status=400)
#        mock_200_ok.return_value = Response(status=200)
#
#        # if netshow says that the bridge is not there
#        mymock = mock.MagicMock()
#        mymock.exists = mock.MagicMock(return_value=False)
#        mock_iface.return_value = mymock
#        response = self.app.delete('/networks/%s/%s' % (network_id, port_id))
#        assert_equals(response.status_code, 400)
#
#        # if netshow says the bridge is there but cannot delete port from the bridge
#        mymock.exists = mock.MagicMock(return_value=True)
#        mymock.members = {'eth1': ''}
#        response = self.app.delete('/networks/%s/%s' % (network_id, port_id))
#        assert_equals(response.status_code, 400)
