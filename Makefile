DESTDIR=/
BUILDIR=$(CURDIR)/debian/DM3Viewer
PROJECT=DM3Viewer
VERSION=0.1.0

all:
	@echo "make win-src - Create source tarball (windows)"
	@echo "make win-exe - Create windows executable"
	@echo "make win-inst - Create windows installer"
	@echo "make win-clean - Delete unnecessary files (windows)"
	@echo "make source - Create source tarball"
	@echo "make rpm - Create rpm package"
	@echo "make deb - Create deb package"
	@echo "make clean - Delete unnecessary files"

win-src:
	make -f windows/Makefile source

win-exe:
	make -f windows/Makefile exe

win-inst:
	make -f windows/Makefile all

win-clean:
	make -f windows/Makefile clean

source:
	make -f linux/Makefile source

deb:
	make -f linux/Makefile deb

rpm:
	make -f linux/Makefile rpm

clean:
	make -f linux/Makefile clean
