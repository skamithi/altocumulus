from netshowlib import netshowlib
import ansible.runner
import ansible.constants
import pkg_resources
import os


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
    ansible.constants.DEFAULT_MODULE_PATH = os.path.join(install_location,
                                                         '..',
                                                         '..',
                                                         '..',
                                                         'ansible_modules',
                                                         'library')
    ansible.constants.HOST_KEY_CHECKING = False
    inv = ansible.inventory.Inventory(['localhost'])
    modargs_str = "name=%s ports='%s'" % (bridgename, bridgemems)
    ansible.runner.Runner(
        module_name='cl_bridge',
        module_args=modargs_str, inventory=inv).run()


def delete_bridge(bridgename):
    """deletes a bridge interface using cumulus ansible module
    Args:
        bridgename(str): name of the bridge to create
    Returns:
        None: if successful
        An error message string if failed
    """
    pass


def add_to_bridge(bridgename, port_id):
    """ add a port to the bridge using cumulus ansible module
    Args:
        bridgename(str): name of the bridge to add port to
        port_id(str): name of the port to add to the bridge
    Returns:
        None: if successful
        An error message string if faileda
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
        An error message string if faileda
    """
    bridgeiface = netshowlib.iface(bridgename)
    if not bridgeiface.exists():
        return "bridge does not exist"
    bridgemems = list(bridgeiface.members.keys())
    try:
        newbridgemems = bridgemems.remove(port_id)
    except ValueError:
        return "port %s not a part of the bridge" % (port_id)
    return update_bridge(bridgename, sorted(newbridgemems))
