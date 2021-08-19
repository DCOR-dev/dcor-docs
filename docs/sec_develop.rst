================
DCOR Development
================

This section describes how to setup a DCOR development system
(CKAN + DCOR extensions).


Ubuntu and CKAN
===============
We recommend to setup a virtual machine for development. It also works with
docker, but currently not out of the box
(see https://github.com/ckan/ckan/issues/5572).
Otherwise, the installation instructions are identical to those in the
:ref:`self-hosting section <selfhost_ubuntuckan>`.  



DCOR Extensions
===============

.. _sec_dev_install:

Installation
------------
This part differs from the installation for production. We want to have the
DCOR extensions installed in editable mode. 

.. note::

    If you are installing DCOR in a virtual machine, it makes sense to
    access the extensions directories directly from the host system.
    (without having to git or rsync data back and forth).

    On the host machine, create a directory where all relevant repositories
    will be cloned to (e.g. ``/home/paul/repos/DCOR``).


    In Virtual Machine Manager, add a "Filesystem" hardware. Choose "Path" driver,
    "Passthrough" mode, "Default" write policy and set the source path to where
    the repositories are located on the host machine (``/home/paul/repos/DCOR``).
    Set the target path to "/repos".
    
    On the guest machine, add the following line to `/etc/fstab`:
    
    .. code::
    
       /repos   /dcor-repos    9p  trans=virtio,version=9p2000.L,rw    0   0
    
    After ``mkdir /dcor-repos``, ``chmod a+rx /dcor-repos``,
    and ``mount /dcor-repos``, you can then access
    the repositories of the host machine directly from the guest machine.
    In order for everything to work properly, libvirt needs access to
    ``/home/paul/repos/DCOR``. The easiest way to achieve that
    is to set the libvirt user to your user name, i.e. edit ``/etc/libvirt/qemu.conf``
    and set ``user = "paul"`` (``systemctl restart libvirtd`` after doing so).


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

Next, install each of those repositories in the CKAN virtual environment
(in the exact same order).

.. code::

    source /usr/lib/ckan/default/bin/activate
    cd /dcor-repos
    pip install --upgrade pip wheel
    # shared extension dependency
    pip install -e dcor_shared
    # extensions
    pip install -e ckanext-dc_log_view
    pip install -e ckanext-dc_serve
    pip install -e ckanext-dc_view
    pip install -e ckanext-dcor_depot
    pip install -e ckanext-dcor_schemas
    pip install -e ckanext-dcor_theme
    # dcor control (this must be installed at the very end)
    pip install -e dcor_control


Initialization
--------------
Please follow the :ref:`initialization steps for self-hosting
<selfhost_dcorext_init>`.



Load some test data into the database
=====================================
You can test the basic functionalities of your DCOR installation by
importing these publicly available datasets from figshare:

.. code::

   ckan import-figshare


robots.txt
==========
If you don't want bots to index you site, add the following line
to the server section in ``/etc/nginx/sites-enabled/ckan``
(right before ``location / { [...]``):

.. code::

   location = /robots.txt { return 200 "User-agent: *\nDisallow: /\n"; }


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


CLI
---
If you are using the CKAN or DCOR CLI, activate environment and set
``CKAN_INI``.

.. code::

   source /usr/lib/ckan/default/bin/activate
   export CKAN_INI=/etc/ckan/default/ckan.ini


User ``ckan --help`` and ``dcor --help`` to get a list of commands.
E.g. to list all jobs, use

.. code::

   ckan jobs list

To reset the CKAN database and search index:

.. code::

   dcor reset
