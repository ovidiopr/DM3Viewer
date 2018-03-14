# MAKEFILE
# 
# Makefile to create the Windows installer. Many options are
# available:
#   distribution    the distribution including the installer and source
#                   code;
#   installer       create the installer;
#   exe             creates the executable using PyInstaller;
#   -               used alone, creates the distribution;
#   clean           remove all created files except the distribution
#                   files;
#   all             all of the above;
#   cleanall        remove all created files.
# 
# In order for make to work, you need Python, PyQt, PyInstaller, and
# NSIS.
# 
# Copyright (c) 2018 Ovidio Peña Rodríguez.
# 
# This file is part of DM3Viewer.
# 
# DM3Viewer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# DM3Viewer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

SHELL=cmd.exe
PYTHON=python.exe

VERSION = 0.1.0
PROGNAME = viewdm3
EXTNAME = DM3Viewer

MKDIR = mkdir
RMDIR = rmdir
CPDIR = xcopy
CP = copy
RM = del
CD = cd
MV = move
7Z = "c:\Program Files\7-Zip\7z.exe"
NSIS = "c:\Program Files (x86)\NSIS\makensis.exe"

INSTALLER_NAME = Install_$(EXTNAME)_$(VERSION).exe
TAR_NAME = $(EXTNAME)_$(VERSION).tar
INSTALLER_DIRECTORY = $(EXTNAME)_$(VERSION)

$(INSTALLER_DIRECTORY)/$(INSTALLER_NAME): $(INSTALLER_NAME)\
                                          dist/$(PROGNAME).exe
	if exist $(INSTALLER_DIRECTORY) $(RMDIR) $(INSTALLER_DIRECTORY) /s /q
	$(MKDIR) $(INSTALLER_DIRECTORY)
	$(CP) $(INSTALLER_NAME) $(INSTALLER_DIRECTORY)
#	if exist $(INSTALLER_NAME) $(RM) $(INSTALLER_NAME)
	source

distribution: $(INSTALLER_DIRECTORY)/$(INSTALLER_NAME)

installer: $(INSTALLER_NAME)

$(INSTALLER_NAME): dist/$(PROGNAME).exe\
                   $(PROGNAME).nsi
	$(NSIS) $(PROGNAME).nsi

exe: dist/$(PROGNAME).exe

