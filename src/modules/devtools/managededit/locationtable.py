"""
This files defines the class LocationTable.

Copyright (C) 2009 Craig W. Wright and 2013 Google. All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sqlite3
import sys
import re

from devtools.managededit.configuration import Configuration

TABLE_NAME="Location"


class LocationTable:

   def __init__(self, configuration):
      if not isinstance(configuration, Configuration):
         raise RuntimeError("Expected a Configuration as the first argument.")
      self.config_ = configuration

   def __len__(self):
      conn = self._opendb()
      c = conn.cursor()
      c.execute('''SELECT count(*) FROM %s''' % (TABLE_NAME))
      l = c.fetchone()[0]
      self._closedb(conn)
      return l

   def _opendb(self, rebuild=False):
      if rebuild:
         if os.path.isfile(self.config_.getLocationTableFileFullPath()):
            os.remove(self.config_.getLocationTableFileFullPath())
         conn = sqlite3.connect(self.config_.getLocationTableFileFullPath())
         c = conn.cursor()
         c.execute('''CREATE TABLE %s (basename, fullpath)''' % (TABLE_NAME))
         conn.commit()
         return conn
      else:
         return sqlite3.connect(self.config_.getLocationTableFileFullPath())

   def _closedb(self, conn):
      conn.close()

   def rebuild(self):
      """
         Rebuild the location table by traversing all of the SearchPaths
         associated with the Configuration.
      """
      conn = self._opendb(rebuild=True)
      c = conn.cursor()

      try:
         for sp in self.config_.getSearchPaths():
            for f in sp.walk(self.config_.getDirectoryIgnores(),
                             self.config_.getFileIgnores()):
               base = os.path.basename(f)
               command = "INSERT INTO %s VALUES ('%s','%s')" % (TABLE_NAME, base, f)
               c.execute(command)
      finally:
         conn.commit()
         self._closedb(conn)

   def search(self, searchPattern):
      """
         Search the location table for the entries that match searchPattern and
         return them as a list. A list of tuples is returned where the first entry
         in each tuple is the basename of the file and the second entry is the full
         path. The search is done on the base name.
      """
      ret = SearchResult()
      exp = re.compile(str(searchPattern))
      exactMatches=[]
      cwdExactMatches = []

      if os.path.isfile(searchPattern):
         cwdExactMatches.append(
            (searchPattern, os.path.join(os.getcwd(), searchPattern)))
      else:
         if self.config_.getOptionValue("searchCurrentWorkingDirectory"):
            for (root, dirs, files) in os.walk("."):
               dirs[:] = []
               for f in files:
                  if exp.search(f):
                     ret.append(tuple([f, os.path.join(os.getcwd(), f)]))
                     if searchPattern == f:
                        cwdExactMatches.append((f, os.path.join(os.getcwd(), f)))

      conn = self._opendb()
      c = conn.cursor()
      c.execute('''SELECT * FROM %s''' % TABLE_NAME)

      try:
         for item in c:
            if exp.search(item[0]):
               ret.append(item)
            if searchPattern == item[0]:
              exactMatches.append(item)
      finally:
         self._closedb(conn)

      if len(exactMatches) == 1:
        ret = SearchResult()
        ret.append(exactMatches[0])

      if len(cwdExactMatches) == 1:
         ret = SearchResult()
         ret.append(cwdExactMatches[0])

      ret.uniqify()

      return ret

   def dump(self, fileobject):
      """
         Print all of the entries in the database to stdout.

         @param fileobject
         A object that supports a write method.
      """
      conn = self._opendb()
      c = conn.cursor()
      c.execute('''SELECT * FROM %s''' % TABLE_NAME)
      try:
         for row in c:
            print row
      finally:
         self._closedb(conn)


class SearchResult:
   """
      What is returned from the LocationTable.search method.
   """

   def __init__(self):
      self.results_ = []

   def __len__(self):
      return len(self.results_)

   def __iter__(self):
      return self.results_.__iter__()

   def __getitem__(self, key):
      return self.results_[key]

   def append(self, result):
      """
         Append a result.
      """
      self.results_.append(result)

   def narrow(self, criteria):
      """
         If criteria begins with a number and is < len(self)
         treat it as an index into the results and narrow the results to a single item.
         Otherwise treat criteria as a regular expression.
      """
      criteria = str(criteria)

      input = criteria.split(".")
      if input[0].isdigit() and int(input[0]) < len(self):
         self.results_ = [self.results_[int(input[0])]]
      else:
         exp = re.compile(criteria)
         self.results_ = [r for r in self.results_ if exp.search(r[0])]

   def getCommonDirectory(self):
     """If all results live in a common directory return it."""
     dirs = set([os.path.dirname(res[1]) for res in self.results_])
     return dirs.pop() if len(dirs) == 1 else None

   def uniqify(self):
     self.results_ = sorted(set(self.results_))

   def _uniqifyGroup(self, i):
      same = []
      same.append(self.results_[i])
      if i+1 < len(self.results_):
        for r in self.results_[i+1:]:
            if r[0] == same[0][0]:
               same.append(r)
            else:
               break

      if len(same) == 1:
         return [""]

      ret = []
      # It would be good to actually look at path commonality and
      # be more sophisticated here, but this is easy and good enough
      # for my current purpose.
      for s in same:
         components = s[1].split("/")
         size = 4
         if len(components) < size:
            size = len(components)-1
         ret.append("/".join(components[-size:-1]))

      return ret

   def list(self):
      i = 0
      while i < len(self.results_):
         uniquePathsForGroup = self._uniqifyGroup(i);
         for (j, u) in zip(range(i, i+len(uniquePathsForGroup)),uniquePathsForGroup):
            if not u:
               out = "%d. %s\n" % (i, self.results_[j][0])
            else:
               out = "%d. %s - (%s)\n" % (j, self.results_[j][0], u)
            sys.stderr.write(out)
         i += len(uniquePathsForGroup)

      # older implementation
      #for i,r in zip(range(len(self.results_)), self.results_):
      #   sys.stderr.write(str(i) + ". " + str(os.path.join(r[0])) + "\n")

   def dump(self):
      for r in self.results_:
         sys.stdout.write(str(r) + "\n")
