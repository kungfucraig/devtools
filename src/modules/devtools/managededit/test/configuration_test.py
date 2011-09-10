#!/usr/bin/python

import os
import unittest
import tempfile

from devtools.managededit.configuration import *

class ConfigurationTest(unittest.TestCase):

   def setUp(self):
      self.testEditorName_ = "editor"
      self.confDir_ = os.path.join(tempfile.gettempdir(), "meconftest")  

      if os.path.exists(self.confDir_):
         os.removedirs(self.confDir_)
      os.makedirs(self.confDir_)

      os.environ["EDITOR"] = "" 
      os.environ.pop("EDITOR")
      self.c1_ = Configuration(self.confDir_, False)
   
      os.environ["EDITOR"] = self.testEditorName_
      self.c2_ = Configuration(self.confDir_, False)

   def removeConfDir(self, name):
      for root, dirs, files in os.walk(self.confDir_,False):
         for f in files:
            os.remove(os.path.join(root, f))
         for d in dirs:
            os.rmdir(os.path.join(root, d))
      if os.path.exists(name):
         os.rmdir(name)

   def tearDown(self):
      self.removeConfDir(self.confDir_)

   def testC1(self):
      self.assert_(self.c1_.getEditor() == None)

   def testC2(self):
      self.assert_(self.c2_.getEditor() == self.testEditorName_)
      self.assert_(self.c2_.getConfigurationDirectory()
                   ==
                   self.confDir_)
      self.assert_(self.c2_.getLocationTableFile()
                   ==
                   "location_table")
      self.assert_(self.c2_.getLocationTableFileFullPath()
                   ==
                   os.path.join(self.c2_.getConfigurationDirectory(),
                                self.c2_.getLocationTableFile()))
      self.assert_(self.c2_.getConfigurationFile()
                   ==
                   "managededit.conf")
      self.assert_(self.c2_.getConfigurationFileFullPath()
                   ==
                   os.path.join(self.c2_.getConfigurationDirectory(),
                                self.c2_.getConfigurationFile()))

   def testConfigurationFileOperations(self):
      """
         Does the config file exist, and can we create it? 
      """
      self.removeConfDir(self.confDir_)
      os.mkdir(self.c2_.getConfigurationDirectory())

      self.assert_(self.c2_.configurationFileExists() == False)
      self.c2_.createSampleConfigurationFile(self.c2_.getConfigurationFileFullPath())

      self.assert_(self.c2_.configurationFileExists() == True)

      os.remove(self.c2_.getConfigurationFileFullPath())
      self.removeConfDir(self.c2_.getConfigurationDirectory())

      # have it make its own config file.
      c3 = Configuration(self.confDir_, True)
      self.assert_(self.c2_.configurationFileExists() == True)

      # Now find out what happens when this is true, but the file already exists.
      c4 = Configuration(self.confDir_, True)

      # And when it's false
      c5 = Configuration(self.confDir_, False)
   
      os.remove(self.c2_.getConfigurationFileFullPath())
      self.removeConfDir(self.c2_.getConfigurationDirectory())
      


if __name__ == "__main__":
   unittest.main()
