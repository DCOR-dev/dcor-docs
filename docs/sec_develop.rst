================
DCOR Development
================

This section describes how to setup a DCOR development system
(CKAN + DCOR extensions).


Virtual machine
===============
At the time of this writing (August 2020), setting up CKAN in docker was not
straight forward. Therefore, we use a virtualized Ubuntu 20.04 as development
machine.

Download the `iso image <https://ubuntu.com/download/server>`_ and install
some requirements:

.. code::

   sudo apt update
   # CKAN requirements
   sudo apt install -y libpq5 redis-server nginx supervisor
   # needed for building packages that DCOR depends on (dclab)
   sudo apt install -y gcc python3-dev


Install CKAN:

.. code::

   wget http://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
   sudo dpkg -i python-ckan_2.9-py3-focal_amd64.deb


Follow the remainder of the installation guide at 
https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html#install-and-configure-postgresql.


DCOR Extensions
===============
For the development machine (client), it makes sense to have direct access to the
DCOR repositories located on the host machine (without having to git or rsync data
back and forth).

On the host machine, create a directory where all relevant repositories
will be cloned to (e.g. ``/home/paul/repos/DCOR``).

.. code::

   mkdir -p /home/paul/repos/DCOR
   cd /home/paul/repos/DCOR
   git clone git@github.com:DCOR-dev/dcor_control.git
   git clone git@github.com:DCOR-dev/dcor_shared.git
   git clone git@github.com:DCOR-dev/ckanext-dc_log_view.git
   git clone git@github.com:DCOR-dev/ckanext-dc_serve.git
   git clone git@github.com:DCOR-dev/ckanext-dc_view.git
   git clone git@github.com:DCOR-dev/ckanext-dcor_depot.git
   git clone git@github.com:DCOR-dev/ckanext-dcor_schemas.git
   git clone git@github.com:DCOR-dev/ckanext-dcor_theme.git

In Virtual Machine Manager, add a "Filesystem" hardware. Choose "squash" mode
and set the source path to where the repositories are located on the host
machine (``/home/paul/repos/DCOR``). Set the target path to "/repos".

On the client machine, add the following line to `/etc/fstab`:

.. code::

   /repos   /dcor-repos    9p  trans=virtio,version=9p2000.L,rw    0   0

After ``mkdir /dcor-repos`` and ``mount /dcor-repos``, you can then access
the repositories of the host machine directly from the client machine.
To make sure that the *www-data* user has read access
to the repositories, add it to the group of the owner on the client machine
(This is possible because of the "squash" mode - in "managed" mode, we would
have to give permissions to libvirt-qemu on the host machine):

.. code::

   # assuming that the user name is "paul":
   usermod -a -G paul www-data



Important commands
==================
Restart CKAN

.. code::

   supervisorctl reload


Find out what went wrong in case of internal server errors:

.. code::

   supervisorctl status
   tail -n500 /var/log/ckan/ckan-uwsgi.stderr.log

