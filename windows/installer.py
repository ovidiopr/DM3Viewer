#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  installer.py  --- Generate NSIS install script
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


import os
from utils.version import __name__, __mod__, __version__


# Gather all the directories and separate the sources and examples.

base_directory = os.path.join("dist", __mod__)

directories = [""]

example_directories = []
example_files = []
source_directories = []
source_files = []
executable_directories = []
executable_files = []

while len(directories) > 0:
	directory = directories.pop()
	
	# List subdirectories
	subdirectories = [os.path.join(directory, filename) for filename in os.listdir(os.path.join(base_directory, directory)) if os.path.isdir(os.path.join(base_directory, directory, filename))]
	subdirectories.reverse()
	directories += subdirectories
	
	# Separate the examples, the sources and other directories.
	if "sources" in directory:
		source_directories.append(directory)
		source_files.append([os.path.join(directory, filename) for filename in os.listdir(os.path.join(base_directory, directory)) if os.path.isfile(os.path.join(base_directory, directory, filename))])
	elif "examples" in directory:
		example_directories.append(directory)
		example_files.append([os.path.join(directory, filename) for filename in os.listdir(os.path.join(base_directory, directory)) if os.path.isfile(os.path.join(base_directory, directory, filename))])
	else:
		executable_directories.append(directory)
		executable_files.append([os.path.join(directory, filename) for filename in os.listdir(os.path.join(base_directory, directory)) if os.path.isfile(os.path.join(base_directory, directory, filename))])


# Write the script.

script = open("%s.nsi" % (__mod__), 'w')

# Write a header.
script.write("; DO NOT EDIT THIS FILE.\n")
script.write("; \n")
script.write("; This script was automatically generated by installer.py.\n")
script.write("\n")

# Include the VersionCompare macro from the WordFunc header.
script.write("!include \"WordFunc.nsh\"\n")
script.write("!insertmacro VersionCompare\n")

# Set the compression: lzma compression is longer, but more effective.
script.write("SetCompressor lzma\n")
script.write("\n")

# Set the version number and the full name.
script.write("!define VERSION %s\n" % (__version__))
script.write("!define NAME \"%s\"\n" % (__name__))
script.write("!define MODULE \"%s\"\n" % (__mod__))
script.write("\n")

# The name of the software.
script.write("Name \"${NAME} ${VERSION}\"\n")
script.write("\n")

# The file to write.
script.write("OutFile \"Install_${NAME}_${VERSION}.exe\"\n")
script.write("\n")

# The default installation directory.
script.write("InstallDir $PROGRAMFILES\\${NAME}\n")
script.write("\n")

# Registry key to check for directory (so if you install again, it will 
# overwrite the old one automatically).
script.write("InstallDirRegKey HKLM \"Software\\${NAME}\" \"Install_Dir\"\n")
script.write("\n")


# Upon initialization, we verify if the program is already installed
# and show a message dependent on the version that is already
# installed.
script.write("Function .onInit\n")

script.write("\tVar /GLOBAL UNINSTALLER\n")
script.write("\tVar /GLOBAL INSTALLED_VERSION\n")
script.write("\tVar /GLOBAL COMPARISON\n")

script.write("\tReadRegStr $UNINSTALLER HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"UninstallString\"\n")
script.write("\tStrCmp $UNINSTALLER \"\" done\n")
script.write("\t\n")

script.write("\tReadRegStr $INSTALLED_VERSION HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"DisplayVersion\"\n")
script.write("\tStrCmp $INSTALLED_VERSION \"\" older_version\n")
script.write("\t${VersionCompare} $INSTALLED_VERSION ${VERSION} $COMPARISON\n")
script.write("\tStrCmp $COMPARISON \"0\" same_version\n")
script.write("\tStrCmp $COMPARISON \"1\" newer_version\n")
script.write("\tStrCmp $COMPARISON \"2\" older_version\n")
script.write("\t\n")

