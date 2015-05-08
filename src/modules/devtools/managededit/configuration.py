"""
This files defines the class Configuration.

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
import xml.parsers.expat
import re
import sys

import devtools.common.configuration
import devtools.common.utility
from devtools.common.option import *

from devtools.managededit.searchpath import SearchPath

class Configuration(devtools.common.configuration.Configuration):
   """
   Given a Managed Edit configuration file, read it in
   and provide programatic access to its contents.

   If the environment variable EDITOR is defined use it
   as the editor.
   """

   sampleConfigurationFile_ = """<ManagedEditConfiguration>

   <Options>
      <!--
         The default value for the option is given.
         For true/false options, only true or false are accepted as
         values.
      -->
      <Option key="searchCurrentWorkingDirectory" value="false"/>
   </Options>

   <GlobalIgnores>
      <!--
      <DirectoryIgnore pattern="\.svn"/>
      <FileIgnore pattern="\.pyc"/>
      <FileIgnore pattern="\.exe"/>
      <FileIgnore pattern="\.dll"/>
      <FileIgnore pattern="\.pdb"/>
      <FileIgnore pattern="\.ilk"/>
      -->
   </GlobalIgnores>

   <SearchPaths>
      <!--
      <SearchPath path="${HOME}" recursive="true"/>
      <SearchPath path="" recursive="true|false"/>
      -->
   </SearchPaths>
