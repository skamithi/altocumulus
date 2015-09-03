# Proto Cumulus ML2 Plugin

A different implementation of the cumulus ml2 plugin.

Not supported by Cumulus. Just me trying out some stuff.

It currently works in vlan aware mode only.

Comes in 2 parts

Install the "for_cumulus_switch" part on a switch. Its basically flask with some
ansible code. Then install ansible and netshow-linux-lib dependencies.
It provisions the vlans persistently into the configuration.

So configs survive a reboot. Only works with vlan tenant type.

2nd part goes on the network node, or wherever the neutron server is running.

See the notes embedded in the mechanism_driver.py for what to add to the
ml2_conf.ini

There is no startup script included yet for the flask api or any security
features. But thinking of integrating SSL nginx with API key as the
basic security.

This has not been tested in any real switch or server. Just using Cumulus VM and Rackspace
private cloud in vagrant.

It is part of my study of how ML2 plugins work.

