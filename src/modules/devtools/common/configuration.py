"""
This files defines the class Configuration in the common module.
It abstracts out some configuration issues for the various tools.

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
import os
import platform

from devtools.common.option import Option

class Configuration:
   """
      This serves as a base class for the Configuration classes for the various
      tools.
   """

   def __init__(self, configurationDirectory, configurationFile, createConfigurationFile, configurationFileTemplate):

      if platform.system() == "Windows":
         self.configurationDirectory_ = os.path.join(os.environ["APPDATA"], "devtools")
      else:
         self.configurationDirectory_ = os.path.join(os.environ["HOME"], ".devtools")

      if configurationDirectory:
         self.configurationDirectory_ = str(configurationDirectory)

      self.configurationFile_ = str(configurationFile)

      self.createConfigurationFile_ = createConfigurationFile
      self.template_ = configurationFileTemplate
      self.options_ = {}
     
   def getConfigurationDirectory(self):
      """
         Get the directory where all of the configuration data lives.
      """
      return self.configurationDirectory_;

   def getConfigurationFile(self):
      """
         Get the base name of the configuration file.
      """
      return self.configurationFile_

   def getConfigurationFileFullPath(self):
      """
         Get the full path to the location table.
      """
      return os.path.join(
         self.getConfigurationDirectory(),
         self.configurationFile_)

   def configurationFileExists(self):
      """
         Return true if the configuration file exists and
         false otherwise.
      """
      return os.path.exists(self.getConfigurationFileFullPath()); 

   def conditionallyCreateConfigurationFile(self):
      """
         If the member variable createConfigurationFile_ is True
         and the configuration file does not exist then it will be
         created and its contents will be whatever is in the variable
         'self.template_'.
      """
      if self.createConfigurationFile_ and os.path.exists(self.getConfigurationFileFullPath()) == False:
         if os.path.exists(self.getConfigurationDirectory()) == False:
            os.mkdir(self.getConfigurationDirectory())
         self.createSampleConfigurationFile(self.getConfigurationFileFullPath());

   def createSampleConfigurationFile(self, path):
      """
         Create a sample configuration file at location "path" with content "self.template".
         If the file specified already exists raise an exception.
      """
      if os.path.exists(path):
         raise RuntimeError("Failed to create a sample configuration file because the file: '" + path + "' already exists.")

      sc = open(path, "w")
      try:
         sc.write(str(self.template_))
      finally:
         sc.close()

   def clearOptions(self):
      """
         Remove all options.
      """
      self.options_ = {}

   def addOption(self, option):
      """
         Put the given option in the option dictionary. If the option already exists
         throw an error.
      """
      if not isinstance(option, Option):
         raise ValueError("Expected an object of type Option as an input.")
      if self.options_.has_key(option.getKey()):
         raise RuntimeError("The option '" + option.getKey() + "' already exists.")
      self.options_[option.getKey()] = option


   def setOption(self, key, value):
      """
         Given a key look it up in the option dictionary. If it's not there raise
         an error. If it is there call its setValue method with the second argument
         'value'.
      """
      o = self.getOption(key)
      o.setValue(value)

   def setDefaultOptions(self):
      """
         This method will be overridden by derived classes, and is here
         only to ensure consistency of interface.
      """
      pass

   def getOption(self, key):
      """
         Given a key look it up in the option dictionary. If the option does not
         exist raise an error, otherwise return the option.
      """
      return self.options_[str(key)]

   def getOptionValue(self, key):
      """
         @see getOption, but instead of returning the Option, return Option.getValue()
      """
      return self.getOption(key).getValue()


