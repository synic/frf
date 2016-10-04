from setuptools import setup, find_packages

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
          },
      scripts=['frf/bin/frf-startproject'],
      package_data={'frf': ['skel/*']},
      zip_safe=False)
