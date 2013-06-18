"""
This files defines the class SearchPath.

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
import re
import sys

import devtools.common.utility

class SearchPath:
   """
      A SearchPath defines a path to traverse to search for files.

      For now one property, whether to do the search recursively exists.

      It is expected that the search path will be able to handle specific ignore
      directives in the future. For now all ignores must be passed in from the
      outside (which is quite workable for a strictly global set of ignores)

   """

   def __init__(self, path, recursive):
      """
         Treat the pat as a template string and use os.eviron as
         the mapping.
      """
      self.path_ = devtools.common.utility.substituteEnvironment(path)
      self.recursive_ = bool(recursive)
      self.dirIgnores_ = []
      if not os.path.exists(self.path_):
         sys.stderr.write("The path: '" + self.path_ + "' does not exist.")

   def addDirectoryIgnore(self, patternString):
      self.dirIgnores_.append(re.compile(devtools.common.utility.substituteEnvironment(patternString)))

   def walk(self, dirIgnores=[], fileIgnores=[]):
      """
         @param dirIgnores
          This is a list of regular expressions which will be used to test the
          directories and to remove ones that we do not wish to walk over.

         @param fileIgnores
           If a file matches any of these patterns then do not yield it.

      """
      dirIgnores = dirIgnores[:]
      dirIgnores.extend(self.dirIgnores_)

      for root, dirs, files in os.walk(self.path_):

         if not self.recursive_:
            dirs[:] = []

         dirsCopy = dirs[:]
         for d in dirsCopy:
            fullDir = os.path.join(root, d)
            for i in dirIgnores:
               if i.search(fullDir):
                  dirs.remove(d)

         for f in files:
            if len(fileIgnores) == 0:
               yield os.path.join(root, f)
            else:
               for i in fileIgnores:
                  if not i.search(f):
                     yield os.path.join(root, f)
