"""
This files defines some API functions.

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

from devtools.managededit.locationtable import *

import sys
import subprocess
import platform

from optparse import OptionParser
from devtools.managededit.configuration import Configuration

if platform.system() != "Windows":
   import readline

def me_main():
   """
      This is the main line of the scripts me and me.cmd.
      Put here for sharing.
   """
   VERSION="0.1"
   conf = Configuration(None, True)

   usage = "usage: %prog [-r|-d <expression>|-f <expression>|<expression>|-h|--version]"
   version = "%prog " + VERSION
   description=("With no options the given expression will be used to search the location table located at '%s'. An interactive process of narrowing the expression to a single file will then begin and if a single file is indicated it will be launched in $EDITOR.") % (conf.getLocationTableFileFullPath())

   parser = OptionParser(usage=usage, version=version, description=description)
   parser.add_option("-r",
                     "--rebuild-locationtable",
                     action="store_true",
                     dest="rebuild_locationtable",
                     help="Rebuild the location table and exit.")

   parser.add_option("-l",
                     "--dump-locationtable",
                     action="store_true",
                     dest="dump_locationtable",
                     help="Dump the contents of the location table to stdout and exit.")

   parser.add_option("-d",
                     "--find-directory",
                     action="store",
                     dest="directoryExpression",
                     help="Given an expression invoke the interactive narrowing process to allow the selection of a unique directory. Once a unique directory is found print the directory in which the file(s) reside to stdout.")

   parser.add_option("-f",
                     "--find-file",
                     action="store",
                     dest="fileExpression",
                     help="Given an expression invoke the interactive narrowing process to allow the selection of a unique file. Once a unique file is found print the full path for the file to stdout.")



   (options, args) = parser.parse_args(sys.argv[1:])

   #print options, args

   try:
      if options.rebuild_locationtable:
         sys.stdout.write("Rebuilding the location table...")
         sys.stdout.flush()
         n = rebuildLocationTable(conf)
         sys.stdout.write(" " + str(n) + " files indexed.\n")
      elif options.dump_locationtable:
         dumpLocationTable(conf, sys.stdout)
      elif options.directoryExpression:
         location = findDirectory(conf, options.directoryExpression)
         if location:
            sys.stdout.write(location + "\n")
      elif options.fileExpression:
         location = findFile(conf, options.fileExpression)
         if location:
            sys.stdout.write(location + "\n")
      elif len(args) == 1:
         editFile(conf, args[0])
      else:
         sys.stderr.write(parser.format_help())
         sys.exit(1)
   except KeyboardInterrupt, k:
      pass
   except:
      raise


def rebuildLocationTable(configuration):
   """Rebuild the location table

      @returns The length of the location table.
   """
   lt = LocationTable(configuration)
   lt.rebuild()
   return len(lt)


def dumpLocationTable(configuration, fileobject):
   """Dump the location table to stdout.

      @param fileobject
      An object that supports the write method.
   """
   lt = LocationTable(configuration)
   lt.dump(fileobject)


def findRecord(configuration, pattern):
   """Find the record tuple given a pattern."""
   lt = LocationTable(configuration)
   res = lt.search(str(pattern))

   while len(res) > 1:
      res.list()
      sys.stderr.write("> ")
      criteria = raw_input()
      res.narrow(criteria)

   if len(res) == 1:
      return res[0]
   else:
      return None


def findDirectory(configuration, pattern):
   """Given a pattern call find record, but just return the
      directory that the file associated with the record is in.
   """
   lt = LocationTable(configuration)
   res = lt.search(str(pattern))

   while not res.getCommonDirectory() and len(res):
      res.list()
      sys.stderr.write("> ")
      criteria = raw_input()
      res.narrow(criteria)

   return os.path.dirname(res[0][1]) if len(res) else None


def findFile(configuration, pattern):
   """Given a pattern call find record. Then return the
      full path that the file associated with the record is in.
   """
   r = findRecord(configuration, pattern)
   if not r:
      return None
   else:
      return r[1]


def editFile(configuration, pattern):
   """Given a pattern call find record. Then use the return directory
      and invoke the editor stored in the configuration.
   """
   f = findFile(configuration, pattern)
   if f:
      command = configuration.getEditor() + ' "' + f + '"'
      subprocess.Popen(command, shell=True)
