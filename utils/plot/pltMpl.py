# -*- coding: UTF-8 -*-
#
#  plot.py  --- Plotting functionalities
#     This file is part of DM3Viewer, a simple PyQt application to
#      view and export DM3 files.
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
#  This script is based on the example "embedding_in_qt4.py" available
#  at http://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html

'''
Created on Feb 05, 2018

@author: ovidio
'''

import os

from PyQt4 import QtCore, QtGui

import numpy as np

import matplotlib
matplotlib.use("Qt4Agg")
matplotlib.rcParams["backend.qt4"] = "PyQt4"
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize
from matplotlib.image import AxesImage
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

slider_max = 1000.0
slider_interval = 50


def save_image(fname, data, size=(1, 1), dpi=80, cmap='hot', scale_pos=3, zrange=None, scale=1.0, units='nm'):
    if zrange is None:
        zrange = (np.amin(data), np.amax(data))
    fig = plt.figure()
    fig.set_size_inches(size)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.set_cmap(cmap)
    ax.imshow(data, aspect='equal', vmin=zrange[0], vmax=zrange[1], extent = (0., scale, 0., scale))

    if 0 < scale_pos <= 10:
        scale_units = units
        scale_conv = 1.0
        scale_value = 10**np.floor(np.log10(np.max(scale)/4))
        scale_value = scale_value*np.floor(np.max(scale)/4/scale_value)
        if scale_value < 1:
            if scale_units == "nm":
                scale_units = r"$\AA$"
                scale_conv = 10.0
                scale_value = 10**np.floor(np.log10(scale_conv*np.max(scale)/4))
                scale_value = scale_value*np.floor(scale_conv*np.max(scale)/4/scale_value)
            elif scale_units == u'\xb5m':
                scale_units = "nm"
                scale_conv = 1000.0
                scale_value = 10**np.floor(np.log10(scale_conv*np.max(scale)/4))
                scale_value = scale_value*np.floor(scale_conv*np.max(scale)/4/scale_value)

        if scale_value < 1 or np.isnan(scale_value):
            scale_units = units
            scale_conv = 1.0
            scale_value = 1

        scalebar = AnchoredSizeBar(ax.transData, scale_value/scale_conv, '%i %s' % (scale_value, scale_units),
                                   loc=scale_pos, color='black', frameon=True, label_top=True,
                                   size_vertical=scale_value/scale_conv/10.0, pad=0.2, borderpad=0.5)

        ax.add_artist(scalebar)

    plt.savefig(fname, dpi=dpi)


