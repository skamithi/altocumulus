from argparse import ArgumentParser
from flask import Flask
import cumulus_ml2.ansible as cumulus_ml2_ansible
import cumulus_ml2.netshow as cumulus_ml2_netshow

DEFAULT_API_BIND = '0.0.0.0'
DEFAULT_API_PORT = 8140
DEFAULT_ROOT_HELPER = 'sudo'

app = Flask(__name__)


def send_400_fail(errmsg):
    pass


def send_200_ok():
    pass


def bridge_name(network_id, prefix='brq'):
    """ returns bridge name used in creation or deletion of openstack generated
    bridge

    Args:
      network_id (str): Openstack network id. Really long hash string. First 12
      chars are used to generate bridge name
      prefix (str): Prefix to use when creating bridge name. Defaults to ``brq``

    Returns:
      None if network_id is invalid
      Bridge name if network_is is valid
    """
    try:
        if not isinstance(network_id, unicode):
            return None
    except NameError:
        if not isinstance(network_id, str):
            return None
    if len(network_id) < 12:
        return None

    return prefix + network_id[0:11]


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
    errmsg = cumulus_ml2_ansible.create_bridge(bridge_name(network_id))
    if errmsg:
        return send_400_fail(errmsg)
    else:
        return send_200_ok()


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
    errmsg = cumulus_ml2_ansible.delete_bridge(bridge_name(network_id))
    if errmsg:
        return send_400_fail(errmsg)
    else:
        return send_200_ok()


@app.route('/networks/<network_id>/<port_id>', methods=['PUT'])
def add_port_to_bridge(network_id, port_id):
    """Generic call for adding a port to a linux bridge
    Args:
        network_id(str): network_id provided by openstack. first 12 chars
        matches name of the generated bridge
    Returns:
        200 Status OK back to the client, if everything is okay.
        400 Failed to the client if something is wrong.
    """
    # create a bridge if is not there..If it exists, just return none
    errmsg = cumulus_ml2_ansible.create_bridge(network_id)
    if errmsg:
        return send_400_fail(errmsg)
    else:
        errmsg = cumulus_ml2_ansible.add_to_bridge(
            bridge_name(network_id), port_id)
        if errmsg:
            return send_400_fail(errmsg)
        else:
            return send_200_ok()


@app.route('/networks/<network_id>/<port_id>', methods=['DELETE'])
def delete_port_to_bridge(network_id, port_id):
    """Generic call for deleting a port to a linux bridge
    Args:
        network_id(str): network_id provided by openstack. first 12 chars
        matches name of the generated bridge
    Returns:
        200 Status OK back to the client, if everything is okay.
        400 Failed to the client if something is wrong.
    """
    errmsg = cumulus_ml2_netshow.check_bridge(bridge_name(network_id))
    if errmsg:
        return send_400_fail(errmsg)
    else:
        errmsg = cumulus_ml2_ansible.delete_bridge(
            bridge_name(network_id, port_id))
        if errmsg:
            return send_400_fail(errmsg)
        else:
            return send_200_ok()


def main():
    """forms executable function for usr/bin/cumulus-flask-api
    """
    parser = ArgumentParser()
    parser.add_argument('-c', '--config-file', default='config.yml')
    parser.add_argument('-d', '--debug', action='store_true')

#    args = parser.parse_args()

#    config = utils.load_config(args.config_file)
#
#    bind = config.get('bind', DEFAULT_API_BIND)
#    port = config.get('port', DEFAULT_API_PORT)

#    app.debug = config.get('debug', False)
#    app.run(host=bind, port=port)
