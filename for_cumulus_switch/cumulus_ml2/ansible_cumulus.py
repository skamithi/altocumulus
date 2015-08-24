from netshowlib import netshowlib
import ansible.runner
import pkg_resources
import os


vlan_aware_bridgename = ''

def reload_config():
    """ run ifreload -a to push the changes into the persistent config
    """
    inv = ansible.inventory.Inventory(['localhost'])
    results = ansible.runner.Runner(
        module_name='shell',
        become=True,
        transport='local',
        module_args="/sbin/ifreload -a", inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']


def update_bridge(bridgename, vlan_id, port_id):
    """ creates or updates a cumulus linux bridge using
    the cumulus ansible modules
    Args:
        bridgename(str): name of the bridge to update/create
        bridgemems(str): list of ports to set to the bridge
    Returns:
        None if successful
        String error message if something bad occurs
    """
    # checks done at kernel level. No confirmation if in config
    # get list of members
    bridgemems = netshowlib.iface(bridgename).members.keys()
    # create swpX.Y port name or bondX.Y name
    portname = "%s.%s" % (port_id, vlan_id)
    # check if portname is in bridgelist if so, just exit, no errors
    if portname in bridgemems:
        return None

    # append to bridgemember list
    bridgemems.append(portname)
    # install updated bridgemem list to ifupdown config.
    install_location = pkg_resources.require('cumulus-ml2-service')[0].location
    _library = os.path.join(install_location, '..', '..', '..',
                            'ansible_modules', 'library')
    inv = ansible.inventory.Inventory(['localhost'])
    modargs_str = "name=%s ports='%s'" % (bridgename, ' '.join(sorted(bridgemems)))
    results = ansible.runner.Runner(
        module_name='cl_bridge',
        module_path=_library,
        become=True,
        transport='local',
        module_args=modargs_str, inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']
    itworked = results.get('contacted')
    # if the change actually occurred reload the config
    if itworked['localhost'].get('changed'):
        return reload_config()


def delete_bridge(bridgename):
    """deletes a bridge interface using cumulus ansible module
    Args:
        bridgename(str): name of the bridge to create
    Returns:
        None: if successful
        An error message string if failed
    """
    inv = ansible.inventory.Inventory(['localhost'])
    delete_bridge_str = "/bin/rm /etc/network/interfaces.d/%s" % (bridgename)
    results = ansible.runner.Runner(
        module_name="shell",
        become=True,
        transport='local',
        module_args=delete_bridge_str, inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']
    itworked = results.get('contacted')
    # if the change actually occurred reload the config
    if itworked['localhost'].get('changed'):
        return reload_config()


def add_to_bridge(bridgename, vlan_id, port_id):
    """ add a port to the bridge using cumulus ansible module. if the switch is
    running in traditional mode, then configure the port in a traditional way,
    otherwise check for vlan aware mode and provision that.
    Args:
        bridgename(str): name of the bridge to add port to, if using traditional
        mode
        vlan_id(str): vlan to add to the vlan aware bridge ports or use it to
        create trunk of switch port in traditional mode
        port_id(str): name of the port to add to the bridge. If a string that
        says 'none', then ignore if in vlan aware mode. if if traditional mode
        it should have a valid port.
    Returns:
        None: if successful
        An error message string if failed
    """
    if in_vlan_aware_mode():
      return update_bridge_vlan_aware(vlan_id)
    else:
      return update_bridge(bridgename, vlan_id, port_id)


def delete_from_bridge(bridgename, vlan_id, port_id):
    """ delete a port from the bridge using cumulus ansible module. if switch is
    running in traditional mode it will delete the port from the bridge. if in
    vlan aware mode, it will remove the vlan from the vlan aware bridge.
    In traditional mode if the bridge has no members left, then delete the
    bridge
    Args:
        bridgename(str): name of the bridge to add port to
        vlan_id(str): vlan to remove from vlan aware bridge or vlan id for
        physical port to append before removing port from the bridge
        port_id(str): name of the port to add to the bridge
    Returns:
        None: if successful
        An error message string if failed
    """
    if in_vlan_aware_mode():
      return delete_from_bridge_vlan_aware(vlan_id)
    else:
      return delete_from_bridge_classic_mode(bridgename, vlan_id, port_id)

def in_vlan_aware_mode():
    """ Check kernel sysfs to see if any port is running in vlan aware mode.
    If it is, the the assumption is switch is running in vlan aware mode
    Returns:
      True: if in vlan aware mode
    """
    portlist = netshowlib.portname_list()
    for _portname in portlist:
      _iface = netshowlib.iface(_portname)
      if hasattr(iface, 'vlan_filtering') and \
        _iface.vlan_filtering() and \
        _iface.is_bridge():
            vlan_aware_bridgename = _iface.name
            return True
    return False

def update_bridge_vlan_aware(vlan_id):
    """ Call cumulus ansible module to add the missing vlan to the vlan aware
    bridge
    todo:
        refactor and utilize same ansible calling code across of these functions
    Returns:
        error string if something goes wrong
    """
    install_location = pkg_resources.require('cumulus-ml2-service')[0].location
    _library = os.path.join(install_location, '..', '..', '..',
                            'ansible_modules', 'library')
    inv = ansible.inventory.Inventory(['localhost'])
    #TODO check that vlan_aware_bridgename exists
    modargs_str = "name=%s vlan_aware=yes vids=%s" % (vlan_aware_bridgename, new_vlan_list(vlan_id))
    results = ansible.runner.Runner(
        module_name='cl_bridge',
        module_path=_library,
        become=True,
        transport='local',
        module_args=modargs_str, inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']
    itworked = results.get('contacted')
    # if the change actually occurred reload the config
    if itworked['localhost'].get('changed'):
        return reload_config()

    # search for interface in vlan aware mode

    # bridgeiface = netshowlib.iface(bridgename)
    # if not bridgeiface.exists():
    #     return "bridge does not exist"
    # bridgemems = list(bridgeiface.members.keys())
    # try:
    #   newbridgemems = bridgemems.remove(port_id)
    # except ValueError:
    #    return "port %s not a part of the bridge" % (port_id)
    # if there are bridge members left, update the bridge persisent config
    # if newbridgemems:
    #    return update_bridge(bridgename, sorted(newbridgemems))
    # else:
        # delete the bridge from the persisent config
    #    return delete_bridge(bridgename)
