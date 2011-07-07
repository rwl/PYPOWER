# Copyright (C) 2010-2011 Richard Lincoln
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

from os.path import abspath, dirname, join
from setuptools import setup, find_packages

cwd = abspath(dirname(__file__))
f = open(join(cwd, "README"))
kwds = {"long_description": f.read()}
f.close()

entry_points = [
    'pf = pypower.main:pf',
    'opf = pypower.main:opf'
]

setup(name="PYPOWER",
      version="4.0.0",
      description="Solves power flow and optimal power flow problems",
      author="Richard Lincoln",
      author_email="r.w.lincoln@gmail.com",
      url="http://www.pypower.org/",
#      install_requires=["numpy", "scipy"],
      entry_points={"console_scripts": entry_points},
      license="GPLv3",
      include_package_data=True,
      packages=find_packages(),
      test_suite="pypower.t.test_pypower.test_pypower",
      zip_safe=True,
      **kwds)
