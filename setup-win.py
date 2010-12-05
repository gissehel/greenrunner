#!/usr/bin/env python
from distutils.core import setup
from babel.messages import frontend as babel
import sys
import py2exe
from setup import setup_args, setup
# import os
# import yaml

DIST_PATH = r'bin'

if len(sys.argv) == 1 :
    sys.argv = [sys.argv[0],]
    sys.argv += ['py2exe','--dist-dir',DIST_PATH]

setup_args['console'] = ['greenrunner.py']

if __name__=='__main__' :
    setup(**setup_args)
