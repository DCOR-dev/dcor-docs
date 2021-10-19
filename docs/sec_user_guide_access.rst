======================
Accessing Data on DCOR
======================

General remarks
===============
There are two ways of interacting with data on a DCOR instance,
via the web interface or via the API. With the web interface, you can
browse and search data in a convenient way with your webbrowser. The API
allows you to write custom scripts or libraries (DCOR-Aid uses the API).


Access via DCOR-Aid GUI
=======================
TODO


Access via DCOR-Aid Python library
==================================
The DCOR-Aid Python library provides you with a convenient interface
to the API. In principle, you are not limited to Python or DCOR-Aid,
as DCOR is basically `CKAN <https://ckan.readthedocs.io/>`_ and thus
uses the `same API <https://docs.ckan.org/en/2.9/api/index.html>`_.

To initiate a connection with DCOR, run:

.. ipython:: python

  import dcoraid
  api = dcoraid.CKANAPI(server="dcor-dev.mpl.mpg.de",
                        api_key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiItNUVsLVBTZVdfZ3hMM2tKNnZXS0hWZUdsN011SnpMRlFRMHluNzdUanZqRnhLX3VNLTQyUHhsbVQwRl9yOGlZbklOam9CN3E4emZITDA0TCIsImlhdCI6MTYzNDY1NTc1OH0.VfHEPXdEZKjCZOP4bO8cl0OiIxsvZZksWyQLl80UGbI")
  # check that everything works
  assert api.is_available()

Here, ``server`` is the DCOR instance you are connecting to and
``api_key`` is your personal access token that you need if you would like
to access private data. You can omit ``api_key`` if you are only interested
in public data (or if you don't have an account).

The ``dcoraid.CKANAPI`` class gives you full access to the `underlying
API <https://docs.ckan.org/en/2.9/api/index.html>`_. For instance, you could
list all details of
`this dataset <https://dcor-dev.mpl.mpg.de/dataset/figshare-7771184-v2>`_ with:

.. ipython:: python

  dataset_dict = api.get("package_show", id="figshare-7771184-v2")
  # the first ten entries of the dataset dictionary
  for key in list(dataset_dict.keys())[:10]:
    print(f"{key:18s}: {dataset_dict[key]}")
  # all resource names in the dataset
  print([r["name"] for r in dataset_dict["resources"]])
  # the first ten metadata entries of the first resource
  for key in list(dataset_dict["resources"][0].keys())[:10]:
    print(f"{key:31s}: {dataset_dict['resources'][0][key]}")

.. note::

  Beware of the `dataset ambiguity`: On DCOR, a dataset (or package)
  contains a number of resources. You would call one of those resources
  a dataset in dclab. In other words, on DCOR a dataset consists of multiple
  RT-DC files while with :func:`dclab.new_dataset` you always ever only open
  one resource.

Another very useful tool in DCOR-Aid is the ``APIInterrogator`` class
which sits on top of ``CKANAPI`` and, amongst other things, simplifies
searching for datasets:

.. ipython:: python

  # instantiate APIInterrogator
  air = dcoraid.APIInterrogator(api)
  # search for a dataset in a DCOR circle
  dbe = air.search_dataset(query="reference data",
                           circles=["figshare-import"])
  # the returned database extract (one hit)...
  len(dbe)
  # ...contains all metadata of the datasets matching the search query
  dbe[0]["name"]



Example: List all IDs of .rtdc resources for a DCOR circle
===========================================================
Let's say you are interested in all RT-DC data files in a DCOR circle,
because you would like to run an automated analysis with dclab.
The following script creates a list of IDs ``resource_ids`` with all RT-DC
files in the
`Figshare mirror <https://dcor.mpl.mpg.de/organization/figshare-import>`_
circle and plots one of the resources. For more information on how to
access DCOR data with dclab, please refer to the
:ref:`dclab docs <dclab:sec_av_dcor>`.

.. plot::

  import dclab
  import dcoraid
  import matplotlib.pylab as plt

  # name of the circle in question
  circle_name = "figshare-import"

  # initialize API (for private datasets, also provide `api_key`)
  api = dcoraid.CKANAPI("dcor.mpl.mpg.de")
  air = dcoraid.APIInterrogator(api)
  # get a list of all datasets for `circle_name`
  datasets = air.search_dataset(circles=[circle_name])
  # iterate over all datasets and populate our resources list
  resource_ids = []
  for ds_dict in datasets:
      # iterate over all resources of a dataset
      for res_dict in ds_dict["resources"]:
          # identify RT-DC data
          if res_dict["mimetype"] == "RT-DC":
              resource_ids.append(res_dict["id"])

  # do something with one of the resources in dclab
  with dclab.new_dataset(resource_ids[47]) as ds:
      kde = ds.get_kde_scatter(xax="area_um", yax="deform")
      ax = plt.subplot(111, title=ds.config['experiment']['sample'])
      sc = ax.scatter(ds["area_um"], ds["deform"], c=kde, marker=".")
      ax.set_xlabel(dclab.dfn.get_feature_label("area_um"))
      ax.set_ylabel(dclab.dfn.get_feature_label("deform"))
      plt.colorbar(sc, label="kernel density estimate [a.u]")
      plt.show()
