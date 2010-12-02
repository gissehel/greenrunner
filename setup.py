#!/usr/bin/env python
from distutils.core import setup
import sys
# import os
# import yaml

setup(
    console=['greenrunner.py'],
    options={
        'py2exe' : {
        'includes' : [
            ]
        },
        },
    )
