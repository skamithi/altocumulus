from netshowlib import netshowlib
import ansible.runner
import ansible.constants
import pkg_resources
import os


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


def update_bridge(bridgename, bridgemems):
    """ creates or updates a cumulus linux bridge using
    the cumulus ansible modules
    Args:
        bridgename(str): name of the bridge to update/create
        bridgemems(str): list of ports to set to the bridge
    Returns:
        None if successful
        String error message if something bad occurs
    """
    install_location = pkg_resources.require('cumulus-ml2-service')[0].location
    _library = os.path.join(install_location, '..', '..', '..',
                            'ansible_modules', 'library')
    inv = ansible.inventory.Inventory(['localhost'])
    modargs_str = "name=%s ports='%s'" % (bridgename, ' '.join(bridgemems))
    results = ansible.runner.Runner(
        module_name='cl_bridge',
        module_path=_library,
        become=True,
        transport='local',
        module_args=modargs_str, inventory=inv).run()
    _error = results.get('dark')
    if _error:
        return _error['localhost']['msg']
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
    return reload_config()


def add_to_bridge(bridgename, port_id):
    """ add a port to the bridge using cumulus ansible module
    Args:
        bridgename(str): name of the bridge to add port to
        port_id(str): name of the port to add to the bridge
    Returns:
        None: if successful
        An error message string if failed
    """
    # get bridgemem list and add port id to the list
    bridgeiface = netshowlib.iface(bridgename)
    # if bridge doesn't exist create it with port_id as
    # first member otherwise append to list of existing
    # members and update bridge info
    bridgemems = [port_id]
    if bridgeiface.exists():
        bridgemems = list(bridgeiface.members.keys())
        if port_id not in bridgemems:
            bridgemems.append(port_id)
    return update_bridge(bridgename, sorted(bridgemems))


def delete_from_bridge(bridgename, port_id):
    """ delete a port from the bridge using cumulus ansible module
    Args:
        bridgename(str): name of the bridge to add port to
        port_id(str): name of the port to add to the bridge
    Returns:
        None: if successful
        An error message string if failed
    """
    bridgeiface = netshowlib.iface(bridgename)
    if not bridgeiface.exists():
        return "bridge does not exist"
    bridgemems = list(bridgeiface.members.keys())
    try:
        newbridgemems = bridgemems.remove(port_id)
    except ValueError:
        return "port %s not a part of the bridge" % (port_id)
    # if there are bridge members left, update the bridge persisent config
    if newbridgemems:
        return update_bridge(bridgename, sorted(newbridgemems))
    else:
        # delete the bridge from the persisent config
        return delete_bridge(bridgename)
