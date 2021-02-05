.. _selfhost:

============
Self-Hosting
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
   apt install -y aptitude net-tools mlocate screen needrestart


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

You can then run the tests with e.g.::

  export CKAN_INI=/etc/ckan/default/test-dcor.ini
  pytest /path/to/ckanext-dcor_depot


SSL
===
Encrypting data transfer should be a priority for you. If your server
is available online, you can use e.g. `Let's Encrypt <https://letsencrypt.org/>`_
to obtain an SSL certificate.
If you are hosting CKAN/DCOR internally in your organization, you will have
to create a self-signed certificate and distribute the public key to the
client machines manually.


First copy the certificate to ``/etc/ssl/private``.

.. code::

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
the following (change ``dcor.mpl.mpg.de`` to whatever domain you use).

.. code::

   proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone=cache:30m max_size=250m;
   proxy_temp_path /tmp/nginx_proxy 1 2;
    
   server {
       client_max_body_size 10G;
       listen       443 ssl http2;
       listen       [::]:443 ssl http2;
       server_name  dcor.mpl.mpg.de;        

       ssl_certificate "/etc/ssl/certs/dcor.mpl.mpg.de.cert";
       ssl_certificate_key "/etc/ssl/private/dcor.mpl.mpg.de.key";

       # Uncoment to avoid robots (only on development machines)
       #location = /robots.txt { return 200 "User-agent: *\nDisallow: /\n"; }

       # Uncomment to mask other bot's activities
       #location ^~ /backup { return 404; }
       #location ^~ /wp { return 404; }
       #location ^~ /wordpress { return 404; }
       #location ^~ /old { return 404; }
       #location ^~ /node/ { return 404; }
       #location ^~ /server { return 404; }
       #location ^~ /sitemap { return 404; }
       #location = /.well-known/security.txt { return 404; }

       location / {
           proxy_pass http://127.0.0.1:8080/;
           proxy_set_header Host $host;
           proxy_cache cache;
           proxy_cache_bypass $cookie_auth_tkt;
           proxy_no_cache $cookie_auth_tkt;
           proxy_cache_valid 30m;
           proxy_cache_key $host$scheme$proxy_host$request_uri;
           # In emergency comment out line to force caching
           # proxy_ignore_headers X-Accel-Expires Expires Cache-Control;
       }
   
   }

   # Redirect all traffic to SSL
   server {
       listen 80;
       listen [::]:80;
       server_name dcor.mpl.mpg.de;
       return 301 https://$host$request_uri;
   }

   # Optional: Reject traffic that is not directed at `dcor.mpl.mpg.de:80`
   server {
       listen 80 default_server;
       listen [::]:80 default_server;
       server_name _;
       return 444;
   }

   # Optional: Reject traffic that is not directed at `dcor.mpl.mpg.de:443`
   server {
   listen       443 default_server;
       listen       [::]:443 default_server;
       server_name  _;
       return 444;
       ssl_certificate "/etc/ssl/certs/ssl-cert-snakeoil.pem";
       ssl_certificate_key "/etc/ssl/private/ssl-cert-snakeoil.key";
   }


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


Known Issues
============

- When setting up CKAN error email notifications, emails are sent for every file
  accessed on the server. Set the logging level to "WARNING" in all sections
  in ``/etc/ckan/default/ckan.ini``.

- If you get the following errors in ``/var/log/ckan/ckan-uwsgi.stderr.log``:

  .. code::

    Error processing line 1 of /usr/lib/ckan/default/lib/python3.8/site-packages/ckanext-dcor-theme-nspkg.pth:

      Traceback (most recent call last):
        File "/usr/lib/python3.8/site.py", line 175, in addpackage
          exec(line)
        File "<string>", line 1, in <module>
        File "<frozen importlib._bootstrap>", line 553, in module_from_spec
      AttributeError: 'NoneType' object has no attribute 'loader'

    Remainder of file ignored

  Not sure what is causing this, but it was solved for me by editing
  the relevant .pth file. Add a new line after the first semicolon.

  From

  .. code::

    import sys, types, os;has_mfs = sys.version_info > (3, 8);p = os.path.join(sys._getframe(1).$

  to

  .. code::

    import sys, types, os;
    has_mfs = sys.version_info > (3, 8);p = os.path.join(sys._getframe(1).$

  .. code::

    sed -i -- 's/os;has_mfs/os;\nhas_mfs/g' /usr/lib/ckan/default/lib/python3.8/site-packages/ckan*.pth

- If you get import errors like this and you are running a development server:

  .. code::

    Traceback (most recent call last):
      File "/etc/ckan/default/wsgi.py", line 12, in <module>
        application = make_app(config)
      File "/usr/lib/ckan/default/src/ckan/ckan/config/middleware/__init__.py", line 56, in make_app
        load_environment(conf)
      File "/usr/lib/ckan/default/src/ckan/ckan/config/environment.py", line 123, in load_environment
        p.load_all()
      File "/usr/lib/ckan/default/src/ckan/ckan/plugins/core.py", line 140, in load_all
        load(*plugins)
      File "/usr/lib/ckan/default/src/ckan/ckan/plugins/core.py", line 154, in load
        service = _get_service(plugin)
      File "/usr/lib/ckan/default/src/ckan/ckan/plugins/core.py", line 257, in _get_service
        raise PluginNotFoundException(plugin_name)
    ckan.plugins.core.PluginNotFoundException: dcor_schemas

  Please make sure that the ckan process/user has read (execute for directories)
  permission. The following might help, or you run UWSGI as root.

  .. code::

    chmod a+x /dcor-repos/*
    find /dcor-repos -type d -name ckanext |  xargs -0 chmod -R a+rx
    chmod -R a+rx /dcor-repos/dcor_control
    chmod -R a+rx /dcor-repos/dcor_shared