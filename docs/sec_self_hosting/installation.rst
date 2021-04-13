============
Installation
============

This section describes how to setup your own DCOR production instance.


.. _selfhost_ubuntuckan:

Ubuntu and CKAN
===============

Please use an `Ubuntu 20.04 <https://ubuntu.com/download/server>`_
installation for any development or production usage. This makes it
easier to give support and track down issues.

Before proceeding with the installation of CKAN, install the following
packages:

.. code::

   apt update
   # CKAN requirements
   apt install -y libpq5 redis-server nginx supervisor
   # needed for building packages that DCOR depends on (dclab)
   apt install -y gcc python3-dev
   # additional tools that you might find useful, but are not actually required
   apt install -y aptitude net-tools mlocate screen needrestart python-is-python3


Install CKAN:

.. code::

   wget https://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
   dpkg -i python-ckan_2.9-py3-focal_amd64.deb


.. note::

   Do *NOT* setup file uploads when following the instructions
   at https://docs.ckan.org. DCOR has its own dedicated directories
   for data uploads. The command ``dcor inspect`` will try to
   setup/fix that for you.

Follow the remainder of the installation guide at 
https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html#install-and-configure-postgresql.
Make sure to note down the PostgreSQL password which you will need in the
initialization step.


Make sure to initiate the CKAN database with

.. code::

   source /usr/lib/ckan/default/bin/activate
   export CKAN_INI=/etc/ckan/default/ckan.ini
   ckan db init


DCOR by default stores all data on ``/data``. This makes it easier to
control backups and separate the CKAN/DCOR software from the actual data.
If you have not mounted a block device or a network share on ``/data``,
please create this directory with

.. code::

   mkdir /data



.. _selfhost_dcorext:

DCOR Extensions
===============

.. _selfhost_dcorext_inst:

Installation
------------

Whenever you need to run the ``ckan``/``dcor`` commands or have to update
Python packages, you have to first activate the CKAN virtual environment.

.. code::

    source /usr/lib/ckan/default/bin/activate

With the active environment, first install some basic requirements.

.. code::

    pip install --upgrade pip
    pip install wheel


Then, install DCOR, which will install all extensions including their
requirements.

.. code::

    pip install dcor_control


.. _selfhost_dcorext_init:

Initialization
--------------
The ``dcor_control`` package installed the entry point ``dcor`` which
allows you to manage your DCOR installation. Just type ``dcor --help``
to find out what you can do with it.

For the initial setup, you have to run the ``inspect`` command. You
can run this command on a routinely basis to make sure that your DCOR
installation is setup correctly.

.. code::

   source /usr/lib/ckan/default/bin/activate
   dcor inspect


Testing
-------
For testing, common practice is to create separate test databases. We adapt
the recipe from the `CKAN docs <https://docs.ckan.org/en/2.9/contributing/test.html>`_
to test the DCOR extensions (e.g. we don't need datastore).

- Activate the virtual environment::

   source /usr/lib/ckan/default/bin/activate

- Install the requirements::

   pip install -r /usr/lib/ckan/default/src/ckan/dev-requirements.txt
   # https://github.com/ckan/ckan/issues/5570
   pip install pytest-ckan

- Create the test database::

   sudo -u postgres createdb -O ckan_default ckan_test -E utf-8

- Create ckan.ini for testing::

   cp /etc/ckan/default/ckan.ini /etc/ckan/default/test-dcor.ini

  Modify test-dcor.ini::

    #sqlalchemy.url = postgresql://ckan_default:passw@localhost/ckan_default
    sqlalchemy.url = postgresql://ckan_default:passw@localhost/ckan_test

    #solr_url=http://127.0.0.1:8983/solr
    solr_url=http://127.0.0.1:8983/solr/ckan

- Configure `Solr Multi-core <https://docs.ckan.org/en/2.9/contributing/test.html?highlight=testing#configure-solr-multi-core>`_.

- Initialize the testing db::

    export CKAN_INI=/etc/ckan/default/test-dcor.ini
    ckan db init

You can then run the tests with e.g.::

  export CKAN_INI=/etc/ckan/default/test-dcor.ini
  pytest /path/to/ckanext-dcor_depot


SSL
===

You have two options. If you server is reachable through the internet, you
should use Let's encrypt (or a certificate from your organization) to set
up SSL. If you are hosting your server on the intranet (clinics scenario),
then you should create your own certificate and distribute it to your
users


Creating an SSL certificate (Intranet only)
-------------------------------------------
Start by creating your certificate (valid for 10 years)::

  openssl req -newkey rsa:4096 -x509 -sha256 -days 3650 -nodes -out fqdn.cert -keyout fqdn.key

where `fqdn` is your fully qualified domain name (FQDN) which maps to the
server's IP address. Make sure to enter it in the dialog (otherwise use
the IP address). This makes connection tests easier (e.g. if you only have
SSH access to the machine and need to use SSH tunneling to connect to the
CKAN instance by mapping its FQDN in the `/etc/hosts` file to `127.0.0.1`
on the testing client).

You may want to create an :ref:`encrypted access token <sec_sh_access_token>`
for your users.

Now proceed with the SSL configuration below, replacing "dcor.mpl.mpg.de"
with your FQDN.


Configuring nginx (SSL and uWSGI proxy)
---------------------------------------
Encrypting data transfer should be a priority for you. If your server
is available online, you can use e.g. `Let's Encrypt <https://letsencrypt.org/>`_
to obtain an SSL certificate.
If you are hosting CKAN/DCOR internally in your organization, you will have
to create a self-signed certificate and distribute the public key to the
client machines manually.

First copy the certificate to ``/etc/ssl/private``::

   cp dcor.mpl.mpg.de.cert /etc/ssl/certs/
   cp dcor.mpl.mpg.de.key /etc/ssl/private/

.. note::

   If dclab, Shape-Out, or DCOR-Aid cannot connect to your CKAN instance,
   it might be because the certificate in ``/etc/ssl/certs/`` does not
   contain the full certificate chain. In this case, just download the
   entire certificate chain using Firefox (right-lick on the shield
   symbol an look at the certificate - there should be a download
   option for the chained certificate somewhere) and replace the content
   of the .cert file with that.

Then, edit ``/etc/nginx/sites-enabled/ckan`` and replace its content with
the following (change ``dcor.mpl.mpg.de`` to whatever domain you use):

.. literalinclude:: nginx_ckan_config.txt
   :language: nginx

Now, we need to modify the CKAN uWSGI file at
``/etc/ckan/default/ckan-uwsgi.ini``:

.. literalinclude:: ckan-uwsgi.ini
   :language: ini


Unattended upgrades
===================
`Unattended upgrades <https://wiki.debian.org/UnattendedUpgrades>`_ offer a
simple way of keeping the server up-to-date and patched against security
vulnerabilities.

.. code::

   apt-get install unattended-upgrades apt-listchanges

Edit the file `/etc/apt/apt.conf.d/50unattended-upgrades` to your liking.
The default settings should already work, but you might want to setup
email notifications and automated reboots.

.. note::

   If you have access to an internal email server and wish to get
   email notifications from your system, install

   .. code::
   
      apt install bsd-mailx ssmtp

   and edit ``/etc/ssmtp/ssmtp.conf``:
   
   .. code:
   
      mailhub=post.your.internal.server.de
      hostname=dcor.your.domain.de
      FromLineOverride=YES

   Note that this is something different than CKAN email notifications.


