"""
Define various utility routines

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

import string
import os

def substituteEnvironment(templateString):
   """
      Given a string with embedded environment variables such as: "${HOME}/xxxx",
      substitute the appropriate environment variables using string.Template.
   """
   template = string.Template(str(templateString))
   return template.safe_substitute(os.environ)

 
