"""
This files defines the class Option and several subclasses.

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

class Option:
   """
      Options are used by a Configuration to convey some information about
      how a particular utility is to behave.

      An option has a string key and a value of a type that is determined
      by the particular subclass.
   """

   def __init__(self, key, value):
      """
         @param key
          Always interpreted as a string.

         @param value
          Always taken as is.
      """

      self.key_ = str(key)
      self.value_ = value

   def getKey(self):
      return self.key_

   def getValue(self):
      return self.value_

   def setValue(self, value):
      raise RuntimeError("Unable to call setValue on base class Option.")


class BooleanOption(Option):
   """
      An option with a BooleanValue
   """

   def __init__(self, key, value):
      """
         @param value @see setValue
      """
      Option.__init__(self, key, None)
      self.setValue(value)

   def setValue(self, value):
      """
          @param
          If this argument is a string then it may
          have one of the casen-insensitive values
          "true" or "false". This will be interpreted as
          True or False (duh). Any other string value triggers
          an exception. Otherwise this argument is handed to the
          function 'bool'.
      """
      actualValue = bool(value)
      if isinstance(value, str):
         svalue = value.lower()
         if svalue == "true":
            actualValue = True
         elif svalue == "false":
            actualValue = False
         else:
            raise ValueError("The BooleanOption '" + self.getKey() + "' requires a string value of 'true' or 'false'.")
      self.value_ = actualValue


class StringOption(Option):
   """
      An option with a StringValue 
   """

   def __init__(self, key, value):
      """
         @param value @see setValue
      """
      Option.__init__(self, key, None)
      self.setValue(str(value))

   def setValue(self, value):
      """
         We try to turn the given value to a string.
      """
      self.value_ = str(value)


 
       

