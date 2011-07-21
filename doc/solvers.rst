Third Party Solvers
-------------------

PYPOWER includes interfaces to several third party solvers.  This section
provides some notes on how to install the solvers.

IPOPT
+++++

AC optimal power flow (OPF) problems and DC OPF problems with quadratic cost
functions can be solved using IPOPT_.  To install the Python interface to
IPOPT, PyIPOPT_, on Debian first obtain the latest stable release of IPOPT.
It must be newer than version 3.9.1::

  $ wget http://www.coin-or.org/download/source/Ipopt/Ipopt-3.9.3.tgz
  $ tar xvf Ipopt-3.9.3.tgz
  $ cd Ipopt-3.9.3/

IPOPT requires a third party linear solver. MUMPS_ is the only compatible
solver available under a free software license. IPOPT provides a convenient
script for downloading and patching MUMPS::

  $ cd ThirdParty/Mumps
  $ ./get.Mumps
  $ cd ../..

IPOPT will compile MUMPS automatically when it is compiled. By default the
IPOPT libraries will be installed into ``./lib/`` and the headers into
``./include/coin``. This can be changed by specifying the ``prefix`` flag::

  $ ./configure --prefix=/usr/local
  $ make
  $ sudo make install

To let the linker know where the new libraries are create a file::

  $ sudo nano -w /etc/ld.so.conf.d/ipopt.conf

containing the paths to IPOPT and MUMPS::

  /usr/local/lib/coin
  /usr/local/lib/coin/ThirdParty

Next, obtain the latest PyIPOPT source code::

  $ cd ..
  $ svn checkout https://pyipopt.googlecode.com/svn/trunk/ pyipopt
  $ cd pyipopt/

Modify the makefile paths to match your environment::

	CC = gcc
	CFLAGS = -O3 -fpic -shared #-g
	DFLAGS = -fpic -shared
	LDFLAGS = -lipopt -lm -llapack -lblas -lcoinmumps

	PY_DIR = /usr/local/lib/python2.6/dist-packages
	IPOPT_INCLUDE = /usr/local/include/coin

	IPOPT_LIB = /usr/local/lib/coin

	MUMPS_INCLUDE=/usr/local/include/coin/ThirdParty
	MUMPS_LIB = /usr/local/lib/coin/ThirdParty

	PYTHON_INCLUDE = /usr/include/python2.6

	NUMPY_INCLUDE = /usr/include/numpy

	pyipopt: src/callback.c src/pyipopt.c
		$(CC) -o pyipopt.so -L$(IPOPT_LIB) -I$(IPOPT_INCLUDE) -L$(MUMPS_LIB) -I$(MUMPS_INCLUDE) -I$(PYTHON_INCLUDE) -I$(NUMPY_INCLUDE) $(CFLAGS) $(LDFLAGS) src/pyipopt.c src/callback.c

	install: pyipopt
		cp ./pyipopt.so $(PY_DIR)
	clean:
		rm pyipopt.so

Compile and install to ``PY_DIR``::

  $ make
  $ make install


LP Solve
++++++++

DC OPF problems with piecewise linear can be solved using a Python interface to
lp_solve_. Download and unpack the latest source archive
(lp_solve_5.5.2.0_source.tar.gz) build::

  $ cd lp_solve_5.5/lpsolve55
  $ sh ./ccc

Copy the ``liblpsolve55`` files to the library path::

  $ cp bin/ux32/* /usr/loca/lib/

Download and unpack the Python source code
(lp_solve_5.5.2.0_Python_source.tar.gz) into the same directory as the lp_solve
source. Compile the Python extension::

  $ cd ../extra/Python/
  $ sudo python setup.py install


.. include:: ./link_names.txt
