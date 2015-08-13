from cumulus_ml2.api import app
import mock
from nose.tools import assert_equals
from flask import Response


class TestApi(object):
    def setup(self):
        self.app = app.test_client()

    @mock.patch('cumulus_ml2.ansible.create_bridge')
    @mock.patch('cumulus_ml2.api.send_400_fail')
    @mock.patch('cumulus_ml2.api.send_200_ok')
    def test_create_bridge(self,
                           mock_200_ok, mock_400_fail,
                           mock_using_ansible):
        network_id = '1111222333323434'
        mock_400_fail.return_value = Response(status=400)
        mock_200_ok.return_value = Response(status=200)
        # if ansible generates an error message
        mock_using_ansible.return_value = 'error_msg'
        response = self.app.put('/networks/%s' % (network_id))
        assert_equals(response.status_code, 400)
        mock_using_ansible.assert_called_with('brq11112223333')
        # if ansible generates no errors
        mock_using_ansible.return_value = None
        response = self.app.put('/networks/%s' % (network_id))
        assert_equals(response.status_code, 200)

    @mock.patch('cumulus_ml2.ansible.delete_bridge')
    @mock.patch('cumulus_ml2.api.send_400_fail')
    @mock.patch('cumulus_ml2.api.send_200_ok')
    def test_delete_bridge(self,
                           mock_200_ok, mock_400_fail,
                           mock_using_ansible):
        network_id = '1111222333323434'
        mock_400_fail.return_value = Response(status=400)
        mock_200_ok.return_value = Response(status=200)
        # if ansible generates an error message
        mock_using_ansible.return_value = 'error_msg'
        response = self.app.delete('/networks/%s' % (network_id))
        assert_equals(response.status_code, 400)
        mock_using_ansible.assert_called_with('brq11112223333')
        # if ansible generates no errors
        mock_using_ansible.return_value = None
        response = self.app.delete('/networks/%s' % (network_id))
        assert_equals(response.status_code, 200)
