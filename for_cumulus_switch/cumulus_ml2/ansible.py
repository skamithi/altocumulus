from netshowlib import netshowlib


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
    pass


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
