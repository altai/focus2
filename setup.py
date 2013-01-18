#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


import os
import pdb
import re
import shlex
import subprocess
import sys

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as original_build_py


class build_py(original_build_py):
    def _get_data_files(self):
        """
        Remove HAML belonging to Focus2, add HTML files instead.
        """
        data = original_build_py._get_data_files(self)
        package = 'focus2'
        src_dir = self.get_package_dir(package)
        build_dir = os.path.join(*([self.build_lib] + package.split('.')))
        plen = len(src_dir) + 1

        filenames = []
        for arg, dirname, names in os.walk(os.path.join(src_dir, 'templates')):
            for name in names:
                if name.endswith('haml'):
                    input_file = os.path.join(arg, name)
                    output_file = os.path.join(
                        arg, re.sub('.haml$', '.html', name))
                    command = 'haml --format html5 {0} {1}'.format(input_file,
                                                                   output_file)
                    print command
                    popen_args = shlex.split(command)
                    subprocess.call(popen_args)
                    filenames.append(output_file)
        plen = len(src_dir) + 1
        filenames = [
            file[plen:] for file in filenames
        ]
        data.append((package, src_dir, build_dir, filenames))
        return data


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(name='focus2',
      version=read('focus2/_version.py').split("'")[1],
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
      install_requires=['Flask==0.9',
                        'Flask-WTF==0.8',
                        'itsdangerous==0.17',
                        'jsonschema==0.2'],
      tests_require=['mox'],
      classifiers=['Development Status :: 1 - Planning',
                'Intended Audience :: Developers',
                'Intended Audience :: Information Technology',
                'License :: OSI Approved :: '
                'GNU Lesser General Public License v2 or later (LGPLv2+)',
                'Operating System :: OS Independent',
                'Programming Language :: Python :: 2.6'],
      cmdclass={'build_py': build_py})
