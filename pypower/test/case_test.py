# Copyright (C) 2009-2011 Richard Lincoln
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

import unittest

import base_test

class Case4GSTest(base_test._BaseTestCase):

    def __init__(self, methodName='runTest'):
        super(Case4GSTest, self).__init__(methodName)

        self.case_name = "case4gs"

if __name__ == "__main__":
    unittest.main()
