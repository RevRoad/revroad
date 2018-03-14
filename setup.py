#!/usr/bin/env python

from setuptools import setup, find_packages

dependencies = [
    'boto3>=1.4.6',
    'google-api-python-client>=1.6.4',
    'requests>=2.18.4',
    'Django>=2.0.0',
    'Pillow>=5.0.0',
]

setup(name='revroad',
      version='1.0',
      description='RevRoad Shared Utilities',
      author='RevRoad',
      author_email='developer@revroad.com',
      url='https://www.revroad.com',
      packages=find_packages(),
      install_requires=dependencies,
     )