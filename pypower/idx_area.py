# Copyright (C) 1996-2011 Power System Engineering Research Center
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

"""Defines constants for named column indices to areas matrix.

The index, name and meaning of each column of the areas matrix is given below:

columns 0-1
    0.  C{AREA_I}           area number
    1.  C{PRICE_REF_BUS}    price reference bus for this area

@author: Ray Zimmerman (PSERC Cornell)
@author: Richard Lincoln
"""

# define the indices
AREA_I          = 0    # area number
PRICE_REF_BUS   = 1    # price reference bus for this area
