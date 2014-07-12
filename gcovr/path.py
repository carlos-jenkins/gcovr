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

import os
import re
import sys


#
# Class that creates path aliases
#
class PathAliaser(object):

    def __init__(self):
        self.aliases = {}
        self.master_targets = set()
        self.preferred_name = {}

    def path_startswith(self, path, base):
        return path.startswith(base) and (
            len(base) == len(path) or path[len(base)] == os.path.sep)

    def master_path(self, path):
        match_found = False
        while True:
            for base, alias in self.aliases.items():
                if self.path_startswith(path, base):
                    path = alias + path[len(base):]
                    match_found = True
                    break
            for master_base in self.master_targets:
                if self.path_startswith(path, master_base):
                    return path, master_base, True
            if match_found:
                sys.stderr.write(
                    "(ERROR) violating fundamental assumption while walking "
                    "directory tree.\n\tPlease report this to the gcovr "
                    "developers.\n")
            return path, None, match_found

    def unalias_path(self, path):
        path = resolve_symlinks(path)
        path, master_base, known_path = self.master_path(path)
        if not known_path:
            return path
        # Try and resolve the preferred name for this location
        if master_base in self.preferred_name:
            return self.preferred_name[master_base] + path[len(master_base):]
        return path

    def add_master_target(self, master):
        self.master_targets.add(master)

    def add_alias(self, target, master):
        self.aliases[target] = master

    def set_preferred(self, master, preferred):
        self.preferred_name[master] = preferred


def resolve_symlinks(orig_path):
    """
    Return the normalized absolute path name with all symbolic links resolved
    """
    return os.path.realpath(orig_path)


# This is UGLY.  Here's why: UNIX resolves symbolic links by walking the
# entire directory structure.  What that means is that relative links
# are always relative to the actual directory inode, and not the
# "virtual" path that the user might have traversed (over symlinks) on
# the way to that directory.  Here's the canonical example:
#
#   a / b / c / testfile
#   a / d / e --> ../../a/b
#   m / n --> /a
#   x / y / z --> /m/n/d
#
# If we start in "y", we will see the following directory structure:
#   y
#   |-- z
#       |-- e
#           |-- c
#               |-- testfile
#
# The problem is that using a simple traversal based on the Python
# documentation:
#
#    (os.path.join(os.path.dirname(path), os.readlink(result)))
#
# will not work: we will see a link to /m/n/d from /x/y, but completely
# miss the fact that n is itself a link.  If we then naively attempt to
# apply the "c" relative link, we get an intermediate path that looks
# like "/m/n/d/e/../../a/b", which would get normalized to "/m/n/a/b"; a
# nonexistant path.  The solution is that we need to walk the original
# path, along with the full path of all links 1 directory at a time and
# check for embedded symlinks.
#
#
# NB:  Users have complained that this code causes a performance issue.
# I have replaced this logic with os.walk(), which works for Python >= 2.6
#
def link_walker(path):

    for root, dirs, files in os.walk(os.path.abspath(path), followlinks=True):
        yield (os.path.abspath(os.path.realpath(root)), dirs, files)


def search_file(expr, path):
    """
    Given a search path, recursively descend to find files that match a
    regular expression.
    """
    ans = []
    pattern = re.compile(expr)
    if path is None or path == ".":
        path = os.getcwd()
    elif not os.path.exists(path):
        raise IOError("Unknown directory '" + path + "'")
    for root, dirs, files in link_walker(path):
        for name in files:
            if pattern.match(name):
                name = os.path.join(root, name)
                if os.path.islink(name):
                    ans.append(os.path.abspath(os.readlink(name)))
                else:
                    ans.append(os.path.abspath(name))
    return ans
