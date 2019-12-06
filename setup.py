#!/usr/bin/env python
from setuptools import setup, find_packages
import os


data_files = [(d, [os.path.join(d, f) for f in files])
              for d, folders, files in os.walk(os.path.join('src', 'config'))]


setup(name='splunk-connector',
      version='1.0',
      description='execute splunk queries and format data for passing',
      author='Adam Pridgen',
      author_email='adpridge@cisco.com',
      install_requires=['splunk-sdk', 'tabulate', 'toml', 'pymongo', 'pycrypto', 'docker'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
)