class Mpl3DPlot(FigureCanvas):
    dataChanged = QtCore.pyqtSignal()
    coordsChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, parent = None, width = 8.0, height = 6.0, dpi = 150, toolbar = True, cmap = 'gray', scale_pos = 3):
        self._fig = Figure(figsize = (width, height), dpi = dpi)
        FigureCanvas.__init__(self, self._fig)
        self.setParent(parent)

        self._axes = self._fig.add_subplot(111, aspect = 'auto', position=[0.0, 0.0, 1.0, 1.0])

        if toolbar:
            self._toolbar = NavigationToolbar(self, parent)
        else:
            self._toolbar = None

        self._cmap = cmap
        self._scale_pos = scale_pos

        self.parent = parent
        if self.parent is not None:
            self._min_lbl = QtGui.QLabel(parent = self.parent)
            self._min_lbl.setAlignment(QtCore.Qt.AlignHCenter)
            self._min_lbl.setText('{:.4g}'.format(0))

            self._max_lbl = QtGui.QLabel(parent = self.parent)
            self._max_lbl.setAlignment(QtCore.Qt.AlignHCenter)
            self._max_lbl.setText('{:.4g}'.format(1))

            self._idx_lbl = QtGui.QLabel(parent = self.parent)
            self._idx_lbl.setAlignment(QtCore.Qt.AlignRight)
            self._idx_lbl.setText('Index:')

            self._idx_val = QtGui.QLabel(parent = self.parent)
            self._idx_val.setAlignment(QtCore.Qt.AlignLeft)
            self._idx_val.setText('0, 0')

            self._min_slider = QtGui.QSlider(QtCore.Qt.Vertical, parent = self.parent)
            self._min_slider.setTickPosition(QtGui.QSlider.TicksLeft)
            self._min_slider.setRange(0, int(slider_max))
            self._min_slider.setTickInterval(slider_interval)
            self._min_slider.setValue(0)
            self._min_slider.setTracking(False)
            self._min_slider.setFocusPolicy(QtCore.Qt.NoFocus)

            self._max_slider = QtGui.QSlider(QtCore.Qt.Vertical, parent = self.parent)
            self._max_slider.setTickPosition(QtGui.QSlider.TicksLeft)
            self._max_slider.setRange(0, int(slider_max))
            self._max_slider.setTickInterval(slider_interval)
            self._max_slider.setValue(int(slider_max))
            self._max_slider.setTracking(False)
            self._max_slider.setFocusPolicy(QtCore.Qt.NoFocus)

            self._idx_slider = QtGui.QSlider(QtCore.Qt.Horizontal, parent = self.parent)
            self._idx_slider.setTickPosition(QtGui.QSlider.TicksBelow)
            self._idx_slider.setRange(0, 0)
            self._idx_slider.setTickInterval(1)
            self._idx_slider.setValue(0)
            self._idx_slider.setTracking(False)
            self._idx_slider.setFocusPolicy(QtCore.Qt.NoFocus)

            self.connect(self._min_slider, QtCore.SIGNAL("valueChanged(int)"), lambda value: self.min_changed(value))
            self.connect(self._max_slider, QtCore.SIGNAL("valueChanged(int)"), lambda value: self.max_changed(value))
            self.connect(self._idx_slider, QtCore.SIGNAL("valueChanged(int)"), lambda value: self.idx_changed(value))

            self.connect(self._min_slider, QtCore.SIGNAL("sliderMoved(int)"),
                         lambda value: self._min_lbl.setText('{:.4g}'.format(self.zmin + value*(self.zmax - self.zmin)/slider_max)))
            self.connect(self._max_slider, QtCore.SIGNAL("sliderMoved(int)"),
                         lambda value: self._max_lbl.setText('{:.4g}'.format(self.zmin + value*(self.zmax - self.zmin)/slider_max)))
            self.connect(self._idx_slider, QtCore.SIGNAL("sliderMoved(int)"),
                         lambda value: self._idx_val.setText('%i, %i' % (value % self.data_width, (value//self.data_width) % self.data_height)))

            glayout = QtGui.QGridLayout()
            glayout.addWidget(self, 0, 0, 3, 2)
            glayout.addWidget(self._min_lbl, 2, 2, 1, 2)
            glayout.addWidget(self._max_lbl, 0, 2, 1, 2)
            glayout.addWidget(self._min_slider, 1, 2)
            glayout.addWidget(self._max_slider, 1, 3)
            glayout.addWidget(self._idx_lbl, 3, 0)
            glayout.addWidget(self._idx_val, 3, 2, 1, 2)
            glayout.addWidget(self._idx_slider, 3, 1)

            if toolbar:
                glayout.addWidget(self._toolbar, 3, 0, 4, 1)
            self.parent.setLayout(glayout)

        self.clearPlot()

        # Connect to the mouse events
        self.connect_events()

    def min_changed(self, value):
        self.updateColorMap(min_value=value)
        self._min_lbl.setText('{:.4g}'.format(self.zmin + value*(self.zmax - self.zmin)/slider_max))

    def max_changed(self, value):
        self.updateColorMap(max_value=value)
        self._max_lbl.setText('{:.4g}'.format(self.zmin + value*(self.zmax - self.zmin)/slider_max))

    def idx_changed(self, value):
        self.plot3Ddata()
        i = value % self.data_width if self.data_width > 0 else 0
        j = (value//self.data_width) % self.data_height if (self.data_width > 0) and (self.data_height > 0) else 0
        self._idx_val.setText('%i, %i' % (i, j))

    def clearPlot(self):
        self._axes.clear()
        self._axes.set_axis_off()

        if hasattr(self, '_curve'):
            del(self._curve)

        if hasattr(self, '_im'):
            del(self._im)
        self._im = None

        self._fig.canvas.draw()

        self._fname = ''
        self._dm3 = None
        self._data = None
        self._fdata = None
        self._switch_fft = False
        (self._origin_x, self._scale_x, self._units_x) = (0.0, 0.0, '')
        (self._origin_y, self._scale_y, self._units_y) = (0.0, 0.0, '')
        (self._origin_z, self._scale_z, self._units_z) = (0.0, 0.0, '')

        self._min_slider.setValue(0)
        self._max_slider.setValue(int(slider_max))
        self._min_lbl.setText('{:.4g}'.format(0))
        self._max_lbl.setText('{:.4g}'.format(1))
        self._min_slider.setEnabled(False)
        self._max_slider.setEnabled(False)

        self._idx_slider.setValue(0)
        self._idx_val.setText('0, 0')
        self._idx_slider.setEnabled(False)
        self._idx_slider.setPageStep(10)

        self.emit(QtCore.SIGNAL("dataChanged()"))

    @property
    def data_is_complex(self):
        return (self.data is not None) and (self._data.dtype in (np.complex64, np.complex128))

    @property
    def switch_fft(self):
        return self._switch_fft

    @switch_fft.setter
    def switch_fft(self,  value):
        if self.data is not None and (self._switch_fft != bool(value)):
            if self.data_is_complex:
                self._data = np.fft.ifft2(np.fft.ifftshift(self._data)).real
                self._units_x = self._units_x.split("/")[1]
            else:
                self._data = np.fft.fftshift(np.fft.fft2(self._data))
                self._units_x = "1/%s" % (self._units_x)

            self._scale_x = 1.0/self.size_x
            self._scale_y = 1.0/self.size_y

        self._switch_fft = bool(value)

        self.plot3Ddata()
        self.emit(QtCore.SIGNAL("dataChanged()"))

    @property
    def valid_source(self):
        return self.dm3 is not None

    @property
    def valid_data(self):
        return self.data is not None

    @property
    def data_is_fft(self):
        return self.data is not None and (self.switch_fft != (self.dm3.imagetype in (3,  5, 13)))

    @property
    def data_is_spectra(self):
        return self.data is not None and (self.dm3.imagetype == 2) and (self.data_dim in (1, 3))

    @property
    def no_spectra(self):
        if self.data_is_spectra:
            if self.data_dim == 1:
                return 1
            else:
                return np.prod(self.data.shape[:-1])
        else:
            return 0

    @property
    def spectrum(self):
        if self.data_is_spectra:
            if self.data_dim == 1:
                return self.data
            else:
                idx = self.index
                data = self.data
                for n in self.data.shape[:-1]:
                    data = data[idx % n]
                    idx = idx//n

                return data
        else:
            return None

    @property
    def index_array(self):
        if self.data_is_spectra and (self.data_dim > 1):
            idx = self.index
            shape = self.data.shape[:-1]
            index = []
            for n in shape:
                index += [idx % n]
                idx = idx//n

            return np.array(index)
        else:
            return None

    @property
    def data(self):
        if self._data is None:
            return None
        elif self._data.dtype in (np.complex64, np.complex128):
            if self._fdata is None:
                self._fdata = np.log(np.abs(self._data)) #np.angle(self._data,  deg=True)
            return self._fdata
        else:
            return self._data

    @property
    def zmin(self):
        if self.data is None:
            return 0.0
        else:
            return np.amin(self.data)

    @property
    def zmax(self):
        if self.data is None:
            return 0.0
        else:
            return np.amax(self.data)

    @property
    def vmin(self):
        if self.data is None:
            return 0.0
        else:
            return min(self.dm3.cuts)

    @property
    def vmax(self):
        if self.data is None:
            return 0.0
        else:
            return max(self.dm3.cuts)

    @property
    def data_dim(self):
        if self.data is not None:
            return len(self.data.shape)
        else:
            return 0

    @property
    def data_width(self):
        if self.data is not None:
            return self.data.shape[0]
        else:
            return 0

    @property
    def data_height(self):
        if self.data_dim > 0:
            if self.data_dim > 1:
                return self.data.shape[1]
            else:
                return 1
        else:
            return 0

    @property
    def data_depth(self):
        if self.data_dim > 0:
            if self.data_dim > 2:
                return self.data.shape[2]
            else:
                return 1
        else:
            return 0

    @property
    def units_x(self):
        if self.data is not None:
            return self._units_x
        else:
            return ''

    @units_x.setter
    def units_x(self, value):
        self._units_x = value

    @property
    def units_y(self):
        if self.data is not None:
            return self._units_y
        else:
            return ''

    @units_y.setter
    def units_y(self, value):
        self._units_y = value

    @property
    def units_z(self):
        if self.data is not None:
            return self._units_z
        else:
            return ''

    @units_z.setter
    def units_z(self, value):
        self._units_z = value

    @property
    def scale_x(self):
        if self.data is not None:
            return self._scale_x
        else:
            return 0.0

    @property
    def scale_y(self):
        if self.data is not None:
            return self._scale_y
        else:
            return 0.0

    @property
    def scale_z(self):
        if self.data is not None:
            return self._scale_z
        else:
            return 0.0

    @property
    def origin_x(self):
        if self.data is not None:
            return self._origin_x
        else:
            return 0.0

    @property
    def origin_y(self):
        if self.data is not None:
            return self._origin_y
        else:
            return 0.0

    @property
    def origin_z(self):
        if self.data is not None:
            return self._origin_z
        else:
            return 0.0

    @property
    def size_x(self):
        if self.data is not None:
            return self.data_width*self.scale_x
        else:
            return 0.0

    @property
    def size_y(self):
        if self.data is not None:
            return self.data_height*self.scale_y
        else:
            return 0.0

    @property
    def size_z(self):
        if self.data is not None:
            return self.data_depth*self.scale_z
        else:
            return 0.0

    @property
    def range_x(self):
        if self.data is not None:
            return self.scale_x*(np.linspace(0.0, (self.data_width - 1), self.data_width) - self.origin_x)
        else:
            return np.linspace(0.0, 0.0, 1)

    @property
    def range_y(self):
        if self.data is not None and (self.data_dim > 1):
            return self.scale_y*(np.linspace(0.0, (self.data_height - 1), self.data_height) - self.origin_y)
        else:
            return np.linspace(0.0, 0.0, 1)

    @property
    def range_z(self):
        if self.data is not None and (self.data_dim > 2):
            return self.scale_z*(np.linspace(0.0, (self.data_depth - 1), self.data_depth) - self.origin_z)
        else:
            return np.linspace(0.0, 0.0, 1)

    @property
    def dm3(self):
         return self._dm3

    @property
    def scale_pos(self):
         return self._scale_pos

    @scale_pos.setter
    def scale_pos(self, value):
        self._scale_pos = value
        self.plot3Ddata()

    def cmap_name(self,  vmin = None,  vmax = None):
        if vmin is None:
            vmin = self._min_slider.value()
        if vmax is None:
            vmax = self._max_slider.value()

        if vmin <= vmax:
            return plt.get_cmap(self._cmap)
        else:
            return plt.get_cmap(self._cmap + '_r')

    @property
    def cmap(self,):
        return self.cmap_name()

    @cmap.setter
    def cmap(self,  value):
        self._cmap = value
        self.updateColorMap()

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self,  value):
        self.clearPlot()
        if os.path.exists(value):
            self._fname = value
            self.readFile()

    @property
    def index(self):
        return self._idx_slider.value()

    @index.setter
    def index(self,  value):
        if 0 <= int(value) < self.no_spectra:
            self.clearPlot()
            self._idx_slider.setValue(value)
            self.plot3Ddata()

    def readFile(self):
        from utils.PyDM3 import DM3

        if os.path.exists(self._fname):
            self._dm3 = DM3(self._fname)
            self._data = self.dm3.imagedata
            self._fdata = None
            (self._origin_x, self._scale_x, self._units_x) = self.dm3.axisunits(0)
            if self.data_dim > 1:
                (self._origin_y, self._scale_y, self._units_y) = self.dm3.axisunits(1)
            else:
                (self._origin_y, self._scale_y, self._units_y) = (0.0, 0.0, '')
            if self.data_dim > 2:
                (self._origin_z, self._scale_z, self._units_z) = self.dm3.axisunits(2)
            else:
                (self._origin_z, self._scale_z, self._units_z) = (0.0, 0.0, '')
            self._switch_fft = False

            self._min_slider.setValue(round(slider_max*(self.vmin - self.zmin)/(self.zmax - self.zmin)))
            self._max_slider.setValue(round(slider_max*(self.vmax - self.zmin)/(self.zmax - self.zmin)))

            self._min_slider.setEnabled(not self.data_is_spectra)
            self._max_slider.setEnabled(not self.data_is_spectra)

            if self.no_spectra > 1:
                self._idx_slider.setRange(0, self.no_spectra - 1)
                self._idx_slider.setValue(0)
                self._idx_slider.setTickInterval(self.data_width)
                self._idx_slider.setEnabled(True)
                self._idx_slider.setPageStep(self.data_width)

                self._min_slider.setValue(0)

                self._idx_val.setText('0, 0')
                self._min_lbl.setText('{:.4g}'.format(0))
                self._max_lbl.setText('{:.4g}'.format(1))

            self.plot3Ddata()

            self.emit(QtCore.SIGNAL("dataChanged()"))
        else:
            self.clearPlot()

    def writeFile(self, fname, zoom=1.0,  base_dpi=400):
        if self.valid_source and fname is not None:
            dpi = base_dpi*zoom

            smin = min(self._min_slider.value(), self._max_slider.value())
            smax = max(self._min_slider.value(), self._max_slider.value())

            vmin = self.zmin + smin*(self.zmax - self.zmin)/slider_max
            vmax = self.zmin + smax*(self.zmax - self.zmin)/slider_max

            size = (self.data_width/float(base_dpi), self.data_height/float(base_dpi))
            cmap = self.cmap
            scale = self.data_width*self.scale_x

            save_image(fname, self.data, size=size, dpi=dpi, cmap=cmap, scale_pos=self.scale_pos, zrange=(vmin, vmax), scale=scale, units=self.units_x)

    def listFiles(self):
        if os.path.exists(self.fname):
            files = [x for x in os.listdir(os.path.dirname(self.fname)) if x.endswith(os.path.splitext(self.fname)[1])]
            files.sort()
        else:
            files = []
        return files

    def firstFile(self):
        files = self.listFiles()
        self.fname = os.path.join(os.path.dirname(self.fname), files[0])

    def previousFile(self):
        files = self.listFiles()
        index = files.index(os.path.basename(self.fname)) - 1
        self.fname = os.path.join(os.path.dirname(self.fname), files[index])

    def nextFile(self):
        files = self.listFiles()
        index = files.index(os.path.basename(self.fname)) + 1
        if index >= len(files):
            index = 0
        self.fname = os.path.join(os.path.dirname(self.fname), files[index])

    def lastFile(self):
        files = self.listFiles()
        self.fname = os.path.join(os.path.dirname(self.fname), files[-1])

    def plot3Ddata(self):
        if self.dm3 is not None:
            if self.data_is_spectra: # The file contains a 1D spectrum or a 3D spectral image
                self._axes.clear()
                self._axes.set_aspect('auto')
                self._axes.set_axis_on()
                self._axes.set_position([0.17, 0.1, 0.78, 0.85])
                self._axes.grid(True)

                if self.data_dim ==3:
                    (x_idx, y_idx) = self.index_array
                    (xo, xs, xu) = (self.origin_x, self.scale_x, self.units_x)
                    (yo, ys, yu) = (self.origin_y, self.scale_y, self.units_y)
                    self._axes.set_title('X = %.1f %s, Y = %.1f %s' % ((x_idx - xo)*xs, xu, (y_idx - yo)*ys, yu))
                    self._axes.set_xlabel(self.units_z)
                    self._curve,  = self._axes.plot(self.range_z, self.spectrum)
                else:
                    self._axes.set_xlabel(self.units_x)
                    self._curve,  = self._axes.plot(self.range_x, self.spectrum)

                self._axes.set_ylabel(self.dm3.sptunits)
                self._fig.canvas.draw()
            else: # It is (should be) a 2D image
                self._axes.clear()

                # Interpolation can be 'nearest', 'bilinear' or 'bicubic'
                self._im = self._axes.imshow(self.data, interpolation='nearest', cmap=plt.get_cmap(self._cmap),
                                             vmin=self.zmin, vmax=self.zmax,
                                             extent=(self.range_x[0], self.range_x[-1], self.range_y[0], self.range_y[-1]))

                if 0 < self._scale_pos <= 10:
                    scale_units = self.units_x
                    scale_conv = 1.0
                    scale_value = 10**np.floor(np.log10(self.size_x/4))
                    scale_value = scale_value*np.floor(self.size_x/4/scale_value)
                    if scale_value < 1:
                        if scale_units == "nm":
                            scale_units = r"$\AA$"
                            scale_conv = 10.0
                            scale_value = 10**np.floor(np.log10(scale_conv*self.size_x/4))
                            scale_value = scale_value*np.floor(scale_conv*self.size_x/4/scale_value)
                        elif scale_units == u'\xb5m':
                            scale_units = "nm"
                            scale_conv = 1000.0
                            scale_value = 10**np.floor(np.log10(scale_conv*self.size_x/4))
                            scale_value = scale_value*np.floor(scale_conv*self.size_x/4/scale_value)

                    if scale_value < 1 or np.isnan(scale_value):
                        scale_units = self.units_x
                        scale_conv = 1.0
                        scale_value = 1

                    scalebar = AnchoredSizeBar(self._axes.transData, scale_value/scale_conv, '%i %s' % (scale_value, scale_units),
                                               loc=self._scale_pos, color='black', frameon=True, label_top=True,
                                               size_vertical=scale_value/scale_conv/10.0, pad=0.2, borderpad=0.5)

                    self._axes.add_artist(scalebar)

            # Update the colormap
            self.updateColorMap()

    def updateColorMap(self, min_value = None, max_value = None):
        if (self._im is not None) and (type(self._im) is AxesImage):# and (self.data_height > 1):
            if min_value is None:
                min_value = self._min_slider.value()
            if max_value is None:
                max_value = self._max_slider.value()

            if max_value == min_value: return

            vmin = self.zmin + min(min_value, max_value)*(self.zmax - self.zmin)/slider_max
            vmax = self.zmin + max(min_value, max_value)*(self.zmax - self.zmin)/slider_max

            self._min_lbl.setText('{:.4g}'.format(vmin))
            self._max_lbl.setText('{:.4g}'.format(vmax))

            self._im.set_norm(Normalize(vmin=vmin, vmax=vmax))
            self._im.set_cmap(self.cmap_name(vmin=min_value, vmax=max_value))

            self._axes.set_axis_off()
            self._axes.set_position([0.0, 0.0, 1.0, 1.0])

            self._fig.canvas.draw()

    def connect_events(self):
        # Connect to the mouse events
        self.cidmotion = self._fig.canvas.mpl_connect('motion_notify_event', self.onMotion)
        self.cidleave = self._fig.canvas.mpl_connect('axes_leave_event', self.onLeave)

    def disconnect_events(self):
        # Disconnect from the mouse events
        if hasattr(self, 'cidmotion'): self._fig.canvas.mpl_disconnect(self.cidmotion)
        if hasattr(self, 'cidleave'): self._fig.canvas.mpl_disconnect(self.cidleave)

    def onMotion(self, event):
        # On motion we will move the region if the mouse is over us
        if event.inaxes != self._axes: return

        if self.valid_source:
            xindex = np.argmin(np.abs(self.range_x - event.xdata))
            yindex = np.argmin(np.abs(self.range_y - event.ydata))

            # This is a custom signal to warn that the position changed
            if self.data_dim == 1: # 1D spectrum
                self.emit(QtCore.SIGNAL("coordsChanged"), (event.xdata, event.ydata))
            elif self.data_dim == 2: # 2D image
                self.emit(QtCore.SIGNAL("coordsChanged"), (event.xdata, event.ydata, self.data[xindex, yindex]))
            else: # 3D spectrum image
                self.emit(QtCore.SIGNAL("coordsChanged"), (event.xdata, event.ydata, self.data[xindex, yindex, 0]))
        else:
            # This is a custom signal to warn that the position changed
            self.emit(QtCore.SIGNAL("coordsChanged"), None)

    def onLeave(self, event):
        # This is a custom signal to warn that the position changed
        self.emit(QtCore.SIGNAL("coordsChanged"), None)


