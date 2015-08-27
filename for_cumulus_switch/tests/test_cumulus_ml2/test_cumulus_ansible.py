from asserts import assert_equals
from cumulus_ml2 import cumulus_ansible
import mock


class TestPkgResource(object):
    def __init__(self):
        self.location = 'blah'


@mock.patch('cumulus_ml2.cumulus_ansible.ansible_inventory.Inventory')
@mock.patch('cumulus_ml2.cumulus_ansible.ansible_runner.Runner')
@mock.patch('cumulus_ml2.cumulus_ansible.pkg_resources.require')
def test_update_via_ansible_arguments_passed(mock_install_location,
                                             mock_runner, mock_inventory):
    my_object = TestPkgResource()
    mock_install_location.return_value = [my_object]
    mock_inventory.return_value = 'inventory'
    cumulus_ansible.update_config_via_ansible('br0', "eth1, eth3-4")
    mock_inventory.assert_called_with(['localhost'])
    mock_runner.assert_called_with(
        become=True,
        inventory='inventory',
        module_args="eth1, eth3-4",
        module_name='br0',
        module_path='blah/../../../ansible_modules/library',
        transport='local')


@mock.patch('cumulus_ml2.cumulus_ansible.ansible_inventory.Inventory')
@mock.patch('cumulus_ml2.cumulus_ansible.ansible_runner.Runner')
@mock.patch('cumulus_ml2.cumulus_ansible.pkg_resources.require')
def test_update_via_ansible_results_failed(mock_install_location,
                                           mock_runner, mock_inventory):
    my_object = TestPkgResource()
    mock_install_location.return_value = [my_object]
    mock_inventory.return_value = 'inventory'
    instance = mock_runner.return_value
    instance.run = mock.MagicMock(return_value={
        'dark': {},
        'contacted':
        {'localhost':
         {u'msg': u'missing required arguments: ports',
          u'failed': True,
          'invocation': {'module_name':
                         'cl_bridge',
                         'module_args': u'name=bridge vids=1,20,48,55,74'}}}})

    errormsg = cumulus_ansible.update_config_via_ansible('br0', "eth1, eth3-4")
    assert_equals(errormsg, u'missing required arguments: ports')


@mock.patch('cumulus_ml2.cumulus_ansible.reload_config')
@mock.patch('cumulus_ml2.cumulus_ansible.ansible_inventory.Inventory')
@mock.patch('cumulus_ml2.cumulus_ansible.ansible_runner.Runner')
@mock.patch('cumulus_ml2.cumulus_ansible.pkg_resources.require')
def test_update_via_ansible_changed_true(mock_install_location,
                                         mock_runner, mock_inventory,
                                         mock_reload_config):
    my_object = TestPkgResource()
    mock_install_location.return_value = [my_object]
    mock_inventory.return_value = 'inventory'
    instance = mock_runner.return_value
    instance.run = mock.MagicMock(return_value={
        'dark': {},
        'contacted':
        {'localhost':
         {u'msg': u'missing required arguments: ports',
          u'changed': True,
          'invocation': {'module_name':
                         'cl_bridge',
                         'module_args': u'name=bridge vids=1,20,48,55,74'}}}})

    cumulus_ansible.update_config_via_ansible('br0', "1,20,48,55,74")
    assert_equals(mock_reload_config.call_count, 1)


@mock.patch('cumulus_ml2.cumulus_ansible.ansible_inventory.Inventory')
@mock.patch('cumulus_ml2.cumulus_ansible.ansible_runner.Runner')
def test_reload(mock_runner, mock_inventory):
    mock_inventory.return_value = 'inventory'
    cumulus_ansible.reload_config()
    mock_inventory.assert_called_with(['localhost'])
    mock_runner.assert_called_with(
        become=True,
        inventory='inventory',
        module_args='/sbin/ifreload -a',
        module_name='shell', transport='local'
    )


