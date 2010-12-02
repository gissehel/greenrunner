#!/usr/bin/env python
from distutils.core import setup
import sys

DIST_PATH = r'bin'

sys.argv = [sys.argv[0],]
sys.argv += ['py2exe','--dist-dir',DIST_PATH]

import setup

