# Copyright (C) 2010-2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages

# Read the long description from the README.
thisdir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(thisdir, "README"))
kwds = {"long_description": f.read()}
f.close()

setup(name="PYPOWER",
      version="0.1.1",
      description="Solves power flow and optimal power flow problems",
      author="Richard Lincoln",
      author_email="r.w.lincoln@gmail.com",
      url="http://rwl.github.com/PYPOWER",
#      install_requires=["numpy", "scipy"],
      entry_points={"console_scripts": ["pypower = pypower.main:main"]},
      license="GPLv3",
      include_package_data=False,
      packages=find_packages(),
      test_suite="pypower.test",
      zip_safe=True,
      **kwds)
