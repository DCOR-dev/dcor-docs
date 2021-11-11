"""Screenshots for Uploads (DCKit)"""
import pathlib
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from dckit.main import DCKit

data_path = pathlib.Path(__file__).resolve().parent / ".." / ".." / "data"

app = QApplication(sys.argv)

QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.C))

mw = DCKit()
mw.append_paths([data_path / "calibration_beads_47.rtdc"])
mw.on_task_integrity_all()

app.processEvents(QtCore.QEventLoop.AllEvents, 300)
mw.grab().save("_upload_dckit_preproc.png")
