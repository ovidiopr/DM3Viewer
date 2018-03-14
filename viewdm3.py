#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  viewdm3.py  --- Main file
#     This file is part of DM3Viewer, a simple PyQt application to
#      view DM3 files.
#
#  Copyright (C) 2018 Ovidio Peña Rodríguez <ovidio@bytesfall.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  This program is based on the example "embedding_in_qt4.py" available
#  at http://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html

'''
Created on Feb 05, 2018

@author: ovidio
'''

import os, platform
from PyQt4 import uic, QtCore, QtGui
from utils import version, Plot3D, Options, OptionsDlg

import DM3Viewer_rc


class DM3Viewer(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self)
        self.programDirPath = os.path.dirname(os.path.realpath(__file__))
        self.ui = uic.loadUi(os.path.join(self.programDirPath, 'DM3Viewer.ui'), self)

        self.setWindowTitle(version.__name__)

        self.optionsDlg = None

        # This  gets the settings from wherever they are stored (the storage place is platform dependent)
        self.settings = QtCore.QSettings()
        self.loadOptions()

        self.plot = Plot3D(self.plotQF, toolbar = False, cmap = self.options.colorMap)
        self.plot.scale_pos = self.options.scalePos

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.plot.nextFile)

        self.connect(self.action_Open_DM3, QtCore.SIGNAL("triggered()"), self.fileOpen)
        self.connect(self.action_Reload_DM3, QtCore.SIGNAL("triggered()"), self.plot.readFile)
        self.connect(self.action_Close_DM3, QtCore.SIGNAL("triggered()"), self.fileClose)

        self.connect(self.action_Export_Data, QtCore.SIGNAL("triggered()"), self.fileExportData)
        self.connect(self.action_Export_PNG, QtCore.SIGNAL("triggered()"), lambda: self.fileSaveAs(name='PNG', ext='png'))
        self.connect(self.action_Export_JPG, QtCore.SIGNAL("triggered()"), lambda: self.fileSaveAs(name='JPG', ext='jpg'))
        self.connect(self.action_Export_TIF, QtCore.SIGNAL("triggered()"), lambda: self.fileSaveAs(name='TIFF', ext='tif'))
        self.connect(self.action_Export_PDF, QtCore.SIGNAL("triggered()"), lambda: self.fileSaveAs(name='PDF', ext='pdf'))

        self.connect(self.action_Quit_Viewer, QtCore.SIGNAL("triggered()"), self.fileQuit)

        self.connect(self.action_First_Image, QtCore.SIGNAL("triggered()"), self.plot.firstFile)
        self.connect(self.action_Previous_Image, QtCore.SIGNAL("triggered()"), self.plot.previousFile)
        self.connect(self.action_Next_Image, QtCore.SIGNAL("triggered()"), self.plot.nextFile)
        self.connect(self.action_Last_Image, QtCore.SIGNAL("triggered()"), self.plot.lastFile)

        self.connect(self.action_Info, QtCore.SIGNAL("triggered()"), self.imageInfo)
        self.connect(self.action_FFT, QtCore.SIGNAL("triggered()"), self.switchFFT)

        self.connect(self.action_Options, QtCore.SIGNAL("triggered()"), self.onOptions)
        self.connect(self.action_Timer, QtCore.SIGNAL("triggered()"), self.timerInterval)

        self.connect(self.action_About, QtCore.SIGNAL("triggered()"), self.helpAbout)

        self.connect(self.plot, QtCore.SIGNAL("coordsChanged"), self.setPlotCoords)

        self.connect(self.plot, QtCore.SIGNAL("dataChanged()"), self.onDataChanged)

        # Restore last session state for the main window
        self.resize(self.settings.value("MainWindow/Size", QtCore.QVariant(QtCore.QSize(800, 600))).toSize())
        self.move(self.settings.value("MainWindow/Position", QtCore.QVariant(QtCore.QPoint(0, 0))).toPoint())
        self.restoreState(self.settings.value("MainWindow/State").toByteArray())

        # Launch low-priority initializations (to speed up load time)
        QtCore.QTimer.singleShot(0, self.createLoadFileDlg) # Create the Load DM3 File dialog

        self.updateControls()

    def onDataChanged(self):
        self.updateControls()
        self.setTitle()

    def setTitle(self):
        if os.path.exists(self.plot.fname):
            self.setWindowTitle('DM3 Viewer - ' + os.path.basename(self.plot.fname))
        else:
            self.setWindowTitle('DM3 Viewer')

    def updateControls(self):
        '''Update the state of the controls (Enabled|Disabled)'''
        self.action_Close_DM3.setEnabled(self.plot.valid_source)
        self.action_Reload_DM3.setEnabled(self.plot.valid_source)

        self.action_Export_Data.setEnabled(self.plot.valid_source and not self.plot.data_is_spectra)
        self.action_Export_PNG.setEnabled(self.plot.valid_source and not self.plot.data_is_spectra)
        self.action_Export_JPG.setEnabled(self.plot.valid_source and not self.plot.data_is_spectra)
        self.action_Export_TIF.setEnabled(self.plot.valid_source and not self.plot.data_is_spectra)
        self.action_Export_PDF.setEnabled(self.plot.valid_source and not self.plot.data_is_spectra)

        self.action_First_Image.setEnabled(self.plot.valid_source)
        self.action_Previous_Image.setEnabled(self.plot.valid_source)
        self.action_Next_Image.setEnabled(self.plot.valid_source)
        self.action_Last_Image.setEnabled(self.plot.valid_source)

        self.action_Info.setEnabled(self.plot.valid_data)
        self.action_FFT.setEnabled(self.plot.valid_data and not self.plot.data_is_spectra)
        if self.plot.data_is_fft:
            self.action_FFT.setIcon(QtGui.QIcon(':/Icons/ifft.svg'))
            self.action_FFT.setIconText('IFFT')
            self.action_FFT.setToolTip('Inverse Fast Fourier Transform')
            self.action_FFT.setStatusTip('Calculate the Inverse Fast Fourier Transform of the current DM3 file')
        else:
            self.action_FFT.setIcon(QtGui.QIcon(':/Icons/fft.svg'))
            self.action_FFT.setIconText('FFT')
            self.action_FFT.setToolTip('Fast Fourier Transform')
            self.action_FFT.setStatusTip('Calculate the Fast Fourier Transform of the current DM3 file')
        self.action_FFT.setChecked(self.plot.switch_fft)

        self.action_Timer.setEnabled(self.plot.valid_data)

    def setPlotCoords(self, coords = None):
        if coords is None:
            self.statusbar.showMessage("")
        elif len(coords) == 1:
            self.statusbar.showMessage("x = %.5g" % (coords))
        elif len(coords) == 2:
            self.statusbar.showMessage("x = %.5g, y = %.5g" % (coords))
        elif len(coords) == 3:
            self.statusbar.showMessage("x = %.5g, y = %.5g, z = %.5g" % (coords))
        else:
            self.statusbar.showMessage("")

    def loadOptions(self):
        '''create the self.options object from values stored in the settings'''
        self.options = Options()
        for opt, dflt in zip(self.options.optlist, self.options.dfltlist):
            if isinstance(dflt, (str, unicode)):
                setattr(self.options, opt, unicode(self.settings.value('Options/' + opt, QtCore.QVariant(QtCore.QString(dflt))).toString()))
            elif isinstance(dflt, float):
                setattr(self.options, opt, self.settings.value('Options/' + opt, QtCore.QVariant(dflt)).toDouble()[0])
            elif isinstance(dflt, bool):
                setattr(self.options, opt, self.settings.value('Options/' + opt, QtCore.QVariant(dflt)).toBool())
            elif isinstance(dflt, int):
                setattr(self.options, opt, self.settings.value('Options/' + opt, QtCore.QVariant(dflt)).toInt()[0])
            else:
                raise ValueError('Unsupported type in option "%s"' % dflt)

    def createLoadDlg(self, title, filters, selectedFilter, activeDir):
        # General Load Dialog
        dlg = QtGui.QFileDialog(self, title, "./", "")
        dlg.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dlg.setViewMode(QtGui.QFileDialog.Detail)

        dlg.setFilters(filters)
        dlg.setDirectory(activeDir)
        dlg.selectFilter(selectedFilter)

        return dlg

    def createLoadFileDlg(self):
        # Load DM3 File Dialog (it is never closed, just hidden)
        title = "%s - Load DM3 File" % QtGui.QApplication.applicationName()
        filters = ["DM3 Files (*.dm3)", "All Files (*.*)"]
        selectedFilter = self.settings.value("LoadFileFilter", QtCore.QVariant(QtCore.QString(filters[0]))).toString()
        activeDir = self.options.workDirectory

        self.loadFileDlg = self.createLoadDlg(title, filters, selectedFilter, activeDir)

    def fileOpen(self):
        self.loadFileDlg.setDirectory(self.options.workDirectory)
        if self.loadFileDlg.exec_():
            self.options.workDirectory = self.loadFileDlg.directory().path() #update the working directory
            self.settings.setValue("Options/workDirectory", QtCore.QVariant(self.options.workDirectory)) #save the new working directory
            fileNames = [unicode(item) for item in self.loadFileDlg.selectedFiles()]

            self.plot.fname = fileNames[-1]
            self.setTitle()

    def fileClose(self):
        result = QtGui.QMessageBox.question(self, "Close '%s'" % (os.path.basename(self.plot.fname)),
                                            "Are you sure that you want to close the image '%s'?" % (os.path.basename(self.plot.fname)),
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if (result == QtGui.QMessageBox.Yes):
            self.plot.clearPlot()
            self.setTitle()

    def fileSaveAs(self, name = 'PNG', ext = 'png'):
        if os.path.exists(self.plot.fname):
            dir = "%s.%s" % (os.path.splitext(self.plot.fname)[0], ext)
        else:
            dir = self.options.workDirectory

        fname = QtGui.QFileDialog.getSaveFileName(self, "Select File Name", dir, "%s files (*.%s)" % (name, ext))
        if fname:
            self.options.workDirectory = os.path.dirname(unicode(fname)) #update the working directory
            self.settings.setValue("Options/workDirectory", QtCore.QVariant(self.options.workDirectory)) #save the new working directory
            self.plot.writeFile(unicode(fname), zoom = self.options.zoom)

    def fileExportData(self):
        if os.path.exists(self.plot.fname):
            dir = "%s.%s" % (os.path.splitext(self.plot.fname)[0], 'dat')
        else:
            dir = self.options.workDirectory

        fname = QtGui.QFileDialog.getSaveFileName(self, "Select File Name", dir, "Data Files (*.dat)")
        if fname:
            self.options.workDirectory = os.path.dirname(unicode(fname)) #update the working directory
            self.settings.setValue("Options/workDirectory", QtCore.QVariant(self.options.workDirectory)) #save the new working directory

            import numpy as np

            data = self.plot.getData().copy()

            if self.options.zoom != 1.0: # Resize only if necessary
                from scipy.ndimage import zoom

                data = zoom(data, zoom=self.options.zoom, order=3)

            vmin = min(self.plot.dm3.cuts)
            vmax = max(self.plot.dm3.cuts)

            # Restrict values
            data[np.where(data <= vmin)] = float(vmin)
            data[np.where(data >= vmax)] = float(vmax)

            # Normalize data, scaling to 0-65535, to convert to 16-bit integer
            #data = np.uint16(np.round(65535*(data - vmin)/(vmax - vmin)))
            # Normalize data, scaling to 0-255, to convert to 8-bit integer
            data = np.uint8(np.round(255*(data - vmin)/(vmax - vmin)))

            np.savetxt(unicode(fname), data.astype(int), fmt='%i')

            # Save scale info
            np.savetxt("%s.info" % (os.path.splitext(unicode(fname))[0]), np.array((self.plot.getDataWidth(), self.plot.getDataHeight())), fmt='%.3f')

    def fileQuit(self):
        #result = QtGui.QMessageBox.question(self, "Quit %s" % (version.__name__),
        #                                    "Are you sure that you want to quit %s?" % (version.__name__),
        #                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        #if (result == QtGui.QMessageBox.Yes):
        self.close()

    def onOptions(self):
        '''Shows the options dialog and saves any changes if accepted'''
        if self.optionsDlg is None: self.optionsDlg = OptionsDlg(self) #create the dialog if not already done

        # Make sure that the Dlg is in sync with the options
        self.optionsDlg.setOptions(self.options)
        # Launch the options dialog
        if self.optionsDlg.exec_():
            self.options = self.optionsDlg.getOptions() #get the options from the dialog
            if self.options.scalePos != self.plot.scale_pos:
                self.plot.scale_pos = self.options.scalePos
            if self.options.colorMap != self.plot.cmap:
                self.plot.cmap = self.options.colorMap
        else:
            self.optionsDlg.setOptions(self.options) #reset previous options

    def setUpdateInterval(self):
        if self.options.timeInterval > 0:
            self.timer.start(self.options.timeInterval)
        else:
            self.timer.stop()

    def timerInterval(self):
        interval, ok = QtGui.QInputDialog.getDouble(self, 'Update interval', 'Update interval (s):', self.options.timeInterval/1000.0, 0)
        if ok:
            self.options.timeInterval = 1000.0*interval
            self.setUpdateInterval()

    def imageInfo(self):
        info = self.plot.dm3.info
        infoKeys = ('descrip', 'acq_date', 'acq_time', 'name', 'micro', 'hv', 'mag', 'mode','operator', 'specimen')
        infoDesc = ('Description', 'Acquisition Date', 'Acquisition Time', 'Microscope Name', 'Microscope', 'Voltage', 'Magnification', 'Operation Mode','Operator', 'Specimen')
        infoSuff = ('', '', '', '', '', ' V', ' X', '','', '')

        infoStr = ""
        for i, key in enumerate(infoKeys):
            if info.has_key(key):
                infoStr += "<p><b>%s</b>: %s%s</p>" % (infoDesc[i], info[key], infoSuff[i])

        shape = self.plot.data.shape
        shape_str = '%i' % shape[0]
        (origin, scale, units) = self.plot.dm3.axisunits(0)
        size_str = '%.4g %s' % (shape[0]*scale, units)
        for i in range(1, len(shape)):
            shape_str = '%sx%i' % (shape_str, shape[i])
            (origin, scale, units) = self.plot.dm3.axisunits(i)
            size_str = '%s x %.4g %s' % (size_str, shape[i]*scale, units)
        (zo, zf) = self.plot.dm3.cuts

        QtGui.QMessageBox.information(self, "Image Info...",
                                """<p><b>File Name</b>: %s</p>
                                <p><b>Size</b>: %s px</p>
                                <p><b>Dimensions</b>: %s</p>
                                <p><b>Scale</b>: %.3g %s/px</p>
                                <p><b>Contrast Limits</b>: %i - %i</p>
                                %s""" % (os.path.basename(self.plot.fname), shape_str,
                                size_str, scale, units, zo, zf, infoStr))

    def switchFFT(self):
        self.plot.switch_fft = self.action_FFT.isChecked()

    def helpAbout(self):
        from scipy import __version__ as scipy_version
        from numpy import __version__ as numpy_version
        from matplotlib import __version__ as mpl_version

        QtGui.QMessageBox.about(self, "About %s" % (version.__name__),
                                """<b>%s</b> v%s
                                <p>Copyright &copy; 2018 Ovidio Y. Pe&ntilde;a Rodr&iacute;guez <ovidio.pena [AT] upm.es></p>
                                <p></p>
                                <p>Home page: <a href='%s'>%s</a></p>
                                <p></p>
                                <p>Python %s - Qt %s - PyQt %s on %s</p>
                                <p>Numpy %s - Scipy %s - Matplotlib %s</p>""" % (version.__name__,
                                version.__version__, version.__url__, version.__url__, platform.python_version(),
                                QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, platform.system(),
                                numpy_version, scipy_version, mpl_version))

    def closeEvent(self, event):
        '''This event handler receives widget close events'''
        #if not self.structureIsSaved():
        #    event.ignore()
        #    return

        # Store the options as settings
        for opt in self.options.optlist:
            val = getattr(self.options, opt)
            if isinstance(val, (str, unicode)): val = QtCore.QString(val) #convert python strings to QStrings
            self.settings.setValue("Options/" + opt, QtCore.QVariant(val))

        # Save main window state before closing
        self.settings.setValue("MainWindow/Size", QtCore.QVariant(self.size()))
        self.settings.setValue("MainWindow/Position", QtCore.QVariant(self.pos()))
        self.settings.setValue("MainWindow/State", QtCore.QVariant(self.saveState()))

        self.settings.setValue("LoadFileFilter", QtCore.QVariant(self.loadFileDlg.selectedFilter()))


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(version.__name__)
    app.setApplicationVersion(version.__version__)
    app.setOrganizationName(version.__company__)

    form = DM3Viewer()
    form.show()

    sys.exit(app.exec_())
