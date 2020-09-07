================
DCOR Development
================

This section describes how to setup a DCOR development system
(CKAN + DCOR extensions).


Setup Ubuntu and CKAN
=====================

Please use an `Ubuntu 20.04 <https://ubuntu.com/download/server>`_
installation for any development or production usage. This makes it
easier to give support and track down issues.

Beore proceeding with the installation of CKAN, install the following
packages:

.. code::

   apt update
   # CKAN requirements
   apt install -y libpq5 redis-server nginx supervisor
   # needed for building packages that DCOR depends on (dclab)
   apt install -y gcc python3-dev
   # additional tools that you might find useful, but are not actually required
   apt install aptitude net-tools


Install CKAN:

.. code::

   wget https://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
   dpkg -i python-ckan_2.9-py3-focal_amd64.deb


.. note::

   Do *NOT* setup setup file uploads when following the instructions
   at https://docs.ckan.org. DCOR has its own dedicated directories
   for data uploads. The command ``dcor inspect`` will try to
   setup/fix that for you.

Follow the remainder of the installation guide at 
https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html#install-and-configure-postgresql.
Make sure to note down the PostgreSQL password which you will need in the
initialization step.



DCOR by default stores all data on ``/data``. This makes it easier to
control backups and separate the CKAN/DCOR software from the actual data.
If you have not mounted a block device or a network share on ``/data``,
please create this directory with

.. code::

   mkdir /data
 

Install the DCOR Extensions
===========================

.. note::

    If you are installing DCOR in a virtual machine, it makes sense to
    access the extensions directories directly from the host system.
    (without having to git or rsync data back and forth).

    On the host machine, create a directory where all relevant repositories
    will be cloned to (e.g. ``/home/paul/repos/DCOR``).


    In Virtual Machine Manager, add a "Filesystem" hardware. Choose "managed" mode
    and set the source path to where the repositories are located on the host
    machine (``/home/paul/repos/DCOR``). Set the target path to "/repos".
    
    On the guest machine, add the following line to `/etc/fstab`:
    
    .. code::
    
       /repos   /dcor-repos    9p  trans=virtio,version=9p2000.L,rw    0   0
    
    After ``mkdir /dcor-repos`` and ``mount /dcor-repos``, you can then access
    the repositories of the host machine directly from the guest machine.
    In the "managed" mode, the guest system can set up its own permissions which
    don't affect permissions in the host system. In order for that to work,
    the libvirt user must have rw permissions. The easiest way to achieve that
    is to set the libvirt user to your user name, i.e. edit ``/etc/libvirt/qemu.conf``
    and set ``user = "paul"``.


Let's first choose a directory where all DCOR-related repositories will be
located (e.g. `/dcor-repos`). Clone all relevant directories. If you are
forking any of these repositories, you will wnat to run
`git clone git@github.com:username/repository_name.git`` instead.

.. code::

   mkdir -p /dcor-repos
   cd /dcor-repos
   git clone https://github.com/DCOR-dev/dcor_control.git
   git clone https://github.com/DCOR-dev/dcor_shared.git
   git clone https://github.com/DCOR-dev/ckanext-dc_log_view.git
   git clone https://github.com/DCOR-dev/ckanext-dc_serve.git
   git clone https://github.com/DCOR-dev/ckanext-dc_view.git
   git clone https://github.com/DCOR-dev/ckanext-dcor_depot.git
   git clone https://github.com/DCOR-dev/ckanext-dcor_schemas.git
   git clone https://github.com/DCOR-dev/ckanext-dcor_theme.git

Next, install each of those repositories in the CKAN virtual environment.

.. code::

    source /usr/lib/ckan/default/bin/activate
    cd /dcor-repos
    pip install --upgrade pip wheel
    # extensions
    pip install -e ckanext-dc_log_view
    pip install -e ckanext-dc_serve
    pip install -e ckanext-dc_view
    pip install -e ckanext-dcor_depot
    pip install -e ckanext-dcor_schemas
    pip install -e ckanext-dcor_theme
    # extension dependencies
    pip install -e dcor_shared
    pip install -r ckanext-dc_log_view/requirements.txt
    pip install -r ckanext-dc_serve/requirements.txt
    pip install -r ckanext-dc_view/requirements.txt
    pip install -r ckanext-dcor_depot/requirements.txt
    pip install -r ckanext-dcor_schemas/requirements.txt
    pip install -r ckanext-dcor_theme/requirements.txt
    # dcor control (this must be installed at the very end)
    pip install -e dcor_control


Initialize DCOR
===============
The ``dcor_control`` package installed the entry point ``dcor`` which
allows you to manage your DCOR installation. Just type ``dcor --help``
to find out what you can do with it.

For the initial setup, you have to run the ``inspect`` command. You
can run this command on a routinely basis to make sure that your DCOR
installation is setup correctly.

.. code::

   dcor inspect


Important commands
==================

System
------

Restart CKAN

.. code::

   supervisorctl reload


Find out what went wrong in case of internal server errors:

.. code::

   supervisorctl status
   tail -n500 /var/log/ckan/ckan-uwsgi.stderr.log

CKAN CLI
--------
Activate environment and set ``CKAN_INI``.

.. code::

   source /usr/lib/ckan/default/bin/activate
   export CKAN_INI=/etc/ckan/default/ckan.ini


Delete all data from the CKAN database:

.. code::

   ckan asset clean
   ckan db clean --yes
   ckan db init
   ckan search-index clear