script.write("\tolder_version:\n")
script.write("\tMessageBox MB_YESNO|MB_ICONEXCLAMATION \\\n")
script.write("\t\"An older version of ${NAME} is already installed and needs to be uninstalled before this installation can proceed. Do you wish to uninstall the older version?\" \\\n")
script.write("\tIDYES uninstall\n")
script.write("\tAbort\n")
script.write("\t\n")

script.write("\tsame_version:\n")
script.write("\tMessageBox MB_YESNO|MB_ICONEXCLAMATION \\\n")
script.write("\t\"This version of ${NAME} is already installed. Do you wish to reinstall it?\" \\\n")
script.write("\tIDYES uninstall\n")
script.write("\tAbort\n")
script.write("\t\n")

script.write("\tnewer_version:\n")
script.write("\tMessageBox MB_YESNO|MB_ICONEXCLAMATION \\\n")
script.write("\t\"A newer version of ${NAME} is already installed. Do you wish to uninstall the newer version and downgrade to this version?\" \\\n")
script.write("\tIDOK uninstall\n")
script.write("\tAbort\n")
script.write("\t\n")

script.write("\tuninstall:\n")
script.write("\tExec \"$UNINSTALLER /S\"\n")
#script.write("\tReadRegStr $UNINSTALLER HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"UninstallString\"\n")
#script.write("\tStrCmp $UNINSTALLER \"\" done\n")
#script.write("\tAbort\n")
script.write("\t\n")

script.write("\tdone:\n")
script.write("\t\n") 

script.write("FunctionEnd\n")


script.write("\t\n") 

# Pages.
script.write("Page components\n")
script.write("Page directory\n")
script.write("Page instfiles\n")
script.write("\n")
script.write("UninstPage uninstConfirm\n")
script.write("UninstPage instfiles\n")
script.write("\n")

# This section is required.
script.write("Section \"${NAME} (required)\"\n")
script.write("\t\n")
script.write("\tSectionIn RO\n")
script.write("\t\n")

# Put all the files in the appropriate directories.
for i in range(len(executable_directories)):
	directory = executable_directories[i]
	if directory == "":
		script.write("\tSetOutPath \"$INSTDIR\"\n")
	else:
		script.write("\tSetOutPath \"$INSTDIR\\%s\"\n" % directory)
	for file in executable_files[i]:
		script.write("\tFile %s\n" % os.path.join(base_directory, file))
	script.write("\t\n")

# Write the installation path into the registry.
script.write("\tWriteRegStr HKLM SOFTWARE\\${NAME} \"Install_Dir\" \"$INSTDIR\"\n")  
script.write("\t\n")

# Write the uninstall keys for Windows.
script.write("\tWriteRegStr HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"DisplayName\" \"${NAME}\"\n")
script.write("\tWriteRegStr HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"DisplayVersion\" \"${VERSION}\"\n")
script.write("\tWriteRegStr HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"UninstallString\" \'\"$INSTDIR\\uninstall.exe\"\'\n")
script.write("\tWriteRegDWORD HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"NoModify\" 1\n")
script.write("\tWriteRegDWORD HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\" \"NoRepair\" 1\n")
script.write("\t\n")
script.write("\tWriteUninstaller \"uninstall.exe\"\n")
script.write("\t\n")

script.write("SectionEnd\n")

script.write("\n")

# The examples section is optional.
#script.write("Section \"Examples\"\n")
#script.write("\t\n")

# Put all the files in the appropriate directories.
#for i in range(len(example_directories)):
#	directory = example_directories[i]
#	script.write("\tSetOutPath \"$INSTDIR\\%s\"\n" % directory)
#	for file in example_files[i]:
#		script.write("\tFile %s\n" % os.path.join(base_directory, file))
#	script.write("\t\n")

#script.write("SectionEnd\n")

#script.write("\n")

# The sources section is optional.
#script.write("Section /o \"Source code\"\n")
#script.write("\t\n")

