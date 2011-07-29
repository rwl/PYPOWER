# Copyright (C) 1996-2011 Power System Engineering Research Center
# Copyright (C) 2010-2011 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

"""Test for optional functionality.
"""

def have_fcn(tag):
    """Test for optional functionality.

    Returns 1 if the optional functionality is available, 0 otherwise.

    @author: Ray Zimmerman (PSERC Cornell)
    @author: Richard Lincoln
    """
    if tag.lower() in ['pyipopt', 'ipopt']:
        try:
            __import__('pyipopt')
            return True
        except ImportError:
            return False
    elif tag.lower() == 'nlopt':
        try:
            __import__('nlopt')
            return True
        except ImportError:
            return False
    elif tag.lower() in ['lp_solve', 'lpsolve', 'lpsolve55']:
        try:
            __import__('lpsolve55')
            return True
        except ImportError:
            return False
    else:
        raise ValueError, 'invalid function name [%s]' % tag
