==============
Upgrading DCOR
==============

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
to install DCOR again (because the environment might be reset).

1. https://docs.ckan.org/en/2.9/maintaining/upgrading/index.html#upgrading

2. Install DCOR (either via `pip install dcor_control` or as described in
   the :ref:`development section <sec_dev_install>`).