dist/$(PROGNAME).exe: *.py *.ui *.qrc\
                    windows/viewer.ico\
                    utils/*.py\
                    utils/*.ui
	pyinstaller $(PROGNAME).py -w\
		-i "windows/viewer.ico"\
		--add-data "$(EXTNAME).ui;."\
		--add-data "$(EXTNAME).qrc;."\
		--add-data "README.txt;."\
		--add-data "LICENSE.txt;."\
		--add-data "utils/Options.ui;utils"\
		--hidden-import="scipy._lib.messagestream"

install_script: $(PROGNAME).nsi

$(PROGNAME).nsi: dist/$(PROGNAME).exe\
               windows\installer.py
# Copy the script installer.py in the root dir
	$(CP) windows\installer.py . /y
	python installer.py
# Remove the script installer.py from the root dir
	$(RM) installer.py

source:
	if not exist $(INSTALLER_DIRECTORY) $(MKDIR) $(INSTALLER_DIRECTORY)
# build the source package in the installer directory
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=$(INSTALLER_DIRECTORY) --prune
	if exist MANIFEST $(RM) MANIFEST

clean:
	if exist $(PROGNAME).nsi $(RM) $(PROGNAME).nsi
	if exist $(PROGNAME).spec $(RM) $(PROGNAME).spec
	if exist build $(RMDIR) build /s /q
	if exist dist $(RMDIR) dist /s /q
	if exist $(INSTALLER_NAME) $(RM) $(INSTALLER_NAME)

all: distribution\
     clean

cleanall: clean
	if exist $(INSTALLER_DIRECTORY) $(RMDIR) $(INSTALLER_DIRECTORY) /s /q# MAKEFILE
# 
# Makefile to create the Windows installer. Many options are
# available:
#   distribution    the distribution including the installer and source
#                   code;
#   installer       create the installer;
#   exe             creates the executable using PyInstaller;
#   -               used alone, creates the distribution;
#   clean           remove all created files except the distribution
#                   files;
#   all             all of the above;
#   cleanall        remove all created files.
# 
# In order for make to work, you need Python, PyQt, PyInstaller, and
# NSIS.
# 
# Copyright (c) 2018 Ovidio Peña Rodríguez.
# 
# This file is part of DM3Viewer.
# 
# DM3Viewer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# DM3Viewer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

SHELL=cmd.exe
PYTHON=python.exe

VERSION = 0.1.0
PROGNAME = viewdm3
EXTNAME = DM3Viewer

MKDIR = mkdir
RMDIR = rmdir
CPDIR = xcopy
CP = copy
RM = del
CD = cd
MV = move
7Z = "c:\Program Files\7-Zip\7z.exe"
NSIS = "c:\Program Files (x86)\NSIS\makensis.exe"

INSTALLER_NAME = Install_$(EXTNAME)_$(VERSION).exe
TAR_NAME = $(EXTNAME)_$(VERSION).tar
INSTALLER_DIRECTORY = $(EXTNAME)_$(VERSION)

$(INSTALLER_DIRECTORY)/$(INSTALLER_NAME): $(INSTALLER_NAME)\
                                          dist/$(PROGNAME).exe
	if exist $(INSTALLER_DIRECTORY) $(RMDIR) $(INSTALLER_DIRECTORY) /s /q
	$(MKDIR) $(INSTALLER_DIRECTORY)
	$(CP) $(INSTALLER_NAME) $(INSTALLER_DIRECTORY)
#	if exist $(INSTALLER_NAME) $(RM) $(INSTALLER_NAME)
	source

distribution: $(INSTALLER_DIRECTORY)/$(INSTALLER_NAME)

installer: $(INSTALLER_NAME)

$(INSTALLER_NAME): dist/$(PROGNAME).exe\
                   $(PROGNAME).nsi
	$(NSIS) $(PROGNAME).nsi

exe: dist/$(PROGNAME).exe

dist/$(PROGNAME).exe: *.py *.ui *.qrc\
                    windows/viewer.ico\
                    utils/*.py\
                    utils/*.ui
	pyinstaller $(PROGNAME).py -w\
		-i "windows/viewer.ico"\
		--add-data "$(EXTNAME).ui;."\
		--add-data "$(EXTNAME).qrc;."\
		--add-data "README.txt;."\
		--add-data "LICENSE.txt;."\
		--add-data "utils/Options.ui;utils"\
		--hidden-import="scipy._lib.messagestream"

install_script: $(PROGNAME).nsi

$(PROGNAME).nsi: dist/$(PROGNAME).exe\
               windows\installer.py
# Copy the script installer.py in the root dir
	$(CP) windows\installer.py . /y
	python installer.py
# Remove the script installer.py from the root dir
	$(RM) installer.py

source:
	if not exist $(INSTALLER_DIRECTORY) $(MKDIR) $(INSTALLER_DIRECTORY)
# build the source package in the installer directory
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=$(INSTALLER_DIRECTORY) --prune
	if exist MANIFEST $(RM) MANIFEST

clean:
	if exist $(PROGNAME).nsi $(RM) $(PROGNAME).nsi
	if exist $(PROGNAME).spec $(RM) $(PROGNAME).spec
	if exist build $(RMDIR) build /s /q
	if exist dist $(RMDIR) dist /s /q
	if exist $(INSTALLER_NAME) $(RM) $(INSTALLER_NAME)

all: distribution\
     clean

cleanall: clean
	if exist $(INSTALLER_DIRECTORY) $(RMDIR) $(INSTALLER_DIRECTORY) /s /q
