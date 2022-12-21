from distutils.core import setup
import platform

if platform.system() == "Windows":
   scriptsToInstall=['src/scripts/me.cmd', 'src/scripts/cg.cmd']
else:
   scriptsToInstall=['src/scripts/me', 'src/scripts/cg']

print(scriptsToInstall)

setup(name="devtools",
      version="0.1",
      description="A set of utilities that aid in the development of other software.",
      author="Craig W. Wright",
      author_email="kungfucraig@gmail.com",
      url="http://craigwwright.wordpress.com/devtools",
      packages=["devtools"],
      package_dir={'devtools': "src/modules/devtools"},
      package_data={"devtools" : ['common/*.py', 'managededit/*.py', 'codegen/*.py']},
      scripts=scriptsToInstall,
     )
