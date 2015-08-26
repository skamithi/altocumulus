from cumulus_ml2.api import app
from cumulus_ml2 import api
import mock
from nose.tools import assert_equals


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
        instance.add_to_bridge = mock.MagicMock(
            return_value='something bad happened')
        self.app.put(
            '/networks/%s/%s/%s' % (network_id, vlan_id, port_id))
        mock_response.assert_called_with('something bad happened',
                                         mimetype='text/plain', status=400)
        mock_cumulus_ansible.assert_called_with(bridgename=u'brq11112222333',
                                                port_id=u'bond0', vlan_id=u'2222')

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible')
    @mock.patch('cumulus_ml2.api.Response')
    def test_add_port_to_bridge_no_failure_occurred(self, mock_response,
                                                    mock_cumulus_ansible):
        network_id = '111122223333444'
        vlan_id = '2222'
        port_id = 'bond0'
        instance = mock_cumulus_ansible.return_value
        instance.add_to_bridge = mock.MagicMock(
            return_value=None)
        add_to_bridge_func_call = mock.call().add_to_bridge()

        self.app.put(
            '/networks/%s/%s/%s' % (network_id, vlan_id, port_id))
        mock_response.assert_called_with(None,
                                         mimetype='text/plain', status=200)
        mock_cumulus_ansible.assert_called_with(bridgename=u'brq11112222333',
                                                port_id=u'bond0', vlan_id=u'2222')
        assert_equals(mock_cumulus_ansible.mock_calls[1],
                      add_to_bridge_func_call)

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible')
    @mock.patch('cumulus_ml2.api.Response')
    def test_delete_port_from_bridge_successful(self, mock_response,
                                                mock_cumulus_ansible):
        network_id = '111122223333444'
        vlan_id = '2222'
        port_id = 'bond0'
        instance = mock_cumulus_ansible.return_value
        instance.delete_from_bridge = mock.MagicMock(
            return_value=None)
        delete_from_bridge_func_call = mock.call().delete_from_bridge()
        self.app.delete(
            '/networks/%s/%s/%s' % (network_id, vlan_id, port_id))
        mock_response.assert_called_with(None,
                                         mimetype='text/plain', status=200)
        mock_cumulus_ansible.assert_called_with(bridgename=u'brq11112222333',
                                                port_id=u'bond0', vlan_id=u'2222')

        assert_equals(mock_cumulus_ansible.mock_calls[1],
                      delete_from_bridge_func_call)

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible')
    @mock.patch('cumulus_ml2.api.Response')
    def test_delete_port_from_bridge_fails(self, mock_response, mock_cumulus_ansible):
        network_id = '111122223333444'
        vlan_id = '2222'
        port_id = 'bond0'
        instance = mock_cumulus_ansible.return_value
        instance.delete_from_bridge = mock.MagicMock(
            return_value='failed')
        self.app.delete(
            '/networks/%s/%s/%s' % (network_id, vlan_id, port_id))
        mock_response.assert_called_with('failed',
                                         mimetype='text/plain', status=400)
        mock_cumulus_ansible.assert_called_with(bridgename=u'brq11112222333',
                                                port_id=u'bond0', vlan_id=u'2222')
