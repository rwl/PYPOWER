# Copyright (C) 2011 Richard Lincoln
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

"""PYPOWER utilities.
"""


def sub2ind(shape, I, J, row_major=False):
    """Returns the linear indices of subscripts
    """
    if row_major:
        ind = (I % shape[0]) * shape[1] + (J % shape[1])
    else:
        ind = (J % shape[1]) * shape[0] + (I % shape[0])

    return ind.astype(int)


def feval(func, *args, **kw_args):
    """Evaluates the function C{func} using positional arguments C{args}
    and keyword arguments C{kw_args}.
    """
    return eval(func)(*args, **kw_args)


def have_fcn(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False
