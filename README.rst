**PYPOWER** is a power flow and Optimal Power Flow (OPF) solver. It is a port of
MATPOWER_ to the Python_ programming language. Current
features include:

* DC and AC (Newton's method & Fast Decoupled) power flow and
* DC and AC optimal power flow (OPF)

Status
======

.. |nbsp| unicode:: 0xa0
   :trim:

|libraries|_ |nbsp| |pyversions|_ |nbsp| |license|_ |nbsp| |downloads|_ |nbsp| |travis|_ |nbsp| |pypi_version|_

.. |libraries| image:: https://img.shields.io/librariesio/release/pypi/PYPOWER
.. _libraries: https://libraries.io/pypi/PYPOWER

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/PYPOWER
.. _pyversions: https://img.shields.io/librariesio/release/pypi/PYPOWER

.. |license| image:: https://img.shields.io/pypi/l/PYPOWER
.. _license: https://github.com/rwl/PYPOWER/blob/master/LICENSE

.. |downloads| image:: https://img.shields.io/pypi/dm/PYPOWER.svg
.. _downloads: https://pypistats.org/packages/pypower

.. |travis| image:: https://img.shields.io/travis/rwl/pypower/master?label=Travis%20CI
.. _travis: https://travis-ci.org/rwl/PYPOWER

.. |pypi_version| image:: https://badge.fury.io/py/PYPOWER.svg
.. _pypi_version: https://badge.fury.io/py/PYPOWER

Prerequisites
=============

PYPOWER depends upon these prerequisites on the level of the operating system:

* Python_ >= 3.5

Virtual Environment
===================

PYPOWER is recommended to be installed into a virtual environment::

  $ python3.8 -m venv venv  # Or any supported Python version

Dependencies
============

PYPOWER depends upon NumPy, SciPy and PyRLU which can be installed as follows::

  $ venv/bin/python -m pip install -r requirements.txt

Installation
============

The recommended way of installing PYPOWER is using pip_::

  $ venv/bin/python -m pip install PYPOWER

Alternatively, `download <http://pypi.python.org/pypi/PYPOWER#downloads>`_ and
unpack the tarball and install::

  $ tar zxf PYPOWER-5.x.y.tar.gz
  $ venv/bin/python setup.py install

Testing
=======

PYPOWER can be tested locally using the same tooling as on Travis CI::

  $ venv/bin/python -m tox -e py27,py38  # Or any supported Python version

Using PYPOWER
=============

Installing PYPOWER creates ``pf`` and ``opf`` commands. To list the command
options::

  $ venv/bin/pf -h

or::

  $ venv/bin/opf -h

PYPOWER includes a selection of test cases. For example, to run a power flow
on the IEEE 14 bus test case::

  $ venv/bin/pf -c case14

Alternatively, the path to a PYPOWER case data file can be specified::

  $ venv/bin/pf /path/to/case14.py

The ``opf`` command has the same calling syntax. For example, to solve an OPF
for the IEEE Reliability Test System and write the solved case to file::

  $ venv/bin/opf -c case24_ieee_rts --solvedcase=rtsout.py

For further information please refer to https://rwl.github.io/PYPOWER/ and the
`API documentation`_.

Support
=======

Questions and comments regarding PYPOWER should be directed to the `mailing
list <http://groups.google.com/group/pypower>`_:

    pypower@googlegroups.com

License & Copyright
===================

Copyright (c) 1996-2015, Power System Engineering Research Center (PSERC)  
Copyright (c) 2010-2025 Richard Lincoln

The code in PYPOWER is distributed under the 3-clause BSD license
below. The PYPOWER case files distributed with PYPOWER are not covered
by the BSD license. In most cases, the data has either been included
with permission or has been converted from data available from a
public source.

While not required by the terms of the license, we do request that
publications derived from the use of MATPOWER explicitly acknowledge
that fact by citing:

    R. D. Zimmerman, C. E. Murillo-Sanchez, and R. J. Thomas, "MATPOWER:
    Steady-State Operations, Planning and Analysis Tools for Power Systems
    Research and Education," Power Systems, IEEE Transactions on, vol. 26,
    no. 1, pp. 12–19, Feb. 2011.

Links
=====

* MATPOWER_ from PSERC (Cornell)
* matpower.app_ MATPOWER web application based on GNU Octave in WebAssembly
* Oct2PYPOWER_ Python bridge to MATPOWER using Oct2Py
* pandapower_ from Fraunhofer IWES and University of Kassel
* TESP_ from PNNL
* MatDyn_ by Stijn Cole
* PSAT_ by Federico Milano
* OpenDSS_ from EPRI
* GridLAB-D_ from PNNL
* PyCIM_

.. _Python: http://www.python.org
.. _pip: https://pip.pypa.io
.. _SciPy: http://www.scipy.org
.. _MATPOWER: http://www.pserc.cornell.edu/matpower/
.. _Git: http://git-scm.com/
.. _GitHub: http://github.com/rwl/PYPOWER
.. _`API documentation`: https://rwl.github.io/PYPOWER/api
.. _PyCIM: http://www.pycim.org
.. _MatDyn: http://www.esat.kuleuven.be/electa/teaching/matdyn/
.. _PSAT: http://www.uclm.es/area/gsee/web/Federico/psat.htm
.. _OpenDSS: http://sourceforge.net/projects/electricdss/
.. _GridLAB-D: http://sourceforge.net/projects/gridlab-d/
.. _pandapower: http://www.uni-kassel.de/go/pandapower
.. _TESP: https://tesp.readthedocs.io
.. _Oct2PYPOWER: https://github.com/rwl/oct2pypower
.. _matpower.app: https://matpower.app
