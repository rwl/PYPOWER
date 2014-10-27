Changelog
=========

Version 4.1.2 (2014-10-27)
--------------------------

- [FIX] Fixed error in runopf() (`issue #11`_).
- [FIX] Fixed runpf.py with ENFORCE_Q_LIMS option (`pull request #13`_).

.. _`issue #11`: https://github.com/rwl/PYPOWER/issues/11
.. _`pull request #13`: https://github.com/rwl/PYPOWER/pull/13/


Version 4.1.1 (2014-09-17)
--------------------------

- [FIX] loadcase.py: Fixed NumPy 1.9 warning about "== None" comparisions.


Version 4.1.0 (2014-05-29)
--------------------------

- [NEW] Support for Python 3 (3.3 and above).
- [CHANGE] Updated to MATPOWER 4.1.
- [REMOVED] Support for Python 2.5 and below.


Version 4.0.1 (2011-07-14)
--------------------------

- [CHANGE] printpf.py: changed boolean operators from bitwise to logical to fix
  the output options

- [FIX] savecase.py: adding indentation to produce valid Python modules


Version 4.0.0 (2011-07-07)
--------------------------

Initial release, port of MATPOWER version 4.0
