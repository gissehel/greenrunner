#!/usr/bin/env python
from distutils.core import setup
from babel.messages import frontend as babel
import sys
# import os
# import yaml

setup(
    # console=['greenrunner.py'],
    name='greenrunner',
    version='0.99',
    description='Run a set of green paper page alredy included in a greenpepper labels page, and generate a report that can be archived',
    url='http://code.google.com/p/greenrunner/',
    author='Gissehel',
    author_email='dist-greenrunner@gissehel.org',
    scripts=['greenrunner.py'],
    packages=['web','webrip','greenrunnerlib'],
    options={
        },
    cmdclass = {'compile_catalog': babel.compile_catalog,
                'extract_messages': babel.extract_messages,
                'init_catalog': babel.init_catalog,
                'update_catalog': babel.update_catalog},
    message_extractors = {
        '': [
            ('**.py',                'python', None),
            ],
        },
    data_files=[('locale/fr_FR/LC_MESSAGES', ['locale/fr_FR/LC_MESSAGES/greenrunner.mo'])],

    )
