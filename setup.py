#!/usr/bin/env python
# -*- coding: utf8 -*-

"""setup.py file for samiTools."""

# Import required modules
from distutils.core import setup
from setuptools import setup, find_packages

print(str(find_packages()))
setup(name='samiTools',
      version='1.0.0',
      author='Victoria Morris',
      author_email='victoria.morris@bl.uk',
      license='MIT License',
      description='Tools for working with SAMI files.',
      long_description=
      '''Tools for working with SAMI files.''',
      packages=find_packages(),
      platforms=['any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python'
          'Topic :: Scientific/Engineering :: Information Science',
          'Topic :: Text Processing'
      ],
      url='https://github.com/victoriamorris/samiTools',
      requires=['setuptools', 'regex']
      )
