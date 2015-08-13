from cumulus.api import app
import mock
from nose.tools import assert_equals

class TestApi(self):
    def setup(self):
        self.app = app.test_client()

    @mock.patch('cumulus.api.create_bridge_using_ansible')
    @mock.patch('cumulus.api.400_fail')
    @mock.patch('cumulus.api.200_ok')
    def test_create_bridge(self,
            mock_200_ok, mock_400_fail, mock_using_ansible):
        # if ansible generates an error message
        mock_using_ansible.return_value = 'error_msg'
        mock_400_fail.return_value = 'golly i failed'
        response = self.app.put('/networks/br111122223333')
        assert_equals(response, '')


