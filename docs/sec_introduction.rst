============
Introduction
============

Background
==========
DC is a microfluidics-based imaging technique that provides a
high-throughput, high-dimensional, single-cell analysis. Measurement
rates reach 1000 cells per second. An image is recorded for each cell,
enabling cell charactererization based on its phenotype. Due to the
moderate microfluidic forces in the imaging channel, cells are deformed
which makes it possible to infer mechanical properties. In addition,
fluorescence information can be recorded, allowing a direct comparison
to flow cytometry measurements.

Since DC measurements are comparatively large (hundreds of MB to several GB),
the handling and/or backup of these data can become a problem, especially
for small research and diagnostics labs. The deformability cytometry open
repository (DCOR) offers a solution to this problem. Users can upload their
DC data, create collections, share with other users, and cite their data
in scientific publications. Furthermore, DCOR is designed to integrate with the
open-source analysis software `Shape-Out <https://shapeout2.readthedocs.io>`_;
with DCOR, data analysis only requires a network connection, the actual data
remain on the server.


DCOR is open and free
=====================
The official DCOR service at https://dcor.mpl.mpg.de is free of charge.
If you are not permitted (e.g. by data protection laws) to store your
data there, you can always set up your own DCOR instance. This process
is described in the :ref:`self-hosting section <selfhost>` and should
probably (depending on your storage and backup strategy) involve your
IT department. Please let us know if you are planning to set up your
own DCOR instance so we can advertise this. Also, please don't hesitate to
get into contact with us (e.g. issues and pull requests on GitHub) if you
feel like you are missing a specific feature or configuration option.
DCOR should be robust and user-friendly - let's improve it together!


Technology
==========
DCOR is based on `CKAN <https://docs.ckan.org/>`_, an online data managing
and publishing system. We provide a set of extensions and tools designed to
make the work with DC data easier. For instance, this includes a RESTful
service that allows Shape-Out to directly access DC resources without
downloading entire measurements
(`ckanext-dc_serve <https://github.com/DCOR-dev/ckanext-dc_serve>`_) or
previews of DC data on CKAN web interface
(`ckanext-dc_view <https://github.com/DCOR-dev/ckanext-dc_view>`_).
You can find all extensions and tools at the
`DCOR-dev GitHub organization <https://github.com/DCOR-dev>`_.