# Put all the files in the appropriate directories.
#for i in range(len(source_directories)):
#	directory = source_directories[i]
#	script.write("\tSetOutPath \"$INSTDIR\\%s\"\n" % directory)
#	for file in source_files[i]:
#		script.write("\tFile %s\n" % os.path.join(base_directory, file))
#	script.write("\t\n")

#script.write("SectionEnd\n")

#script.write("\n")

# Offer the possibility to put shortcuts in the Start Menu.
script.write("Section \"Start Menu Shortcuts\"\n")
script.write("\t\n")
script.write("\tSetOutPath \"$INSTDIR\"\n")
script.write("\t\n")
script.write("\tCreateDirectory \"$SMPROGRAMS\\${NAME}\"\n")
script.write("\tCreateShortCut \"$SMPROGRAMS\\${NAME}\\Uninstall.lnk\" \"$INSTDIR\\uninstall.exe\" \"\" \"$INSTDIR\\uninstall.exe\" 0\n")
script.write("\tCreateShortCut \"$SMPROGRAMS\\${NAME}\\${NAME}.lnk\" \"$INSTDIR\\${MODULE}.exe\" \"\" \"$INSTDIR\\${MODULE}.exe\" 0\n")
script.write("\tCreateShortCut \"$SMPROGRAMS\\${NAME}\README.lnk\" \"$INSTDIR\\README.txt\" \"\" \"$INSTDIR\\README.txt\" 0\n")
script.write("\tCreateShortCut \"$SMPROGRAMS\\${NAME}\GPL.lnk\" \"$INSTDIR\\LICENSE.txt\" \"\" \"$INSTDIR\\LICENSE.txt\" 0\n")
script.write("\t\n")
script.write("SectionEnd\n")

script.write("\n")

# Uninstaller.
script.write("Section \"Uninstall\"\n")
script.write("\t\n")

# Remove all source files.
for i in range(len(source_directories)-1, -1, -1):
	directory = source_directories[i]
	for file in source_files[i]:
		script.write("\tDelete $INSTDIR\%s\n" % file)
	script.write("\t\n")
	script.write("\tRMDir \"$INSTDIR\%s\"\n" % directory)
	script.write("\t\n")

# Remove all example files.
for i in range(len(example_directories)-1, -1, -1):
	directory = example_directories[i]
	for file in example_files[i]:
		script.write("\tDelete $INSTDIR\%s\n" % file)
	script.write("\t\n")
	script.write("\tRMDir \"$INSTDIR\%s\"\n" % directory)
	script.write("\t\n")

# Remove all executable files.
for i in range(len(executable_directories)-1, -1, -1):
	directory = executable_directories[i]
	for file in executable_files[i]:
		script.write("\tDelete $INSTDIR\%s\n" % file)
	script.write("\t\n")
	if directory == "":
		script.write("\tSetOutPath \"$INSTDIR\"\n")
	else:
		script.write("\tRMDir \"$INSTDIR\%s\"\n" % directory)
	script.write("\t\n")

# Remove registry keys.
script.write("\tDeleteRegKey HKLM \"Software\Microsoft\Windows\CurrentVersion\\Uninstall\\${NAME}\"\n")
script.write("\tDeleteRegKey HKLM SOFTWARE\\${NAME}\n")
script.write("\t\n")

# Remove the uninstaller.
script.write("\tDelete $INSTDIR\\uninstall.exe\n")
script.write("\t\n")

# Remove shortcuts, if any.
script.write("\tDelete \"$SMPROGRAMS\\${NAME}\\Uninstall.lnk\"\n")
script.write("\tDelete \"$SMPROGRAMS\\${NAME}\\${NAME}.lnk\"\n")
script.write("\tDelete \"$SMPROGRAMS\\${NAME}\README.lnk\"\n")
script.write("\tDelete \"$SMPROGRAMS\\${NAME}\GPL.lnk\"\n")
script.write("\t\n")

# Remove directories used
script.write("\tRMDir \"$SMPROGRAMS\\${NAME}\"\n")
script.write("\tRMDir \"$INSTDIR\"\n")
script.write("\t\n")

script.write("SectionEnd\n")
