"""Screenshots for Find Data"""
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from dcoraid.gui import DCORAid


app = QApplication(sys.argv)

QtCore.QLocale.setDefault(QtCore.QLocale(QtCore.QLocale.C))

# screenshot of Find Data tab
mw = DCORAid()
mw.tabWidget.setCurrentIndex(0)
mw.lineEdit_public_search.setText("reference data")
mw.on_public_search()
mw.public_filter_chain.fw_datasets.tableWidget.setCurrentCell(0, 0)
time.sleep(1)

app.processEvents(QtCore.QEventLoop.AllEvents, 300)
mw.grab().save("_access_dcoraid_init.png")
