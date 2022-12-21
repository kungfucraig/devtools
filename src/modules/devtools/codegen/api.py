"""
This files contains the classes: Generator, Template, and Module

Copyright (C) 2009
by Craig W. Wright <kungfucraig@gmail.com>

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
from optparse import OptionParser, OptionValueError
from devtools.codegen.configuration import Configuration


def cg_main():
   """
      This is the main line of the script cg and cg.cmd.
      It is put here so that Linux and Windows versions can share.
   """


   def variableMapCallback(option, opt_str, value, parser):
      """
      Helper function taken almost verbatim from optparse documentation.
      """
      assert value is None
      value = []

      def floatable(str):
         try:
            float(str)
            return True
         except ValueError:
            return False
      for arg in parser.rargs:
         # stop on --foo like options
         if arg[:2] == "--" and len(arg) > 2:
            break
         # stop on -a, but not on -3 or -3.0
         if arg[:1] == "-" and len(arg) > 1 and not floatable(arg):
            break
         value.append(arg)

      del parser.rargs[:len(value)]

      localVariables = {}
      for v in value:
         fields = v.split("=")
         if len(fields) == 1:
            localVariables[fields[0]]=""
         elif len(fields) == 2:
            localVariables[fields[0]] = fields[1]
         else:
            localVariables[fields[0]] = "=".join(fields[1:])

      setattr(parser.values, option.dest, localVariables)


   VERSION="0.1"

   conf = Configuration()

   usage = "usage: %prog [<generator>|-h|--version|-m]"
   version = "%prog " + VERSION
   description="With no options the given generator name will be referenced to a generator (template) of the same name in your codegen configuration file. That generator will then be executed. Output is written to stdout."

   parser = OptionParser(usage=usage, version=version, description=description)


   parser.add_option("-m",
                     "--variable-map",
                     dest="varmap",
                     action="callback",
                     callback=variableMapCallback,
                     help="A list of key value pairs which will define current use variables for the generator. For example '-m foo=bar classname=NewClass filename=Foo.h'.")

   (options, args) = parser.parse_args(sys.argv[1:])

   try:
      if len(args) == 1:
         ch = conf.getGenerator(args[0])
         vs = conf.getVariables(options.varmap)
         ch.generate(vs)
      else:
         sys.stderr.write(parser.format_help())
         sys.exit(1)
   except KeyboardInterrupt as k:
      pass
   except:
      raise
 

