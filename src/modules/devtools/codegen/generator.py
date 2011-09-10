"""
This files contains the classes: Generator, Template, and Module

Copyright (C) 2009 Craig W. Wright

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
import sys
import datetime
import string

import devtools.common.utility

class Generator:
   """
      A base class code generator.
   """
   def __init__(self, name):
      self.name_ = devtools.common.utility.substituteEnvironment(name)

   def getName(self):
      return self.name_

   def generate(self, variables):
      """
         Derived classes should implement this.
      """
      pass


class Template(Generator):
   """
      A Template is simply an object that has a key and points to a text file
      on disk. That file can contain anything, but ideally it has references to
      variables, which this class will dereference. It will then parameterized text.
   """
   def __init__(self, name, templateFile):
      Generator.__init__(self, name)
      self.file_= devtools.common.utility.substituteEnvironment(templateFile)

   def generate(self, variables):
      f = open(self.file_)
      s = ""
      try:
         for l in f.readlines():
            s += l
      finally:
         f.close()

      s = string.Template(s)
      s = s.safe_substitute(variables)
      sys.stdout.write(s)
