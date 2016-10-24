#!/usr/bin/env

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
  'description': 'South',
  'author': 'Antoine Neuenschwander',
  'url': 'https://twitter.com/sued_anfluege',
  'download_url': '',
  'author_email': 'antoine@schoggi.org',
  'version': '0.1',
  'install_requires': [
     'nose', 'requests', 'tweepy', 'expiringdict',
     'bunch', 'couchdbkit', 'PyYAML'],
  'packages': ['south'],
  'scripts': [],
  'entry_points': {
    'console_scripts': ['south=south.__main__:main']
  },
  'name': 'South'
}

setup(**config)
