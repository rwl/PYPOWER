# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

import logging

from os.path import basename, splitext, isfile

import csv

from numpy import array

logger = logging.getLogger(__name__)

DEFAULT_VERSION = 31
SUPPORTED_VERSIONS = [29, 30 , 31]

def psse2case(casefile, version=None, delimiter=None):
    """ Returns a dict containing case data matrices as values.
    """
    if isinstance(casefile, dict):
        ppc = casefile
    elif isinstance(casefile, basestring):
        fname = basename(casefile)
        logger.info("Loading PSS/E Raw file [%s]." % fname)

        fd = None
        try:
            fd = open(casefile, "rb")
        except:
            logger.error("Error opening %s." % fname)
            return None
        finally:
            if file is not None:
                ppc = _parse_file(file, version, delimiter)
                fd.close()
    else:
        ppc = _parse_file(casefile, version, delimiter)

    return ppc

def _parse_file(fd, version, delimiter):
    sep = _delimiter(fd) if delimiter is None else delimiter
    ver = _version(fd, sep) if version is None else version

    ppc = {}


    return ppc


def _delimiter(fd):
    """Uses the first line to determine if data items are separated by a comma
    or one or more blank spaces.

    @rtype: A one-character string.
    @return: Either ',' or ' '.
    """
    fd.seek(0)
    header0 = file.next().split("/")[0]

    if "," in header0:
        logger.info("Assuming comma delimited data items.")
        delimiter = ","
    else:
        logger.info("Assuming data items are separated by whitespace.")
        delimiter = " "

    return delimiter


def _version(fd, delimiter):
    """Uses the first line to determine the data format version or returns the
    default version.

    @rtype: int
    @return: Raw data format version.
    """
    fd.seek(0)
#    header0 = file.next().split("/")[0]
    reader = csv.reader(fd, delimiter=delimiter, skipinitialspace=True)

    h0 = reader.next()
    if len(h0) < 3:
        version = DEFAULT_VERSION
        logger.info("No version info found, assuming version %d." % version)
    else:
        # IC, SBASE, REV, XFRRAT, NXFRAT, BASFRQ
        version = int(h0[2])
        logger.info("Found version %d data." % version)
        if version not in SUPPORTED_VERSIONS:
            logger.warning("Version %d data not currently supported. "
                "Supported versions are: %s "
                "Attempting to parse file as version %d data." %
                (version, SUPPORTED_VERSIONS, DEFAULT_VERSION))
            version = DEFAULT_VERSION

    return version
