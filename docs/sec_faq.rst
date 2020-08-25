==========================
Frequently Asked Questions
==========================


How DCOR handles data
=====================
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
