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


def tabulate_data(gcovdata):
    """
    Return a dictionary with tabulated data ready for a report.
    """
    raise NotImplementedError('FIXME: Implement!')


def sort_keys(covdata, options):
    """
    Sort GCOV data as requested by the user.
    """

    keys = list(covdata.keys())

    def _num_uncovered(key):
        total, covered, percent = covdata[key].coverage()
        return total - covered

    def _percent_uncovered(key):
        total, covered, percent = covdata[key].coverage()
        if covered:
            return -1.0 * covered / total
        else:
            return total or 1e6

    if options.sort_uncovered:
        keys.sort(key=_num_uncovered)
    elif options.sort_percent:
        keys.sort(key=_percent_uncovered)
    else:
        keys.sort()

    return keys
