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

Let's first set up our development environment. The ``dcor_control``
package comes with a convenient ``dcor develop`` command. This command
will create the ``/dcor-repos`` directory, clone all DCOR-related
repositories into it and install each of them in editable mode.

.. note::

    If you have already installed all packages in editable mode from
    GitHub repositories, a simple `dcor update` will only update those
    (regardless of where they are located in the file system).

.. code::

   source /usr/lib/ckan/default/bin/activate
   pip install dcor_control
   dcor develop


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
