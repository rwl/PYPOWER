Changelog
=========

Version 5.1.5 (2020-10-21)
--------------------------

- [NEW] Added new function: AC continuation power flow

Version 5.1.2 (2017-06-09)
--------------------------

- [NEW] Configured continuous integration using Travis.

Version 5.1.0 (2017-06-09)
--------------------------

- [NEW] Added Python 3 support.

Version 5.0.1 (2016-07-04)
--------------------------

- [FIX] Fixed `issue #21`_ and  `issue #25`_ in savecase() (`pull request #26`_).
- [CHANGE] Based on 'recursion limit' issues affecting savemat() in savecase(), converted non-scalars to arrays.
- [NEW] Created t_savecase.py and added t_savecase() to test_pypower.py.

.. _`issue #21`: https://github.com/rwl/PYPOWER/issues/21
.. _`issue #25`: https://github.com/rwl/PYPOWER/issues/25
.. _`pull request #26`: https://github.com/rwl/PYPOWER/pull/26/

Version 5.0.0 (2015-05-29)
--------------------------

- [CHANGE] 3-clause BSD License


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
