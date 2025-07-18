=======================
Manually upgrading DCOR
=======================

Note that it is recommended to use the Ansible playbooks instead.
Upgrading with ansible only means incrementing the CKAN version numbers
and file hashes.

The following instructions describe the upgrade process for a manual installation.

DCOR only
=========

Updating DCOR is done via the command::

    dcor update

This will update all extensions to the latest release (if installed from
PyPI) or to the latest commit (if installed from git repositories).

After each update, you should make sure that your installation is still set
up correctly. The following command will check your configuration files
(amongst other things)::

    dcor inspect


Upgrading CKAN/DCOR
===================

If you would like to upgrade CKAN via a .deb package (recommended), you may have
to install DCOR again (because the environment will be reset). First, follow the
steps to upgrade CKAN from the `CKAN docs
<https://docs.ckan.org/en/latest/maintaining/upgrading/index.html#upgrading>`_:

1. Make sure your system is up-to-date and not running any outdated binaries.

2. Activate the virtual environment::

     source /usr/lib/ckan/default/bin/activate
     export CKAN_INI=/etc/ckan/default/ckan.ini

4. Shut down all services::

     systemctl stop supervisor
     systemctl stop nginx

5. Create a database backup::

     mkdir -p CKAN_updates
     DATE=$(printf '%(%Y-%m-%d)T\n' -1)
     CKANVER=$(python -c "import ckan; print(ckan.__version__)")
     sudo -u postgres pg_dump --format=custom -d ckan_default > CKAN_updates/ckan_${CKANVER}_${DATE}.dump

6. Check the `CKAN Changelog <https://github.com/ckan/ckan/blob/master/CHANGELOG.rst>`_
   to see if there are any incompatibilities. Making a patch release upgrade should not be
   problematic, but if you are planning to upgrade to a minor release, please be careful.
   You should probably also check the `CKAN upgrade docs
   <https://docs.ckan.org/en/latest/maintaining/upgrading/index.html#upgrade-ckan>`_.

   Install the latest version of CKAN for your system::

     CKANMINOR=2.11
     CKANPATCH=2.11.3
     UBUNTURELEASE=$(lsb_release -cs)
     DLNAMESERVR=python-ckan_${CKANMINOR}-${UBUNTURELEASE}_amd64.deb
     DLNAMELOCAL=python-ckan_${CKANPATCH}-${UBUNTURELEASE}_amd64.deb
     mkdir -p CKAN_updates
     wget https://packaging.ckan.org/${DLNAMESERVR} -O CKAN_updates/${DLNAMELOCAL}
     apt-get -y remove python-ckan
     rm -rf /usr/lib/ckan/
     dpkg -i CKAN_updates/${DLNAMELOCAL}

7. Reactivate the environment::

     deactivate
     source /usr/lib/ckan/default/bin/activate
     export CKAN_INI=/etc/ckan/default/ckan.ini

8. For the upgrade from CKAN 2.9 to 2.10, Solr must be installed (previous versions of Solr were
   installed via ``apt``)::

     apt purge tomcat9 solr-tomcat

   Then, install solr manually as described in (installing ``openjdk-11-jdk-headless``
   is sufficient, you don't have to install ``openjdk-11-jdk``).
   https://docs.ckan.org/en/latest/maintaining/installing/solr.html?highlight=solr#installing-solr-manually
   (CKAN 2.11 recommends solr 9.x).
   Note that solr by default listens to tcp6 (IPv6). Thus, any setting in the
   ckan.ini file that uses `127.0.0.1` will not work - use `localhost` instead.
   To test solr, make sure that the following URL returns JSON data:
   ``http://localhost:8983/solr/ckan/select/?q=*:*&rows=1&wt=json``

9. Install DCOR (either via `pip` or as described in
   the :ref:`development section <sec_dev_install>`)::

     # This might be necessary if pip is still broken:
     #  wget https://gitlab.gwdg.de/pmuelle3/ckan-release-mirror/-/raw/main/get-pip.py?inline=false -O CKAN_updates/get-pip.py
     # Make sure there is no conflict between setuptools and distutils
     # (https://github.com/pypa/setuptools/issues/2993#issuecomment-1003765389)
     #  export SETUPTOOLS_USE_DISTUTILS=stdlib
     #  python CKAN_updates/get-pip.py
     pip install --upgrade pip wheel
     pip install --upgrade --force-reinstall dcor_control

10. Rerun rebranding scripts::

     sed -i 's/ckan.locale_default=en_US/ckan.locale_default=en_GB/g' /etc/ckan/default/ckan.ini
     ckan dcor-theme-main-css-branding
     ckan dcor-theme-i18n-branding

11. Make sure the configuration is intact (you may skip scanning for orphaned files)::

     dcor inspect

12. If the CKAN upgrade requires a database upgrade (see CKAN changelog)::

     ckan db upgrade
     # This will take some time. For installations with many datasets, consider
     # running it in a screen session:
     ckan search-index rebuild

13. Finally start nginx and supervisor::

     systemctl start nginx
     systemctl start supervisor
