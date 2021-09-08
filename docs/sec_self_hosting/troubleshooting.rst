===============
Troubleshooting
===============

- When setting up CKAN error email notifications, emails are sent for every file
  accessed on the server. Set the logging level to "WARNING" in all sections
  in ``/etc/ckan/default/ckan.ini``.

- If you get the following errors in ``/var/log/ckan/ckan-uwsgi.stderr.log``::

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

- If you get import errors like this and you are running a development server::

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
  permission. The following might help, or you run UWSGI as root::

    chmod a+x /dcor-repos/*
    find /dcor-repos -type d -name ckanext |  xargs -0 chmod -R a+rx
    chmod -R a+rx /dcor-repos/dcor_control
    chmod -R a+rx /dcor-repos/dcor_shared


- If you are having issues with HDF5 file locking and are storing your
  data on a network file storage::

    Traceback (most recent call last):
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/rq/worker.py", line 812, in perform_job
        rv = job.perform()
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/rq/job.py", line 588, in perform
        self._result = self._execute()
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/rq/job.py", line 594, in _execute
        return self.func(*self.args, **self.kwargs)
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/ckanext/dcor_schemas/jobs.py", line 27, in set_dc_config_job
        with dclab.new_dataset(path) as ds:
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/dclab/rtdc_dataset/load.py", line 63, in new_dataset
        return load_file(data, identifier=identifier, **kwargs)
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/dclab/rtdc_dataset/load.py", line 22, in load_file
        return fmt(path, identifier=identifier, **kwargs)
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/dclab/rtdc_dataset/fmt_hdf5.py", line 194, in __init__
        self._h5 = h5py.File(h5path, mode="r")
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/h5py/_hl/files.py", line 424, in __init__
        fid = make_fid(name, mode, userblock_size,
      File "/usr/lib/ckan/default/lib/python3.8/site-packages/h5py/_hl/files.py", line 190, in make_fid
        fid = h5f.open(name, flags, fapl=fapl)
      File "h5py/_objects.pyx", line 54, in h5py._objects.with_phil.wrapper
      File "h5py/_objects.pyx", line 55, in h5py._objects.with_phil.wrapper
      File "h5py/h5f.pyx", line 96, in h5py.h5f.open
    OSError: Unable to open file (unable to lock file, errno = 37, error message = 'No locks available')

  You have to disable file locking via the environment variable
  `HDF5_USE_FILE_LOCKING='FALSE'`. The most convenient fix is to add the line::

    export HDF5_USE_FILE_LOCKING='FALSE'

  to `/usr/lib/ckan/default/bin/activate`.

  Also, you will have to set the environment variable for all configuration
  files (uwsgi and worker jobs in  `/etc/supervisor/conf.d/*.conf`)::

    # put this before the "command=" option.
    environment=HDF5_USE_FILE_LOCKING=FALSE

  Just to be sure, you could also add this to `/etc/environment`::

    HDF5_USE_FILE_LOCKING="FALSE"

- If uploads to DCOR fail and you are getting these errors in the nginx logs::

    [crit] 983#983: *623 pwrite() "/var/lib/nginx/body/0000000001" failed (28: No space left on device)


  This means that your root partition does not have enough free space to
  cache uploaded files. A workaround is to move the data directly to the
  block storage on `/data`. Add this in the nginx configuration file
  (`server` section)::

    client_body_temp_path /data/tmp/nginx 1 2;

  and make sure that `www-data` has rw access to this directory.

- If your root partition is suddenly full, this might be due to the systemd
  journal in `/var/logs`. You can free up space by running::

    journalctl --vacuum-files=2

  To add a general limit on how large the journal may become, edit the
  file `/etc/systemd/journald.conf` and set::

    SystemMaxUse=200M

  It might also help to remove-purge the `snapd` package::

    apt purge snapd
    rm -rf /snap
    rm -rf /var/snap
    rm -rf /var/lib/snapd

- Problems wih `OSError: [Errno 28] No space left on device` upon uploads of
  large files. The reason might be that uwsgi stores temporary files in /tmp.
  You could check this with::

    (default) root@server:/# lsof / | grep "/tmp"
    uwsgi      1301         www-data    7u   REG   0,28 2038633555 1304952 /tmp/#1304952 (deleted)
    uwsgi      1301         www-data   12u   REG   0,28 1558086333 1304953 /tmp/#1304953 (deleted)

  You could also check whether your CKAN installation is responsible for this
  (`df -h` shows less space than there should be) by restarting all services::

    supervisorctl restart all

  According to a PDF file that I found somewhere, uwsgi always stores its
  temporary files under `/tmp`, a behavior that can be controlled via the
  environment variable `TMPDIR`. Thus, the solution is to edit the uwsgi
  supervisor file `/etc/supervisor/conf.d/ckan-uwsgi.conf` and set this
  `TPMDIR` to something under `/data`::

    environment=HDF5_USE_FILE_LOCKING=FALSE,TMPDIR=/data/tmp/uwsgi

- If downloads of large resources are aborted by the server after a short
  time, this might be because nginx caches the download on the root partition
  which does not have enough free space. You have to specify a cache location
  with sufficient free space in `/etc/nginx/sites-enabled/ckan` by uncommenting
  the line::

    proxy_temp_path /data/tmp/nginx/proxy 1 2;

- If uploads fail with a timeout error message and in the logs you get::

    OSError: timeout during read(57344) on wsgi.input
    2021-09-07 09:20:43 uWSGI 127.0.0.1 (HTTP/1.0 500) POST /api/3/action/resource_create => 0 bytes in 8644 msecs to DCOR-Aid/0.6.4

  that probably means that the socket-timeout value for uWSGI is too low.
  A reason for that could be e.g. that the resources are written to a location
  with low write speed (e.g. NFS). A solution is to add the socket-timeout to
  `/etc/ckan/default/ckan-uwsgi.ini`::

    socket-timeout     = 7200
