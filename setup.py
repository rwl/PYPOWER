# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
      version="3.2.0b1",
      description="Power flow and optimal power flow solver",
      author="Richard Lincoln",
      author_email="r.w.lincoln@gmail.com",
      url="http://www.pypower.org/",
#      install_requires=["numpy", "scipy"],
      entry_points={"console_scripts": entry_points},
      license="Apache License version 2.0",
      include_package_data=True,
      packages=find_packages(),
      test_suite="pypower.t.test_pypower.test_pypower",
      zip_safe=True,
      **kwds)

# python setup.py sdist bdist_egg bdist_wininst bdist_msi upload
