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
from bsddb.db import *
import sys
import re

from devtools.managededit.configuration import Configuration


class LocationTable:

   def __init__(self, configuration):
      if not isinstance(configuration, Configuration):
         raise RuntimeError("Expected a Configuration as the first argument.")
      self.config_ = configuration

   def __len__(self):
      db = self._opendb()
      l = len(db)
      self._closedb(db)
      return l

   def _opendb(self, dbflags=None):
      db = DB()
      db.set_flags(DB_DUP)
      db.open(self.config_.getLocationTableFileFullPath(),
              dbtype=DB_BTREE,
              flags=(dbflags if dbflags else DB_CREATE))
      return db


   def _closedb(self, db):
      db.sync()
      db.close()

   def rebuild(self):
      """
         Rebuild the location table by traversing all of the SearchPaths
         associated with the Configuration.
      """
      db = self._opendb(DB_TRUNCATE|DB_CREATE)

      try:
         for sp in self.config_.getSearchPaths():
            for f in sp.walk(self.config_.getDirectoryIgnores(),
                             self.config_.getFileIgnores()):
               base = os.path.basename(f)
               db.put(str(base), str(f))

      finally:
         self._closedb(db)

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

      if self.config_.getOptionValue("searchCurrentWorkingDirectory"):
         for (root, dirs, files) in os.walk("."):
            dirs[:] = []
            for f in files:
               if exp.search(f):
                  ret.append(tuple([f, os.path.join(os.getcwd(), f)]))
               if searchPattern == f:
                 exactMatches.append(os.path.join(os.getcwd(), f))

      db = self._opendb()
      cursor = db.cursor()

      try:
         item = cursor.first()
         while item:
            if exp.search(item[0]):
               ret.append(item)
            if searchPattern == item[0]:
              exactMatches.append(item)
            item = cursor.next()
      finally:
         cursor.close()
         self._closedb(db)

      if len(exactMatches) == 1:
        ret = SearchResult()
        ret.append(exactMatches[0])

      ret.uniqify()

      return ret

   def dump(self, fileobject):
      """
         Print all of the entries in the database to stdout.

         @param fileobject
         A object that supports a write method.
      """
      db = self._opendb()
      cursor = db.cursor()

      try:
         item = cursor.first()
         while item:
            fileobject.write(str(item) + "\n")
            item = cursor.next()
      finally:
         cursor.close()
         self._closedb(db)


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

   def list(self):
      for i,r in zip(range(len(self.results_)), self.results_):
         sys.stderr.write(str(i) + ". " + str(os.path.join(r[0])) + "\n")

   def dump(self):
      for r in self.results_:
         sys.stdout.write(str(r) + "\n")
