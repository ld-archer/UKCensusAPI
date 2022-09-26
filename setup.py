#!/usr/bin/env python3

import setuptools

def readme():
  with open('README.md') as f:
    return f.read()

def read_reqs():
 with open('requirements.txt') as f:
   return [pkg.rstrip('\n') for pkg in f]

setuptools.setup(name='ukcensusapi',
  version='1.1.6',
  description='UK census data query automation',
  long_description=readme(),
  long_description_content_type="text/markdown",
  url='https://github.com/virgesmith/UKCensusAPI',
  author='Andrew P Smith',
  author_email='a.p.smith@leeds.ac.uk',
  packages=setuptools.find_packages(),
  install_requires=read_reqs(),
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ),
  scripts=['inst/scripts/ukcensus-query'],
  tests_require=['pytest'],
)
