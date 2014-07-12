# -*- coding:utf-8 -*-
#  _________________________________________________________________________
#
#  Gcovr: A parsing and reporting tool for gcov
#  Copyright (c) 2013 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the README.md file.
#  _________________________________________________________________________

import sys

from . import sort_keys


#
# Produce the classic gcovr text report
#
def print_text_report(covdata, options):

    if options.output:
        OUTPUT = open(options.output, 'w')
    else:
        OUTPUT = sys.stdout
    total_lines = 0
    total_covered = 0

    # Header
    OUTPUT.write("-" * 78 + '\n')
    OUTPUT.write(" " * 27 + "GCC Code Coverage Report\n")
    OUTPUT.write("Directory: " + options.root + "\n")
    OUTPUT.write("-" * 78 + '\n')
    a = options.show_branch and "Branches" or "Lines"
    b = options.show_branch and "Taken" or "Exec"
    c = "Missing"
    OUTPUT.write(
        "File".ljust(40) + a.rjust(8) + b.rjust(8) + "  Cover   " + c + "\n"
    )
    OUTPUT.write("-" * 78 + '\n')

    # Data
    keys = sort_keys(covdata, options)
    for key in keys:
        t, n, txt = covdata[key].summary()
        total_lines += t
        total_covered += n
        OUTPUT.write(txt + '\n')

    # Footer & summary
    OUTPUT.write("-" * 78 + '\n')
    percent = total_lines and str(int(100.0 * total_covered / total_lines)) \
        or "--"
    OUTPUT.write(
        "TOTAL".ljust(40) + str(total_lines).rjust(8) +
        str(total_covered).rjust(8) + str(percent).rjust(6) + "%" + '\n'
    )
    OUTPUT.write("-" * 78 + '\n')

    # Close logfile
    if options.output:
        OUTPUT.close()


#
# Prints a small report to the standard output
#
def print_summary(covdata, options):
    lines_total = 0
    lines_covered = 0
    branches_total = 0
    branches_covered = 0

    keys = list(covdata.keys())

    for key in keys:
        options.show_branch = False
        (t, n, txt) = covdata[key].coverage()
        lines_total += t
        lines_covered += n

        options.show_branch = True
        (t, n, txt) = covdata[key].coverage()
        branches_total += t
        branches_covered += n

    percent = lines_total and (100.0 * lines_covered / lines_total)
    percent_branches = branches_total and \
        (100.0 * branches_covered / branches_total)

    lines_out = "lines: %0.1f%% (%s out of %s)\n" % (
        percent, lines_covered, lines_total
    )
    branches_out = "branches: %0.1f%% (%s out of %s)\n" % (
        percent_branches, branches_covered, branches_total
    )

    sys.stdout.write(lines_out)
    sys.stdout.write(branches_out)
