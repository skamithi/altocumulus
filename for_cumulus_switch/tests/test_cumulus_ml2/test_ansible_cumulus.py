from cumulus_ml2 import ansible_cumulus
import mock


class TestPkgResource(object):
    def __init__(self):
        self.location = 'blah'


@mock.patch('cumulus_ml2.ansible_cumulus.ansible.inventory.Inventory')
@mock.patch('cumulus_ml2.ansible_cumulus.ansible.runner.Runner')
@mock.patch('cumulus_ml2.ansible_cumulus.pkg_resources.require')
def test_update_bridge(mock_install_location,
                       mock_runner, mock_inventory):
    my_object = TestPkgResource()
    mock_install_location.return_value = [my_object]
    mock_inventory.return_value = 'inventory'
    ansible_cumulus.update_bridge('br0', ['eth1', 'eth3-4'])
    mock_inventory.assert_called_with(['localhost'])
    mock_runner.assert_called_with(
        inventory='inventory',
        module_args="name=br0 ports='['eth1', 'eth3-4']'",
        module_name='cl_bridge')
