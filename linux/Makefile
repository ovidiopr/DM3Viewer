PYTHON=`which python`
# Define the destination directory for 'DM3Viewer'
PROGDIR=$(DESTDIR)/usr/share/viewdm3


source:
	# build the source package in the parent directory
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
	rm -rf MANIFEST

deb:
	# rename the source package to project_version.orig.tar.gz
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -i -I -rfakeroot

rpm:
	# Create the 'install.sh' script
	echo "make DESTDIR=\$$RPM_BUILD_ROOT -f linux/Makefile extras" > install.sh
	echo "$(PYTHON) setup.py install --root=\$$RPM_BUILD_ROOT --install-lib=/usr/share/viewdm3 --record=INSTALLED_FILES" >> install.sh
	echo "echo '/usr/bin/viewdm3' >> INSTALLED_FILES" >> install.sh
	echo "echo '/usr/share/applications/viewdm3.desktop' >> INSTALLED_FILES" >> install.sh
	echo "echo '/usr/share/icons/hicolor/scalable/apps/viewer.svg' >> INSTALLED_FILES" >> install.sh
	# Build the rpm files
	$(PYTHON) setup.py bdist_rpm --install-script install.sh --group "Applications/Science" --dist-dir=../
	# Remove the 'install.sh' script
	find . -name 'install.sh' -delete

install:
	# Build 'DM3Viewer' in the destination directory
	mkdir -p $(PROGDIR)
	$(PYTHON) setup.py install --install-lib=$(PROGDIR)/

extras:
	# For the program to run on the terminal (just typing 'viewdm3'), we copy
	# to /usr/bin a shell script which launchs it
	mkdir -p $(DESTDIR)/usr/bin
	cp $(CURDIR)/linux/viewdm3 $(DESTDIR)/usr/bin/viewdm3

	# Copy the 'DM3Viewer' icon to /usr/share/icons/hicolor/scalable/apps
	mkdir -p $(DESTDIR)/usr/share/icons/hicolor/scalable/apps
	cp $(CURDIR)/Icons/viewer.svg $(DESTDIR)/usr/share/icons/hicolor/scalable/apps/viewer.svg

	# Copy the 'viewdm3.desktop' launcher (shortcut) to /usr/share/applications/
	mkdir -p $(DESTDIR)/usr/share/applications
	cp $(CURDIR)/linux/viewdm3.desktop $(DESTDIR)/usr/share/applications/viewdm3.desktop

	# Copy the 'README' file to /usr/share/doc
	#mkdir -p $(DESTDIR)/usr/share/doc/viewdm3
	#cp $(CURDIR)/README $(DESTDIR)/usr/share/doc/viewdm3/README

files:  install \
	extras

clean:
	$(PYTHON) setup.py clean
	$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf build/ dist/ MANIFEST
	find . -name '*.pyc' -delete
	find . -name '*.o' -delete
	find . -name '*.so' -delete
