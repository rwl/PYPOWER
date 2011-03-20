# Copyright (C) 2009-2011 Rui Bo <eeborui@hotmail.com>
# Copyright (C) 2011 Richard Lincoln <r.w.lincoln@gmail.com>
#
# PYPOWER is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# PYPOWER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PYPOWER. If not, see <http://www.gnu.org/licenses/>.

def checkDataIntegrity(measure, idx, sigma, nbus):
    """Check state estimation input data integrity.
    returns 1 if the data is complete, 0 otherwise.
    NOTE: for each type of measurements, the measurement vector and index
    vector should have the same length. If not, the longer vector will be
    truncated to have the same length as the shorter vector.

    @author: Rui Bo
    @author: Richard Lincoln
    @see: U{http://www.pserc.cornell.edu/matpower/}
    """
    ## options
    verbose = 2    # ppopt[30]

    success     = 1    # pass integrity check?
    nowarning   = 1    # no warning found?

    ## check input data consistency
    # for PF
    if len(measure["PF"]) != len(idx["idx_zPF"]):
        print 'Warning: measurement vector and index vector for PF do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["PF"]), len(idx["idx_zPF"]))
        measure["PF"]  = measure["PF"][:min_len]
        idx["idx_zPF"] = idx["idx_zPF"][:min_len]
        nowarning = 0

    if (idx["idx_zPF"] != None) and (len(sigma["sigma_PF"] <= 0)):  # no sigma defined
        print 'Error: Sigma for PF is not specified.'
        success = 0

    if len(sigma["sigma_PF"]) > 1:
        print 'Warning: Sigma for PF is assigned multiple values. The first value will be used.'
        sigma["sigma_PF"] = sigma["sigma_PF"][0]
        nowarning = 0

    # for PT
    if len(measure["PT"]) != len(idx["idx_zPT"]):
        print 'Warning: measurement vector and index vector for PT do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["PT"]), len(idx["idx_zPT"]))
        measure["PT"]  = measure["PT"][:min_len]
        idx["idx_zPT"] = idx["idx_zPT"][:min_len]
        nowarning = 0

    if idx["idx_zPT"] != None and len(sigma["sigma_PT"]) <= 0:  # no sigma defined
        print 'Error: Sigma for PT is not specified.'
        success = 0

    if len(sigma["sigma_PT"]) > 1:
        print 'Warning: Sigma for PT is assigned multiple values. The first value will be used.'
        sigma["sigma_PT"] = sigma["sigma_PT"](1)
        nowarning = 0


    # for PG
    if len(measure["PG"]) != len(idx["idx_zPG"]):
        print 'Warning: measurement vector and index vector for PG do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["PG"]), len(idx["idx_zPG"]))
        measure["PG"]  = measure["PG"][:min_len]
        idx["idx_zPG"] = idx["idx_zPG"][:min_len]
        nowarning = 0

    if idx["idx_zPG"] != None and len(sigma["sigma_PG"]) <= 0:  # no sigma defined
        print 'Error: Sigma for PG is not specified.'
        success = 0

    if len(sigma["sigma_PG"]) > 1:
        print 'Warning: Sigma for PG is assigned multiple values. The first value will be used.'
        sigma["sigma_PG"] = sigma["sigma_PG"][0]
        nowarning = 0

    # for Va
    if len(measure["Va"]) != len(idx["idx_zVa"]):
        print 'Warning: measurement vector and index vector for Va do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["Va"]), len(idx["idx_zVa"]))
        measure["Va"]  = measure["Va"][:min_len]
        idx["idx_zVa"] = idx["idx_zVa"][:min_len]
        nowarning = 0

    if idx["idx_zVa"] != None and len(sigma["sigma_Va"]) <= 0:  # no sigma defined
        print 'Error: Sigma for Va is not specified.'
        success = 0

    if len(sigma["sigma_Va"]) > 1:
        print 'Warning: Sigma for Va is assigned multiple values. The first value will be used.'
        sigma["sigma_Va"] = sigma["sigma_Va"][0]
        nowarning = 0

    # for QF
    if len(measure["QF"]) != len(idx["idx_zQF"]):
        print 'Warning: measurement vector and index vector for QF do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["QF"]), len(idx["idx_zQF"]))
        measure["QF"]  = measure["QF"][:min_len]
        idx["idx_zQF"] = idx["idx_zQF"][:min_len]
        nowarning = 0

    if idx["idx_zQF"] != None and len(sigma["sigma_QF"]) <= 0:  # no sigma defined
        print 'Error: Sigma for QF is not specified.'
        success = 0

    if len(sigma["sigma_QF"]) > 1:
        print 'Warning: Sigma for QF is assigned multiple values. The first value will be used.'
        sigma["sigma_QF"] = sigma["sigma_QF"][0]
        nowarning = 0

    # for QT
    if len(measure["QT"]) != len(idx["idx_zQT"]):
        print 'Warning: measurement vector and index vector for QT do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["QT"]), len(idx["idx_zQT"]))
        measure["QT"]  = measure["QT"][:min_len]
        idx["idx_zQT"] = idx["idx_zQT"][:min_len]
        nowarning = 0

    if idx["idx_zQT"] != None and len(sigma["sigma_QT"]) <= 0:  # no sigma defined
        print 'Error: Sigma for QT is not specified.'
        success = 0

    if len(sigma["sigma_QT"]) > 1:
        print 'Warning: Sigma for QT is assigned multiple values. The first value will be used.'
        sigma["sigma_QT"] = sigma["sigma_QT"][0]
        nowarning = 0

    # for QG
    if len(measure["QG"]) != len(idx["idx_zQG"]):
        print 'Warning: measurement vector and index vector for QG do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["QG"]), len(idx["idx_zQG"]))
        measure["QG"]  = measure["QG"][:min_len]
        idx["idx_zQG"] = idx["idx_zQG"][:min_len]
        nowarning = 0

    if idx["idx_zQG"] != None and len(sigma["sigma_QG"]) <= 0:  # no sigma defined
        print 'Error: Sigma for QG is not specified.'
        success = 0

    if len(sigma["sigma_QG"]) > 1:
        print 'Warning: Sigma for QG is assigned multiple values. The first value will be used.'
        sigma["sigma_QG"] = sigma["sigma_QG"][0]
        nowarning = 0

    # for Vm
    if len(measure["Vm"]) != len(idx["idx_zVm"]):
        print 'Warning: measurement vector and index vector for Vm do not have the same length. The longer vector will be truncated.'
        min_len = min(len(measure["Vm"]), len(idx["idx_zVm"]))
        measure["Vm"]  = measure["Vm"][:min_len]
        idx["idx_zVm"] = idx["idx_zVm"][:min_len]
        nowarning = 0

    if idx["idx_zVm"] != None and len(sigma["sigma_Vm"]) <= 0:  # no sigma defined
        print 'Error: Sigma for Vm is not specified.'
        success = 0

    if len(sigma["sigma_Vm"]) > 1:
        print 'Warning: Sigma for Vm is assigned multiple values. The first value will be used.'
        sigma["sigma_Vm"] = sigma["sigma_Vm"][0]
        nowarning = 0


    # pause when warnings are present
    if success and not nowarning:
        raw_input('Press any key to continue...')

    ## check if total number of measurements is no less than total number of
    ## variables to be estimated
    allMeasure = [
                    measure["PF"],
                    measure["PT"],
                    measure["PG"],
                    measure["Va"],
                    measure["QF"],
                    measure["QT"],
                    measure["QG"],
                    measure["Vm"]
                    ]
    if len(allMeasure) < 2 * (nbus - 1):
        print 'Error: There are less measurements (%d) than number of variables to be estimated (%d).', len(allMeasure), 2 * (nbus - 1)
        success = 0
