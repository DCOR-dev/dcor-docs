"""Screenshots for Uploads (DCKit)"""
import pathlib
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from dcoraid.gui import DCORAid
from dcoraid.gui.wizard import SetupWizard

sys.path.insert(0, "..")

import upload_task_generation as utg


data_path = pathlib.Path(__file__).resolve().parent / ".." / ".." / "data"

app = QApplication(sys.argv)

QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.C))

# screenshot of upload tab
mw = DCORAid()
mw.tabWidget.setCurrentIndex(3)
time.sleep(1)  # give it time to show the user name
# add an upload job
path_task = data_path.resolve() / "upload_job.dcoraid-task"
if path_task.exists():
    path_task.unlink()
utg.DATASET_TEMPLATE_DICT["owner_org"] = "dcoraid-circle"
utg.generate_task_file(data_path)
mw.panel_upload.on_upload_task(path_task)
time.sleep(1)
app.processEvents(QtCore.QEventLoop.AllEvents, 300)
mw.grab().save("_upload_dcoraid_init.png")
if path_task.exists():
    path_task.unlink()

# screenshot of setup wizard
wiz = SetupWizard(mw)
wiz.show()
app.processEvents(QtCore.QEventLoop.AllEvents, 300)
wiz.grab().save("_upload_dcoraid_wizard.png")
