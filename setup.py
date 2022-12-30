#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  setup.py  --- Python setup file
#     This file is part of DM3Viewer, a simple PyQt application to
#      view DM3 files.
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

from numpy.distutils.core import setup

from utils.version import __mod__, __version__, __title__, __description__, __author__, __email__, __keywords__, __url__

setup(name=__mod__,
      version=__version__,
      description=__title__,
      long_description=__description__,
      author=__author__,
      author_email=__email__,
      maintainer=__author__,
      maintainer_email=__email__,
      keywords=__keywords__,
      url=__url__,
      license='GPL',
      platforms='any',
      packages=[".", "utils"],
      data_files=[(".", ["README.md", "DM3Viewer.ui", "DM3Viewer.qrc"]),
                  ("utils", ["utils/Options.ui"])],
      install_requires=['Numpy>=1.24.0', 'Scipy>=1.9.3', 'PyQt5>= 5.15.7', 'Matplotlib>=3.6.2']
      )
