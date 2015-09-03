# Cumulus ML2 Plugin - Cumulus Switch Component

This python package is to be installed on the Cumulus Switch connected
to the Openstack servers

## Installation


### From the Cumulus Linux Community Repo

Add the apt sources.list entry for the Cumulus Linux Community Repo and
update the apt repository.  Install the ML2 plugin switch service using
``apt-get``

```

```


### From Source

* Git clone this repo

```
```

#### Install Build dependencies

* Install the latest cumulus ansible modules into the package.
```
git submodule init
git submodule update

```

* Install PBR and other python build dependencies


#### Create Python Wheel

```
python setup.py bdist_wheel
ls dist/
[something].whl
```

#### Install the Python Wheel


#### Move the init script to the right location.



#### Setup Secure webserver

Install nginx from the Cumulus Linux community repo.  Copy the nginx
configuration file to the appropriate location and setup SSL. Example shown
below

```
```

#### Configure the ML2 Plugin Switch Service

*  Add the API Key. This should be the same across all switches associated
with a single openstack cluster.

> Note: A switch should not be controlled by 2 openstack controllers. Only one.


* Copy the Flask service startup script to the appropriate /etc location.
```
```


