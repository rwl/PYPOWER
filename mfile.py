# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from pyparsing import Literal, Word, ZeroOrMore, Optional, OneOrMore, \
    alphanums, delimitedList, alphas, Combine, Or, Group, TokenConverter, \
    restOfLine, oneOf, nums


class ToBoolean(TokenConverter):
    """ Converter to make token boolean.
    """
    def postParse(self, instring, loc, tokenlist):
        """ Converts the first token to boolean.
        """
        return bool(tokenlist[0])


class ToInteger(TokenConverter):
    """ Converter to make token into an integer.
    """
    def postParse(self, instring, loc, tokenlist):
        """ Converts the first token to an integer.
        """
        return int(tokenlist[0])


class ToFloat(TokenConverter):
    """ Converter to make token into a float.
    """
    def postParse(self, instring, loc, tokenlist):
        """ Converts the first token into a float.
        """
        return float(tokenlist[0])


def read(file_or_filename):
    """ Returns a dictionary with the contents of the .m file.
    """
    # punctuation
    lbrack = Literal("[")
    rbrack = Literal("]")
    equals = Literal("=")
    scolon = Literal(";").suppress()
    sign = oneOf("+ -")
    decimal_sep = "."

    # matlab comment
    comment = Group(Literal('%') + restOfLine).suppress()

    integer = ToInteger(Combine(Optional(sign) + Word(nums)))

    real = ToFloat(Combine(Optional(sign) + Word(nums) + \
        Optional(decimal_sep + Word(nums)) + \
        Optional(oneOf("E e") + Word(nums))))

    # header
    title = Word(alphanums).setResultsName("title")
    header = Literal("function") + lbrack + delimitedList(Word(alphas)) + \
        rbrack + "=" + title

    # baseMVA
    base_mva = integer.setResultsName("baseMVA")
    base_mva_expr = Literal("baseMVA") + equals + base_mva + scolon

    # bus data
    bus_id = integer.setResultsName("bus_id")
    bus_type = ToInteger(Word('123', exact=1)).setResultsName("bus_type")
    appr_demand = real.setResultsName("Pd") + real.setResultsName("Qd")
    shunt_addm = real.setResultsName("Gs") + real.setResultsName("Bs")
    area = integer.setResultsName("area")
    Vm = real.setResultsName("Vm")
    Va = real.setResultsName("Va")
    kV_base = real.setResultsName("baseKV")
    zone = integer.setResultsName("zone")
    Vmax = real.setResultsName("Vmax")
    Vmin = real.setResultsName("Vmin")

    bus_data = bus_id + bus_type + appr_demand + shunt_addm + \
        area + Vm + Va + kV_base + zone + Vmax + Vmin + scolon

    bus_array = Combine(Optional("mpc.") + Literal('bus')) + '=' + '[' + \
        ZeroOrMore(bus_data) + Optional(']' + scolon)
    bus_array.setResultsName("bus")

    # generator data
    gen_bus_id = integer.setResultsName("bus_id")
    active = real.setResultsName("Pg")
    reactive = real.setResultsName("Qg")
    max_reactive = real.setResultsName("Qmax")
    min_reactive = real.setResultsName("Qmin")
    voltage = real.setResultsName("Vg")
    base_mva = real.setResultsName("mBase")
#    status = boolean.setResultsName("status")
    status = integer.setResultsName("status")
    max_active = real.setResultsName("Pmax")
    min_active = real.setResultsName("Pmin")

    gen_data = gen_bus_id + active + reactive + max_reactive + \
        min_reactive + voltage + base_mva + status + max_active + \
        min_active + scolon

    gen_array = Literal('gen') + '=' + '[' + \
        ZeroOrMore(gen_data) + Optional(']' + scolon)
    gen_array.setResultsName("gen")

    # branch data
    source_bus = integer.setResultsName("fbus")
    target_bus = integer.setResultsName("tbus")
    resistance = real.setResultsName("r")
    reactance = real.setResultsName("x")
    susceptance = real.setResultsName("b")
    long_mva = real.setResultsName("rateA")
    short_mva = real.setResultsName("rateB")
    emerg_mva = real.setResultsName("rateC")
    ratio = real.setResultsName("ratio")
    angle = real.setResultsName("angle")
    status = integer.setResultsName("status")

    branch_data = source_bus + target_bus + resistance + reactance + \
        susceptance + long_mva + short_mva + emerg_mva + ratio + angle + \
        status + scolon

    branch_array = Literal('branch') + '=' + '[' + \
        ZeroOrMore(branch_data) + Optional(']' + scolon)

    # area data
    area = integer.setResultsName("area_id")
    price_ref_bus = integer.setResultsName("price_ref_bus")

    area_data = area + price_ref_bus + scolon

    area_array = Literal('areas') + equals + lbrack + \
        ZeroOrMore(area_data) + Optional(rbrack + scolon)

    # generator cost data

    # [model, startup, shutdown, n, x0, y0, x1, y1]
    # 1 - piecewise linear, 2 - polynomial
    model = integer.setResultsName("model")
    # start up cost
    startup = real.setResultsName("startup")
    # shut down cost
    shutdown = real.setResultsName("shutdown")
    # number of cost coefficients to follow for polynomial
    # cost function, or number of data points for pw linear
    n = integer.setResultsName("n")
    x0 = real.setResultsName("x0")
    y0 = real.setResultsName("y0")
    x1 = real.setResultsName("x1")
    y1 = real.setResultsName("y1")

    linear_cost_data = model + startup + shutdown + n + \
        OneOrMore(real) + scolon

#    piecewise_cost_data = model + startup + shutdown + n + OneOrMore(tuple)
#    polynomial_cost_data = model + startup + shutdown + n + OneOrMore(real)

    generator_cost_array = Literal('gencost') + '=' + '[' + \
        ZeroOrMore(linear_cost_data) + Optional(']' + scolon)

    # assemble pyparsing case
    case = header + \
        ZeroOrMore(comment) + base_mva# + \
#        ZeroOrMore(comment) + bus_array + \
#        ZeroOrMore(comment) + gen_array + \
#        ZeroOrMore(comment) + branch_array + \
#        ZeroOrMore(comment) + Optional(area_array) + \
#        ZeroOrMore(comment) + Optional(generator_cost_array)

    # parse the case file
    data = case.parseFile(file_or_filename)

if __name__ == "__main__":
    d = read("case6ww.m")
    print d