class TestCumulusML2Ansible(object):

    @mock.patch('cumulus_ml2.cumulus_ansible.get_vlan_aware_bridge')
    def setup(self, mock_vlan_aware):
        mock_vlan_aware.return_value = None
        self.myobject = cumulus_ansible.CumulusML2Ansible(bridgename='brq11111',
                                                          vlan_id='123', port_id='bond11',
                                                          delete_vlan=False)

    def test_getting_bridge_ports(self):
        new_mock = mock.MagicMock()
        self.myobject._vlan_aware_bridge = new_mock
        member1 = mock.MagicMock()
        member2 = mock.MagicMock()
        member3 = mock.MagicMock()
        new_mock.members = {'bond0': member1, 'bond1': member2, 'peerlink': member3}
        assert_equals(self.myobject.bridge_ports, sorted(['bond0', 'bond1', 'peerlink']))

    def test_add_to_bridge_vlan_aware_works(self):
        self.myobject.in_vlan_aware_mode = mock.MagicMock(return_value=True)
        self.myobject.add_to_bridge_vlan_aware = mock.MagicMock(
            return_value='exec bridge vlan aware func')
        assert_equals(self.myobject.add_to_bridge(), 'exec bridge vlan aware func')

    def test_delete_from_bridge_vlan_aware_works(self):
        self.myobject.in_vlan_aware_mode = mock.MagicMock(return_value=True)
        self.myobject.delete_from_bridge_vlan_aware = mock.MagicMock(
            return_value='exec delete bridge vlan aware func')
        assert_equals(self.myobject.delete_from_bridge(),
                      'exec delete bridge vlan aware func')

    def test_in_vlan_aware_mode(self):
        self.myobject._vlan_aware_bridge = None
        assert_equals(self.myobject.in_vlan_aware_mode(), False)
        self.myobject._vlan_aware_bridge = mock.MagicMock()
        assert_equals(self.myobject.in_vlan_aware_mode(), True)

    def test_add_to_bridge_classic_mode(self):
        self.myobject.in_vlan_aware_mode = mock.MagicMock(return_value=False)
        self.myobject.add_to_bridge_classic_mode = mock.MagicMock(
            return_value='exec bridge vlan classic mode')
        assert_equals(self.myobject.add_to_bridge(), 'exec bridge vlan classic mode')

    @mock.patch('cumulus_ml2.cumulus_ansible.netshowlib.iface')
    def test_update_port_vlan_list_add_vlan(self, mock_iface):
        instance = mock_iface.return_value
        instance.vlan_list = ['1', '2', '3']
        self.myobject.vlan = '4'
        self.myobject.update_port_vlan_list()
        assert_equals(self.myobject.port_vids, ['1-4'])

    @mock.patch('cumulus_ml2.cumulus_ansible.netshowlib.iface')
    def test_update_port_vlan_list_delete_vlan(self, mock_iface):
        instance = mock_iface.return_value
        instance.vlan_list = ['1', '2', '3']
        self.myobject.delete_vlan = True
        self.myobject.vlan = '3'
        self.myobject.update_port_vlan_list()
        assert_equals(self.myobject.port_vids, ['1-2'])

    @mock.patch('cumulus_ml2.cumulus_ansible.netshowlib.iface')
    def test_update_bridge_vlan_list_add_vlan(self, mock_iface):
        main_bridge = mock_iface.return_value
        member1 = mock.MagicMock()
        member1.vlan_list = ['1', '2']
        member2 = mock.MagicMock()
        member2.vlan_list = ['3', '4']
        main_bridge.members = {'member1': member1, 'member2': member2}
        self.myobject._vlan_aware_bridge = main_bridge
        self.myobject.vlan = '5'
        self.myobject.update_bridge_vlan_list()
        assert_equals(self.myobject.bridge_vids, ['1-5'])

    @mock.patch('cumulus_ml2.cumulus_ansible.netshowlib.iface')
    def test_update_bridge_vlan_list_delete_vlan(self, mock_iface):
        main_bridge = mock_iface.return_value
        member1 = mock.MagicMock()
        member1.vlan_list = ['1', '2']
        member2 = mock.MagicMock()
        member2.vlan_list = ['3', '4']
        main_bridge.members = {'member1': member1, 'member2': member2}
        self.myobject._vlan_aware_bridge = main_bridge
        self.myobject.delete_vlan = True
        self.myobject.vlan = '2'
        self.myobject.update_bridge_vlan_list()
        assert_equals(self.myobject.bridge_vids, ['1', '3-4'])

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible.update_vlan_aware_port_config')
    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible.update_vlan_aware_bridge_config')
    def test_add_to_bridge_vlan_aware_port_config_as_error(self,
                                                           mock_bridge_config,
                                                           mock_port_config):
        mock_port_config.return_value = 'something failed'
        assert_equals(self.myobject.add_to_bridge_vlan_aware(),
                      'something failed')
        assert_equals(mock_bridge_config.call_count, 0)
        assert_equals(mock_port_config.call_count, 1)

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible.update_vlan_aware_port_config')
    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible.update_vlan_aware_bridge_config')
    def test_add_to_bridge_vlan_aware_bridge_config_as_error(self,
                                                             mock_bridge_config,
                                                             mock_port_config):
        mock_port_config.return_value = None
        mock_bridge_config.return_value = 'something failed'
        assert_equals(self.myobject.add_to_bridge_vlan_aware(),
                      'something failed')
        assert_equals(mock_bridge_config.call_count, 1)
        assert_equals(mock_port_config.call_count, 1)

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible.update_port_vlan_list')
    @mock.patch('cumulus_ml2.cumulus_ansible.update_config_via_ansible')
    def test_update_vlan_aware_port_config(self, mock_config_via_ansible,
                                           mock_update_port_vlan_list):
        self.myobject.port = 'bond0'
        self.myobject.port_vids = ['1-10']
        self.myobject.update_vlan_aware_port_config()
        # this test doesn't catch the fact that the call as 3 arguments not 2.
        mock_config_via_ansible.assert_called_with('cl_interface', 'name=bond0 vids=1-10 mstpctl_bpduguard=yes')

    @mock.patch('cumulus_ml2.cumulus_ansible.CumulusML2Ansible.update_bridge_vlan_list')
    @mock.patch('cumulus_ml2.cumulus_ansible.update_config_via_ansible')
    def test_update_vlan_aware_bridge_config(self, mock_config_via_ansible,
                                             mock_update_bridge_vlan_list):
        self.myobject._vlan_aware_bridge = mock.MagicMock()
        self.myobject.vlan_aware_bridge.name = 'bridge'
        self.myobject._bridge_ports = ['bond0', 'bond1', 'peerlink']
        self.myobject.bridge_vids = ['1-20']
        self.myobject.update_vlan_aware_bridge_config()
        mock_config_via_ansible.assert_called_with(
            'cl_bridge', 'name=bridge ports=bond0-1,peerlink vids=1-20')
