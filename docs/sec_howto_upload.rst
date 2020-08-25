======================
Uploading data to DCOR
======================

Data preparation with DCKit
===========================
In many cases, you should not upload your experimental data right away
to DCOR. There may be several reasons for that, such as missing metadata,
uncompressed raw data, or log files that contain sensitive or unnecessary
information (such as the user name of the person that recorded or processed
the raw data). Please also note that DCOR only works with DC data in the HDF5
file format (.rtdc file extension).

DCKit to the rescue! In most cases, it is sufficient to to run your data
through DCKit. Load the files in question, run the integrity check,
complete or correct any missing or bad metadata keys and either convert
the data to the .rtdc file format (for tdms data) or compress the data.
You can verify that everything went as intended by running the integrity
check for the newly generated files. If you are certain that you are not
losing valuable information, you may also use the repack and strip logs option.


Data upload with DCOR-Aid
=========================




Data upload via the web interface (not recommended)
===================================================
