# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

from setuptools import find_packages, setup

setup(name='frf',
      version='0.1',
      description='Falcon REST Framework',
      url='http://github.com/enderlabs/frf/',
      author='Ender Labs Developers',
      author_email='developers@eventboard.io',
      license='Proprietary',
      packages=find_packages(),
      install_requires=[
          'pytz',
          'SQLAlchemy',
          'falcon',
          'jinja2',
          'pycrypto',
          'tabulate',
          'pytest',
          'python-dateutil',
          'gunicorn'
      ],
      extras_require={
          'Docs': ['Sphinx'],
          'Pretty': ['colorama', 'pyfiglet'],
          'Cache': ['redis'],
          'Testing': ['flake8', 'factory-boy],
          },
      scripts=['frf/bin/frf-startproject'],
      package_data={'frf': ['skel/*']},
      zip_safe=False)
