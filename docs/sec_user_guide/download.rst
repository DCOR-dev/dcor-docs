.. _sec_user_guide_download:

================
Downloading data
================

If you need to download instead of :ref:`accessing <sec_user_guide_access>`
the data, you have multiple options.


Downloading with the DCOR-Aid GUI
=================================
This easiest way to download data from DCOR is via the DCOR-Aid user
interface (`download installers here <https://github.com/DCOR-dev/DCOR-Aid/releases/latest>`_
or install with ``pip install dcoraid[GUI]`` and execute ``dcoraid``).
You can choose between downloading public data (no user
account required) or private data (uploaded by your user account or shared
with your user account). DCOR-Aid automatically verifies downloads
with SHA256 checksums.


Downloading with a Python script using dcoraid
==============================================
In cases where you have to script downloads, you can use the ``dcoraid``
Python library. First, install the library with::

    pip install dcoraid

If you wanted to download all resources of a dataset, you could proceed
as follows (exemplary dataset ID ``400ae3d4-9f8a-44f8-887d-1e4f6150deee``):

.. code-block:: python

    import time
    from dcoraid.api import CKANAPI
    from dcoraid.download.queue import DownloadQueue

    download_path = r"D:\\Data"

    api = CKANAPI("https://dcor.mpl.mpg.de")

    ds_dict = api.get("package_show",
                      id="400ae3d4-9f8a-44f8-887d-1e4f6150deee")

    dq = DownloadQueue(api)
    for res in ds_dict["resources"]:
        dq.new_job(resource_id=res["id"],
                   download_path=download_path
                   )

    # Wait until all jobs have finished downloading
    while True:
        for job in dq.jobs:
            if job.state != "done":
                print(f"Downloading {job.path} ({job.get_rate_string()})", end="\r")
                time.sleep(1)
                break
        else:
            break


Downloading with a bash script
==============================
You do not need to have Python installed to download files from DCOR.
This bash script generates a list of links that you can download with
e.g. ``ẁget`` (see below) or a download manager of your choice.

.. code-block:: bash

   # fetch the package metadata JSON
   PKG_DATA=$(curl https://dcor.mpl.mpg.de/api/3/action/package_show?id=400ae3d4-9f8a-44f8-887d-1e4f6150deee)
   # extract the resource URLs from the JSON metadata
   echo $PKG_DATA | jq -r '.result.resources[].url'

The output of the above script is::

   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/57afdb68-f80e-40ac-bdff-8266135feaa3/download/250209_blood_2025-02-09_09.46_m003_reference.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/8d8a1b47-f24a-4d91-85f6-0160dea0226d/download/250209_blood_2025-02-09_09.46_m003_reference_dcn.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/de319c9c-8d4a-4e17-9ae1-4d57a42f4508/download/250209_blood_2025-02-09_09.46_m003_reference_30000.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/1d69f1de-17b3-454a-9c9e-98a962c0606b/download/250209_blood_2025-02-09_09.46_m003_reference_30000_dcn.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/1b2224f6-1fd0-4b7f-a9e2-cc4f376c900d/download/250209_blood_2025-02-09_09.46_m003_reference_5000.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/3efb60c0-0212-43a7-bdd5-030487471ce8/download/250209_blood_2025-02-09_09.46_m003_reference_5000_dcn.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/57ecde5d-f896-4599-ba35-d1be7defc6fe/download/250209_blood_2025-02-09_09.46_m003_reference_dcn_export_28.rtdc
   https://dcor.mpl.mpg.de/dataset/400ae3d4-9f8a-44f8-887d-1e4f6150deee/resource/a233aaf8-9998-4c44-8070-20fdba7cf3b2/download/250209_blood_2025-02-09_09.46_m003_reference_dcn_export_28_minimal.rtdc


.. note::

   You have to manually verify the SHA256 checksums of the downloaded files using the
   ``sha256sum`` tool. You can obtain the checksums with:

   .. code-block:: bash

       echo $PKG_DATA | jq -r '.result.resources[].sha256'


Downloading data with ``wget``
==============================

If you would like to download datasets, you can access it using the following URL

.. code::

   wget https://${SERVER}/dataset/${DATASET_ID}/resource/${RESOURCE_ID}/download/${RESOURCE_NAME}

For private datasets, you would have to pass your API token

.. code::

   wget --header="Authorization: ${YOUR_API_KEY}" https://${SERVER}/dataset/${DATASET_ID}/resource/${RESOURCE_ID}/download/${RESOURCE_NAME}

Example:

.. code::

   wget https://dcor.mpl.mpg.de/dataset/89bf2177-ffeb-9893-83cc-b619fc2f6663/resource/fb719fb2-bd9f-817a-7d70-f4002af916f0/download/calibration_beads.rtdc
