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

import os
import logging
import csv

from numpy import zeros, r_

logger = logging.getLogger(__name__)

DEFAULT_VERSION = 31
SUPPORTED_VERSIONS = [29, 30 , 31, 32]


def psse2case(casefile, version=None, delimiter=None):
    """ Returns a dict containing case data matrices as values.
    """
    if isinstance(casefile, dict):
        ppc = casefile
    elif isinstance(casefile, basestring):
        fname = os.path.basename(casefile)
        logger.info("Loading PSS/E Raw file [%s]." % fname)

        fd = None
        try:
            fd = open(casefile, "rb")
        except:
            logger.error("Error opening %s." % fname)
            return None
        finally:
            if file is not None:
                ppc = _parse_file(fd, version, delimiter)
                fd.close()
    else:
        ppc = _parse_file(casefile, version, delimiter)

    return ppc


def _parse_file(fd, version, delimiter):
    sep = _delimiter(fd) if delimiter is None else delimiter
    ver = _version(fd, sep) if version is None else version

    fd.seek(0)
    reader = csv.reader(fd, delimiter=sep, skipinitialspace=True)

    baseMVA = _parse_header(reader)
    busdata, busmap = _parse_buses(reader, ver)
#    _parse_branches(reader, ver, busmap)

    ppc = {
        "baseMVA": baseMVA,
#        "bus": busdata
    }

    return ppc


def _parse_header(reader):
    """Reads the first three lines of the file and returns the system base MVA.
    """
    h0 = reader.next()
    _ = reader.next()
    _ = reader.next()

    assert (h0[0] == "0") or (h0[0] == "1")

    # v29-30: IC, SBASE
    # v31-32: IC, SBASE, REV, XFRRAT, NXFRAT, BASFRQ
    baseMVA = float(h0[1])

    return baseMVA


def _parse_buses(reader, version):
    # v29-30: I, 'NAME', BASKV, IDE, GL, BL, AREA, ZONE, VM, VA, OWNER
    # v31-32: I, 'NAME', BASKV, IDE, AREA, ZONE, OWNER, VM, VA
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin

    buses = zeros((0, 13))
    busmap = {}
    c = 0

    busdata = reader.next()
    # 0 / END OF BUS DATA, BEGIN LOAD DATA
    while busdata[0].split("/")[0].strip() != "0":
        bus = zeros((1, 13))

        i = int(busdata[0])
        busmap[i] = c

        bus[0, 0] = i
        bus[0, 1] = float(busdata[3]) # type
        bus[0, 2] = 0.0 # Pd (see _parse_loads)
        bus[0, 3] = 0.0 # Qd (see _parse_loads)
        if version in [29, 30]:
            bus[0, 4] = float(busdata[4])  # Gs
            bus[0, 5] = float(busdata[5])  # Bs
            bus[0, 6] = int(busdata[6])    # area
            bus[0, 7] = float(busdata[8])  # Vm
            bus[0, 8] = float(busdata[9])  # Va
            bus[0, 10] = float(busdata[7]) # zone
        elif version in [31, 32]:
            bus[0, 6] = int(busdata[4])    # area
            bus[0, 7] = float(busdata[7])  # Vm
            bus[0, 8] = float(busdata[8])  # Va
            bus[0, 10] = float(busdata[5]) # zone
        bus[0, 9] = float(busdata[2]) # baseKV
        bus[0, 11] = 1.1 # Vmax
        bus[0, 12] = 0.9 # Vmin

        buses = r_[buses, bus]
        busdata = reader.next()
        c += 1

    return buses, busmap


def _parse_branches(reader, ver, busmap):
    pass


def _delimiter(fd):
    """Uses the first line to determine if data items are separated by a comma
    or one or more blank spaces.

    @rtype: A one-character string.
    @return: Either ',' or ' '.
    """
    fd.seek(0)
    header0 = fd.next().split("/")[0]

    if "," in header0:
        logger.info("Found comma delimited data items.")
        delimiter = ","
    else:
        logger.info("Found data items separated by whitespace.")
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ppc = psse2case("/tmp/bench.raw")

#    import savecase
#    savecase.savecase("/tmp/bench.m", ppc["doc"], ppc)
