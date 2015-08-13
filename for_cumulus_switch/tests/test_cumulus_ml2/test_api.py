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
            mock_200_ok, mock_400_fail, mock_using_ansible):

        mock_400_fail.return_value = Response(status=400)
        mock_200_ok.return_value = Response(status=200)
        # if ansible generates an error message
        mock_using_ansible.return_value = 'error_msg'
        response = self.app.put('/networks/br1111')
        assert_equals(response.status_code, 400)
        # if ansible generates no errors
        mock_using_ansible.return_value = None
        response = self.app.put('/networks/br1111')
        assert_equals(response.status_code, 200)


