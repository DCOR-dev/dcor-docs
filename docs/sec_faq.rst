==========================
Frequently Asked Questions
==========================


.. _sec_faq_upload_test:

Can I upload a test dataset somewhere?
======================================
For all testing (or development) purposes, you can use the development
instance at https://dcor-dev.mpl.mpg.de. All datasets on that server are
purged on a regular basis, so feel free to play with it as you see fit.


.. _sec_faq_upload_background:

What happens in the background when I upload a dataset?
=======================================================
For every DC file that you upload, DCOR performs the following tasks in
the background:

- Generate a condensed version of the original data. This computationally
  expensive task is necessary to provide fast access to ancillary features,
  such as volume or principal inertia ratio, to Shape-Out 2 or dclab via the
  DCOR API. It also allows you to only upload the data you actually recorded
  (without any disadvantages).
- Generate a preview image and extract the configuration for visualization
  of the data in the web interface.
- The original file you uploaded is not changed. You can verify that the
  uploaded file is identical to the original file on your hard disk by
  comparing their sha256 sums. The sha256 sum is listed on each resource
  page under Additional Information.

Please note that, due to this data processing, it may take a few minutes
until the preview is visible and the ancillary features are available via
the DCOR API. 


.. _sec_faq_dataset_not_editable:

Why can't I add resources to existing datasets?
===============================================
Not being able to modify a finalized dataset is part of the design of DCOR.
The idea behind this design choice is that any user who uses a dataset
(e.g. for a publication) will always work with the same resources. If you would
be able to add resources (or even replace them), then this would
impair reproducibility (or at least make things intransparent).

When you upload several resources in a dataset via DCOR-Aid, the DCOR-Aid
first creates a *draft* dataset. When a dataset is a *draft*, resources
may be uploaded and metadata may be edited. After the upload is complete,
DCOR-Aid sets the state of the dataset (irreversibly) to *active*. In the
active state, only the following actions are allowed:

1. setting the visibility of a private dataset to public
2. changing the license of a dataset to a less restrictive one
