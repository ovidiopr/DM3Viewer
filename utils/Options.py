#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Options.py  --- Configuration of program options
#     This file is part of DM3Viewer, a simple PyQt application to
#      view and export DM3 files.
#
#  Copyright (C) 2018-2023 Ovidio Peña Rodríguez <ovidio@bytesfall.com>
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

from PyQt5 import uic,  QtCore, QtGui, QtWidgets
import os

ColorMaps = ('gray', 'hot', 'gist_earth', 'terrain', 'ocean', 'brg', 'jet', 'rainbow', 'hsv')
ColorMapsLbl = {'gray': 'Gray',
                'hot': 'Hot',
                'gist_earth': 'Earth',
                'terrain': 'Terrain',
                'ocean': 'Ocean',
                'brg': 'BRG',
                'jet': 'Jet',
                'rainbow': 'Rainbow',
                'hsv': 'HSV'}

class Options(object):
    def __init__(self):
        #variables and default values
        self.optlist = ['workDirectory', 'timeInterval', 'zoom', 'colorMap', 'scalePos']
        self.dfltlist = [QtCore.QDir.currentPath().encode('utf-8'), 0.0, 1.0, 'gray', 3]
        self.reset()

    def reset(self):
        for opt, dflt in zip(self.optlist, self.dfltlist): setattr(self, opt, dflt)

class OptionsDlg(QtWidgets.QDialog):
    '''Dialog containing options for DM3Viewer. The options are members of this object.'''
    def __init__(self, parent = None):
        super(OptionsDlg, self).__init__(parent)
        self.ui = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Options.ui'), self)

        #set validators
        self.timeIntLE.setValidator(QtGui.QDoubleValidator(self))

        #connections
        self.connect(self.workDirectoryPB, QtCore.SIGNAL("clicked()"), self.onChangeWorkDirectory)
        self.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton *)"), self.onclicked)

        self.connect(self.zoomHS, QtCore.SIGNAL("valueChanged(int)"), self.updateZoomLbl)
        #self.connect(self.zoomHS, QtCore.SIGNAL("sliderMoved(int)"), self.updateZoomLbl)

        #update list of color maps
        self.colorMapCB.clear()
        for cm in ColorMaps:
            self.colorMapCB.addItem(ColorMapsLbl[cm])

        #create colormaps
        from numpy import linspace, vstack
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

        fig, axes = plt.subplots(nrows = len(ColorMaps))
        fig.subplots_adjust(top = 0.99, bottom = 0.01, left = 0.2, right = 0.99)
        canvas = FigureCanvas(fig)
        canvas.setParent(self.colorMapsQF)

        gradient = linspace(0, 1, 256)
        gradient = vstack((gradient, gradient))

        for ax, name in zip(axes, ColorMaps):
            ax.imshow(gradient, aspect = 'auto', cmap = plt.get_cmap(name))
            pos = list(ax.get_position().bounds)
            x_text = pos[0] - 0.01
            y_text = pos[1] + pos[3]/2.
            fig.text(x_text, y_text, ColorMapsLbl[name], va = 'center', ha = 'right', fontsize = 11)

        #turn off all ticks & spines
        for ax in axes:
            ax.set_axis_off()

        #define layout for colormaps
        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(canvas)
        self.colorMapsQF.setLayout(vlayout)

        #set options
        self.reset()

    def onChangeWorkDirectory(self):
        filename = QtGui.QFileDialog.getExistingDirectory(self, "Select working directory", self.workDirectoryLE.text())
        if filename: self.workDirectoryLE.setText(filename)

    def onclicked(self, button):
        if self.buttonBox.buttonRole(button) == QtGui.QDialogButtonBox.ResetRole:
            self.reset()

    def reset(self):
        self.setOptions(Options())

    def getOptions(self):
        '''returns an options object filled with values from the dialog'''
        options = Options()
        #GENERAL
        options.workDirectory = self.workDirectoryLE.text().encode('utf-8')
        options.timeInterval = float(self.timeIntLE.text())
        #PLOT
        options.zoom = self.getZoom(self.zoomHS.value())
        options.colorMap = ColorMaps[self.colorMapCB.currentIndex()]
        options.scalePos = self.scalePosCB.currentIndex()

        return options

    def setOptions(self, options):
        '''set dialog values from the passed options object'''
        #GENERAL
        self.workDirectoryLE.setText(options.workDirectory)
        self.timeIntLE.setText(str(options.timeInterval))
        #PLOT
        self.zoomHS.setValue(self.getSliderValue(options.zoom))
        self.colorMapCB.setCurrentIndex(ColorMaps.index(options.colorMap))
        self.scalePosCB.setCurrentIndex(options.scalePos)

    def getSliderValue(self, zoom=0.0):
        if zoom >= 1.0:
            return int(zoom - 1)
        else:
            return int(1.0 - 1.0/zoom)

    def getZoom(self, value=0):
        if value >= 0:
            return value  + 1.0
        else:
            return 1.0/(abs(value)  + 1.0)

    def updateZoomLbl(self, value=0):
        if value == 0:
            self.zoomLbl.setText('1:1')
        elif value > 0:
            self.zoomLbl.setText('1:%i' % (value + 1))
        else: # value < 0
            self.zoomLbl.setText('%i:1' % (1 - value))
            

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = OptionsDlg(None)
    form.show()
    sys.exit(app.exec_())
