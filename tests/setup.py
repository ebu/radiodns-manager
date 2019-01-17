from distutils.core import setup

setup(name='RadioDNSTests',
      version='1.0',
      package_dir={'': 'tests'},
      packages=[''],
      install_requires=[
          'pytest==3.8.0',
          'pytest-ordering==0.6',
          'selenium==3.14.0',
          'requests==2.21.0',
          'SQLAlchemy==1.2.11',
          'PyMySQL==0.9.2',
      ],
      )
