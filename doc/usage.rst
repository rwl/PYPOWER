Usage
-----

Installing PYPOWER creates ``pf`` and ``opf`` commands. To list the command
options::

  $ pf -h

PYPOWER includes a selection of test cases. For example, to run a power flow
on the IEEE 14 bus test case::

  $ pf -c case14

Alternatively, the path to a PYPOWER case data file can be specified.::

  $ pf /path/to/case14.py

The ``opf`` command has the same calling syntax. For example, to solve an OPF
for the IEEE Reliability Test System and write the solved case to file::

  $ opf -c case24_ieee_rts --solvedcase=rtsout.py

For further information please refer to the `API documentation`_.

.. include:: ./link_names.txt
