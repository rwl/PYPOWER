# Copyright (C) 2009 Stijn Cole <stijn.cole@esat.kuleuven.be>
# Copyright (C) 2010 Richard Lincoln <r.w.lincoln@gmail.com>
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

def Loaddyn(casefile_dyn):
    """ Loads dynamic data.

    @param casefile_dyn: m-file with dynamic data
    @return triple of the form (system frequency,
        step size for fixed-step integration algorithms,
        stop time of integration algorithm)

    @see: U{http://www.esat.kuleuven.be/electa/teaching/matdyn/}
    """
    if isinstance(casefile_dyn, dict):
        freq = casefile_dyn["freq"]
        stepsize = casefile_dyn["stepsize"]
        stoptime = casefile_dyn["stoptime"]
    else:
        dyn = __import__(casefile_dyn)
        _, _, _, freq, stepsize, stoptime = eval("dyn.%s" % casefile_dyn)

    return freq,stepsize,stoptime
