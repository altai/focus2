import os
import sys


__version__ = '0.0.1'

from setuptools import setup, find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(name='focus2',
      version=__import__('focus2').__version__,
      license='GNU LGPL 2.1',
      description='Web UI for Altai Private Cloud for Developers',
      author='GridDynamics Openstack Core Team, (c) GridDynamics',
      author_email='openstack@griddynamics.com',
      url='http://www.griddynamics.com/openstack',

      zip_safe=False,
      platforms='any',

      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      test_suite='tests',
      long_description=read('README.rst'),
      install_requires=[
        'Flask==0.9',
        'Flask-WTF==0.8'],
      tests_require=['mox'],
      classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
       'Programming Language :: Python :: 2.6',
        ]
      )