</ManagedEditConfiguration>
"""

   def __init__(self, configurationDirectory, createConfigurationFile):
      """
         @param configurationDirectory
         The directory that the configuration lives in.

         @param createConfigurationFile
         Create the config file if it does not exist.
      """
      devtools.common.configuration.Configuration.__init__(
            self,
            configurationDirectory,
            "managededit.conf",
            createConfigurationFile,
            self.sampleConfigurationFile_)

      self.searchPaths_ = set()
      self.fileIgnores_ = []
      self.dirIgnores_ = []

      self.setDefaultOptions()

      self.editor_ = None
      if os.environ.has_key("EDITOR"):
         self.editor_ = os.environ["EDITOR"]

      self.locationTableFile_ = "location_table"

      # Create the configuration file.
      self.conditionallyCreateConfigurationFile()

      if os.path.exists(self.getConfigurationFileFullPath()):
         p = ConfigurationFileParser(self)
         p.parse(self.getConfigurationFileFullPath())

   def getEditor(self):
      """
         Get the editor to use.
      """
      return self.editor_

   def getLocationTableFile(self):
      """
         Get the base name of the location table file.
      """
      return self.locationTableFile_

   def getLocationTableFileFullPath(self):
      """
         Get the full path to the location table.
      """
      return os.path.join(
         self.getConfigurationDirectory(),
         self.locationTableFile_)

   def addSearchPath(self, searchpath):
      self.searchPaths_.add(searchpath)

   def getSearchPaths(self):
      return self.searchPaths_

   def addFileIgnore(self, patternString):
      self.fileIgnores_.append(re.compile(str(patternString)))

   def getFileIgnores(self):
      return self.fileIgnores_

   def addDirectoryIgnore(self, patternString):
     self.dirIgnores_.append(re.compile(devtools.common.utility.substituteEnvironment(patternString)))

   def getDirectoryIgnores(self):
      return self.dirIgnores_

   def setDefaultOptions(self):
       """
          searchCurrentWorkingDirectory=False
       """
       self.clearOptions()
       self.addOption(BooleanOption("searchCurrentWorkingDirectory", False))


class ConfigurationFileParser:
   """
      Given a config file and a Configuration, process the config
      file and modify the configuration to reflect its contents.
   """
   IN_OPTIONS=1
   IN_GLOBAL_IGNORES=2
   IN_SEARCHPATHS=3

   def __init__(self, configuration):
      if not isinstance(configuration, Configuration):
         raise RuntimeError("Expected a Configuration as the first argument.")
      self.configuration_ = configuration
      self.reset()

   def reset(self):
      self.state_ = None
      self.currentSearchPath_ = None

   def parse(self, filename):
      p = xml.parsers.expat.ParserCreate()
      p.StartElementHandler = self.startElement
      p.EndElementHandler = self.endElement

      f = open(filename)

      try:
         p.ParseFile(f)
      finally:
         f.close()

   def startElement(self, name, attrs):
      if name == "Options":
         self.handleStateTransition(self.IN_OPTIONS)
      elif name == "GlobalIgnores":
         self.handleStateTransition(self.IN_GLOBAL_IGNORES)
      elif name == "SearchPaths":
         self.handleStateTransition(self.IN_SEARCHPATHS)
      elif name == "Option":
         self.handleOption(attrs)
      elif name == "FileIgnore":
         self.handleFileIgnore(attrs)
      elif name == "DirectoryIgnore":
         self.handleDirectoryIgnore(attrs)
      elif name == "SearchPath":
         self.handleSearchPath(attrs)
      elif name == "ManagedEditConfiguration":
         pass
      elif name == "LocalIgnores":
         pass
      else:
         raise RuntimeError("Unknown element: '" + name + "'")

   def endElement(self, name):
      if name == "Options" or name == "GlobalIgnores" or name == "SearchPaths":
         self.state_ = None
      elif name == "SearchPath":
         self.currentSearchPath_ = None

   def handleStateTransition(self, newstate):
      if self.state_ != None:
         raise RuntimeError("Expected empty state, found: '" + str(self.state_) + "'")
      self.state_ = newstate

   def handleOption(self, attrs):
      if not attrs.has_key('key'):
         raise RuntimeError("Option element has no attribute 'key'.")
      if not attrs.has_key('value'):
         raise RuntimeError("Option element has no attribute 'value'.")

      key=attrs['key']
      value=attrs['value']
      self.configuration_.setOption(key, value)

   def handleFileIgnore(self, attrs):
      if not attrs.has_key('pattern'):
         raise RuntimeError("IgnoreFile element has no attribute 'pattern'.")
      pattern = attrs['pattern']

      if self.state_ == self.IN_GLOBAL_IGNORES:
         self.configuration_.addFileIgnore(pattern)

      elif self.state_ == self.IN_SEARCHPATHS and self.currentSearchPath_:
         sys.stderr.write("SearchPath file ignores are not implemented.\n")

      else:
         raise RuntimeError("Misplaced SearchPath element.")

   def handleDirectoryIgnore(self, attrs):
      """
         There should be a way to combine this code with
         the code in handleFileIgnore
      """
      if not attrs.has_key('pattern'):
         raise RuntimeError("IgnoreDirectory element has no attribute 'pattern'.")
      pattern = attrs['pattern']

      if self.state_ == self.IN_GLOBAL_IGNORES:
         self.configuration_.addDirectoryIgnore(pattern)

      elif self.state_ == self.IN_SEARCHPATHS and self.currentSearchPath_:
         self.currentSearchPath_.addDirectoryIgnore(pattern)

      else:
         raise RuntimeError("Misplaced SearchPath element.")


   def handleSearchPath(self, attrs):
      if not attrs.has_key('path'):
         raise RuntimeError("SearchPath element has no attribute 'path'.")
      if not self.IN_SEARCHPATHS:
         raise RuntimeError("SearchPath elements must be nested in the 'SearchPaths' tag.")
      path = attrs['path']
      recursive = False
      if attrs.has_key('recursive'):
         rval = attrs['recursive']
         if rval == "true":
            recursive = True
         elif rval == "false":
            recursive = False
         else:
            raise RuntimeError("Expected the attribute 'recursive' of a SearchPath element to have the value 'true' or 'false'.")

      self.currentSearchPath_ = SearchPath(path, recursive)
      self.configuration_.addSearchPath(self.currentSearchPath_)
