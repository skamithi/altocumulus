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
    bridgemems = []
    if bridgeiface.exists():
        bridgemems = bridgeiface.members
    if port_id in bridgemems:
        return update_bridge(bridgename, bridgemems)


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
    return update_bridge(bridgename, newbridgemems)
