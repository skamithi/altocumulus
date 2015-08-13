from argparse import ArgumentParser

from flask import Flask, Response, request

from altocumulus.utils import Shell

DEFAULT_API_BIND = '0.0.0.0'
DEFAULT_API_PORT = 8140
DEFAULT_ROOT_HELPER = 'sudo'

def 400_fail(errmsg):
  pass

def 200_ok():
  pass

@app.route('/networks/<network_id>', methods=['PUT'])
def create_bridge(network_id):
    """Generic call for creating a linux bridge
    Args:
        network_id(str): network_id provided by openstack. first 12 chars
        matches name of the generated bridge
    Returns:
        200 Status OK back to the client, if everything is okay.
        400 Failed to the client if something is wrong.
    """
    errmsg = create_bridge_using_ansible(network_id)
    if errmsg:
        return 400_fail(errmsg)
    else:
        return 200_ok()

@app.route('/networks/<network_id>', methods=['DELETE'])
def delete_bridge(network_id):
     """Generic call for deleting a linux bridge
    Args:
        network_id(str): network_id provided by openstack. first 12 chars
        matches name of the generated bridge
    Returns:
        200 Status OK back to the client, if everything is okay.
        400 Failed to the client if something is wrong.
    """
    errmsg = delete_bridge_using_ansible(network_id):
    if errmsg:
        return 400_fail(errmsg)
    else:
        return 200_ok()

@app.route('/networks/<network_id>/<port_id>', methods=['DELETE'])
def add_port_to_bridge(network_id, port_id)
    """Generic call for adding a port to a linux bridge
    Args:
        network_id(str): network_id provided by openstack. first 12 chars
        matches name of the generated bridge
    Returns:
        200 Status OK back to the client, if everything is okay.
        400 Failed to the client if something is wrong.
    """
    errmsg = create_bridge_using_netshow(network_id)
    if errmsg:
        return 400_fail(errmsg)
    else:
        errmsg = create_port_to_bridge_using_ansible(network_id, port_id)
        if errmsg:
            return 400_fail(errmsg)
        else:
            return 200_ok()


@app.route('/networks/<network_id>/<port_id>', methods=['PUT'])
def delete_port_to_bridge(network_id, port_id)
    """Generic call for deleting a port to a linux bridge
    Args:
        network_id(str): network_id provided by openstack. first 12 chars
        matches name of the generated bridge
    Returns:
        200 Status OK back to the client, if everything is okay.
        400 Failed to the client if something is wrong.
    """
    errmsg = check_bridge_using__netshow(network_id)
    if errmsg:
        return 400_fail(errmsg)
    else:
        errmsg = delete_port_to_bridge_using_ansible(network_id, port_id)
        if errmsg:
            return 400_fail(errmsg)
        else:
            return 200_ok()


def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config-file', default='config.yml')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    config = utils.load_config(args.config_file)

    bind = config.get('bind', DEFAULT_API_BIND)
    port = config.get('port', DEFAULT_API_PORT)

    app.debug = config.get('debug', False)
    app.run(host=bind, port=port)
