# $Id: Makefile,v 1.6 2010/11/14 08:52:35 rwl Exp $
#

PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/pypower
PROJECT=pypower
VERSION=0.1.1

COMPILE=--no-compile

all:
        @echo "make source - Create source package"
        @echo "make install - Install on local system"
        @echo "make buildrpm - Generate a rpm package"
        @echo "make builddeb - Generate a deb package"
        @echo "make clean - Get rid of scratch and byte files"

source:
        $(PYTHON) setup.py sdist $(COMPILE)

install:
        $(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
        $(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb:
        # build the source package in the parent directory
        # then rename it to project_version.orig.tar.gz
        $(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
        rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
        # build the package
        dpkg-buildpackage -i -I -rfakeroot

clean:
        $(PYTHON) setup.py clean
        $(MAKE) -f $(CURDIR)/debian/rules clean
        rm -rf build/ MANIFEST
        find . -name '*.pyc' -delete
