from cumulus_ml2 import ansible_cumulus
import mock


class TestPkgResource(object):
    def __init__(self):
        self.location = 'blah'


@mock.patch('cumulus_ml2.ansible_cumulus.pkg_resources.require')
def test_update_bridge(mock_install_location):
    my_object = TestPkgResource()
    mock_install_location.return_value = [my_object]
    ansible_cumulus.update_bridge('br0', ['eth1', 'eth3-4'])
