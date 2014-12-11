#!/usr/bin/env python2.6

import os
import setuptools


def find_files(path):
  return [os.path.join(path, f) for f in os.listdir(path)]


setuptools.setup(
  name='workspace-tools',
  version='0.1.0b',

  author='Max Zheng',
  author_email='mzheng@linkedin.com',

  description=open('README.md').read(),

  install_requires=[
    'brownie',
    'subprocess32',
  ],

  license='MIT',

  package_dir={'': 'src'},
  packages=setuptools.find_packages('src'),
  include_package_data=True,

  setup_requires=['setuptools-git'],

  scripts=find_files('bin'),

  classifiers=[
    'Development Status :: 4 - Beta',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Development Tools',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],

  keywords='git svn scm development tools',
)