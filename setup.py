#!/usr/bin/env python
import os
import setuptools
from distutils.util import convert_path

NAME     = 'nclColorTables'
DESC     = "Package to download NCL color tables"

main_ns  = {};
ver_path = convert_path( os.path.join( NAME, "version.py") )
with open(ver_path) as ver_file:
  exec(ver_file.read(), main_ns);

setuptools.setup(
  name             = NAME,
  description      = DESC,
  url              = "https://github.tamu.edu/wodzicki/"+NAME,
  author           = "Kyle R. Wodzicki",
  author_email     = "wodzicki@tamu.edu",
  version          = main_ns['__version__'],
  packages         = setuptools.find_packages(),
  install_requires = [ "bs4", "lxml", "numpy" ],
  scripts          = ["./bin/get_ncl_colortables"],
  zip_safe         = False
);
