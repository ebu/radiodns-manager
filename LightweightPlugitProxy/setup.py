#!/usr/bin/env python

from distutils.core import setup

setup(name='lightweight_plugIt_proxy',
      version='1.0.0',
      description='Transition PlugIt Proxy for RadioDns. The project aims to create a lightweight PlugIt Proxy free from EBU.io',
      author='Ioannis Noukakis',
      author_email='inoukakis@gmail.com',
      install_requires=[
          'Django==2.2.24',
          'pylint==2.1.1',
          'requests==2.21.0',
          'urlparse3==1.1',
          'python-dateutil==2.7.5',
          'django-ipware==2.1.0',
          'requests-toolbelt==0.8.0',
          'psycopg2==2.7.6.1',
          'backoff==1.6.0',
          'Pillow==5.0.0',
          'whitenoise==4.1.2'
      ],
      tests_require=[
      ]
      )
