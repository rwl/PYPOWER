============
Introduction
============

PYPOWER is a power flow and Optimal Power Flow (OPF) solver. It is a port of
MATPOWER_ to the Python_ programming language. Current
features include:

* DC and AC (Newton's method & Fast Decoupled) power flow and
* DC and AC optimal power flow (OPF)


Installation
============

PYPOWER depends upon:

* Python_ 2.6-3.5 and
* SciPy_ 0.9 or later.

It can be installed using pip_::

  $ pip install PYPOWER

Alternatively, `download <http://pypi.python.org/pypi/PYPOWER#downloads>`_ and
unpack the tarball and install::

  $ tar zxf PYPOWER-4.x.y.tar.gz
  $ python setup.py install


Using PYPOWER
=============

Installing PYPOWER creates ``pf`` and ``opf`` commands. To list the command
options::

  $ pf -h

PYPOWER includes a selection of test cases. For example, to run a power flow
on the IEEE 14 bus test case::

  $ pf -c case14

Alternatively, the path to a PYPOWER case data file can be specified::

  $ pf /path/to/case14.py

The ``opf`` command has the same calling syntax. For example, to solve an OPF
for the IEEE Reliability Test System and write the solved case to file::

  $ opf -c case24_ieee_rts --solvedcase=rtsout.py

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
Copyright (c) 2010-2015 Richard Lincoln  

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
