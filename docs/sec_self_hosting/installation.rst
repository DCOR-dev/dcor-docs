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


.. _selfhost_object_storage:


Scratch Space
=============
It is important that you have some scratch space of at least 100 GB available
on you system, so that the `ckanext-dc_serve` extension can create temporary
condensed datasets before uploading them to S3. By default, the cache is
located at `/data/tmp/ckanext-dc_serve` and is editable via the configuration
option `ckanext.dc_serve.tmp_dir`.


Object Storage
==============
You should use a cloud storage provider that you trust instead of setting this
up yourself. If you know what you are doing (e.g. for testing) and would like
to setup S3-compatible object storage yourself, you can use `MinIO
<https://min.io/download#/linux>`_. On a Ubuntu/Debian machine, install
the latest MinIO server like so::

    wget https://dl.min.io/server/minio/release/linux-amd64/minio_RELEASEDATE.0.0_amd64.deb
    dpkg -i minio_RELEASEDATE.0.0_amd64.deb

This also installed the ``minio`` systemd service which we want to use.
First, make sure that the user defined in the service::

    systemctl show minio | grep User=

actually exists. You can add a system user via::

    useradd -r minio-user

Then, create a file ``/etc/defaul/minio`` with the following content::

    # Volume to be used for MinIO server (make sure minio-user has access).
    MINIO_VOLUMES="/srv/minio"
    # Use if you want to run MinIO on a custom port (console is the web interface).
    MINIO_OPTS="--address :9000 --console-address :9001"
    # Root user for the server.
    MINIO_ROOT_USER=minio-root-user-account-name
    # Root secret for the server.
    MINIO_ROOT_PASSWORD=secret-password-for-minio-root-user
    # set this for MinIO to reload entries with 'mc admin service restart'
    MINIO_CONFIG_ENV_FILE=/etc/default/minio

Now you can enable and start the minio service::

    systemctl enable minio
    systemctl start minio

Create a "dcor" user (``http://minio.server.name:9001/identity/users/add-user``)
with `readwrite` permissions and create an access key (via "Service Accounts")
which you can then copy-paste to the ``ckan.ini`` configuration::

    dcor_object_store.access_key_id = access-key-id
    dcor_object_store.secret_access_key = secret-access-key

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


.. _selfhost_dcorext_worker:

Background workers
------------------
DCOR comes with three job queues `dcor-short`, `dcor-normal`, and `dcor-long`
for data processing after a resource is added to a dataset. The CKAN instance
populates those queues and CKAN workers (e.g. via `ckan jobs worker dcor-short`)
fetching and running the jobs in the background. The workers are run, like
ckan itself, via `supervisor` and are defined via individual configuration
files in `/etc/supervisor/conf.d`. When you run `dcor inspect` (see next
section), these files will be created with your approval.


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
If you are setting up a development instance, then you might want to be able
to run the DCOR tests. This step is not required if you are setting up an
instance for production.

For testing purposes, you can use the `DCOR vagrant box
<https://app.vagrantup.com/paulmueller/boxes/dcor-test>`_. It contains
a full install of DCOR (including SOLR and object storage) and is updated
regularly.

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

  openssl req -newkey rsa:4096 -x509 -config openssl-csr-config.txt -days 3650 -nodes -out dcor-example-com.crt -keyout dcor-example-com.key

using this `openssl-csr-config.txt` file:

.. literalinclude:: openssl-csr-config.txt
   :language: ini

where `dcor.example.com` is your fully qualified domain name (FQDN) which maps to the
server's IP address. Using the FQDN makes connection tests easier (e.g. if you only have
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

In order for unattended upgrades to work properly: whenever updates are
installed, make sure that `needrestart` automatically restarts the services
by editing the file `/etc/needrestart/needrestart.conf` and setting::

    $nrconf{restart} = 'a';


Supervisor
==========
Sometimes the ckan-uwsgi start job might take a little longer and the default
(1s) is not long enough so supervisor becomes impatient. Edit the file
``/etc/supervisor/conf.d/ckan-uwsgi.conf`` and add ``startsecs=60``.


Systemd
=======
It is important that all services required for CKAN to run should be started
before starting ``supervisor``. This can be achieved by running
``systemctl edit supervisor`` and pasting the following config::

    [Unit]
    Requires=solr.service
    After=solr.service
    Requires=redis.service
    After=redis.service
    Requires=postgresql.service
    After=postgresql.service

    [Service]
    Restart=always
    RestartSec=20

If `solr` is slow when starting up, add this to its unit file ``systemctl edit solr``::

    [Service]
    ExecStartPost=/bin/sleep 250
    Restart=on-failure
    RestartSec=10s


Afterwards run::

    systemctl daemon-reload
