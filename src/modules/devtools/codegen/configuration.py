"""
This files defines the class Configuration for codegen.

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
import string
import copy
from datetime import datetime

import devtools.common.configuration
from devtools.common.option import *
from devtools.codegen.generator import *


class Configuration(devtools.common.configuration.Configuration):
   """
   Given a CodeGen configuration file, read it in
   and provide programatic access to its contents.

   The configuration is constructed with several default variables:
      @see getVariables
   """

   sampleConfigurationFile_ = """<CodeGenConfiguration>

   <Options>
      <!--
         The default value for the option is given.
         For true/false options, only true or false are accepted as
         values.

         For datetime, date, and time format possibilities, see the
         python reference for datetime.

         <Option key="datetimeformat" value="%Y-%m-%d %H:%M:%S"/>
         <Option key="dateformat" value="%Y-%m-%d"/>
         <Option key="timeformat" value="%H:%M:%S"/>
      -->
   </Options>

   <Variables>
      <!--
        The following default variables are predefined:
           year (YYYY), month (MM), day (DD), datetime, date, and time.

        Here are some examples of a custom variables:
           <Variable key="email" value="me@frop.org"/>
           <Variable key="me" value="Whoever I Am"/>
           <Variable key="foo" value="bar"/>
      -->
   </Variables>

   <Generators>
      <!--
         This is an example template definition. ${VARIABLE} refers to
         an environment variable.
         <Template name="ch" path="${HOME}/path/to/cppInclude.template"/>
      -->
   </Generators>
</CodeGenConfiguration>
"""

   def __init__(self, configurationDirectory=None, createConfigurationFile=True):
      """
         @param configurationDirectory
         The directory that the configuration lives in.
         Or None to use the default.

         @param createConfigurationFile
         Create the config file if it does not exist.

      """
      devtools.common.configuration.Configuration.__init__(
            self,
            configurationDirectory,
            "codegen.conf",
            createConfigurationFile,
            self.sampleConfigurationFile_)

      self.generators_ = {}
      self.variables_ = {}

      self.setDefaultOptions()


      # Create the configuration file.
      self.conditionallyCreateConfigurationFile()

      if os.path.exists(self.getConfigurationFileFullPath()):
         p = ConfigurationFileParser(self)
         p.parse(self.getConfigurationFileFullPath())

   def addGenerator(self, generator):
      if generator.getName() in self.generators_:
         raise ValueError("A Generator with the name: '" + self.generator_.getName() + "' already exists.")
      self.generators_[generator.getName()] = generator;

   def getGenerator(self, name):
      name = str(name)
      if name not in self.generators_:
         raise ValueError("Unknown generator: '" + name + "'.")
      return self.generators_[name]

   def setDefaultOptions(self):
       """
       """
       self.addOption(StringOption("datetimeformat", "%Y-%m-%d %H:%M:%S"))
       self.addOption(StringOption("dateformat", "%Y-%m-%d"))
       self.addOption(StringOption("timeformat", "%H:%M:%S"))

   def getVariables(self, localVariables):
      """
         Return a copy of the variable map.

         The variable map includes datetime variables (year, month, day, date, time, datetime),
         the entire content of the environment (os.environ), and the variables defined in the code
         gen config file. The order of precedence is the order stated in the previous sentence.

         \param [in] localVariables
         This is a map of keys to values and will be included in the returned
         variable map. These take ultimate precendence.
      """
      variables = {}

      # Default are lowest precedence.
      now = datetime.datetime.now()
      variables["year"] = now.year
      variables["month"] = now.month
      variables["day"] = now.day
      variables["date"] = now.strftime(self.getOption("dateformat").getValue())
      variables["time"] = now.strftime(self.getOption("timeformat").getValue())
      variables["datetime"] = now.strftime(self.getOption("datetimeformat").getValue())

      # Next is the environment.
      for k,v in list(os.environ.items()):
         variables[k] = v

      # Finally user variables.
      for k,v in list(self.variables_.items()):
         variables[k] = v

      if localVariables:
         for k,v in list(localVariables.items()):
            variables[k] = v

      return variables

   def setVariable(self, key, value):
      self.variables_[key] = value


class ConfigurationFileParser:
   """
      Given a config file and a Configuration, process the config
      file and modify the configuration to reflect its contents.
   """
   IN_OPTIONS=1
   IN_GENERATORS=2
   IN_VARIABLES=2

   def __init__(self, configuration):
      if not isinstance(configuration, Configuration):
         raise RuntimeError("Expected a Configuration as the first argument.")
      self.configuration_ = configuration
      self.reset()

   def reset(self):
      self.state_ = None

   def parse(self, filename):
      p = xml.parsers.expat.ParserCreate()
      p.StartElementHandler = self.startElement
      p.EndElementHandler = self.endElement

      f = open(filename, 'rb')

      try:
         p.ParseFile(f)
      finally:
         f.close()

   def startElement(self, name, attrs):
      if name == "Options":
         self.handleStateTransition(self.IN_OPTIONS)
      elif name == "Generators":
         self.handleStateTransition(self.IN_GENERATORS)
      elif name == "Variables":
         self.handleStateTransition(self.IN_VARIABLES)
      elif name == "Option":
         self.handleOption(attrs)
      elif name == "Template":
         self.handleTemplate(attrs)
      elif name == "Variable":
         self.handleVariable(attrs)
      elif name == "CodeGenConfiguration":
         pass
      else:
         raise RuntimeError("Unknown element: '" + name + "'")

   def endElement(self, name):
      if name == "Options" or name == "Generators" or name == "Variables":
         self.state_ = None

   def handleStateTransition(self, newstate):
      if self.state_ != None:
         raise RuntimeError("Expected empty state, found: '" + str(self.state_) + "'")
      self.state_ = newstate

   def handleOption(self, attrs):
      if 'key' not in attrs:
         raise RuntimeError("Option element has no attribute 'key'.")
      if 'value' not in attrs:
         raise RuntimeError("Option element has no attribute 'value'.")

      key=attrs['key']
      value=attrs['value']
      self.configuration_.setOption(key, value)

   def handleTemplate(self, attrs):
      if 'name' not in attrs:
         raise RuntimeError("Option element has no attribute 'name'.")
      if 'path' not in attrs:
         raise RuntimeError("Option element has no attribute 'path'.")

      t = Template(attrs['name'], attrs['path'])
      self.configuration_.addGenerator(t)

   def handleVariable(self, attrs):
      if 'key' not in attrs:
         raise RuntimeError("Variable element has no attribute 'key'.")
      if 'value' not in attrs:
         raise RuntimeError("Variable element has no attribute 'value'.")

      self.configuration_.setVariable(attrs['key'], attrs['value'])
