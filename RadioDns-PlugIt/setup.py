from setuptools import setup
# from distutils.core import setup


setup(
    name="RadioDns-PlugIt",
    packages=[],
    version="3.0.0",
    license="BSD",
    description="",
    author="EBU Technology & Innovation",
    author_email="poor@ebu.ch",
    url="https://git.ebu.io/radiodns/radiodns-plugit",
    download_url="",
    keywords=[],
    classifiers=[],
    long_description="",
    long_description_content_type='',
    install_requires=[
        'flask==1.0.2',
        'sqlalchemy==1.2.11',
        'Flask-SQLAlchemy==2.3.2',
        'alembic==1.0.0',
        'dnspython==1.15.0',
        'requests==2.21.0',
        'raven==6.9.0',
        'boto==2.43.0',
        'Pillow==5.2.0',
        'plugit==0.3.12',
        'MySQL-python==1.2.5',
        'Werkzeug==0.14.1',
        'pylint==1.9.3',
        'backoff==1.6.0',
        'jsonschema==2.6.0',
        'simplejson==3.16.0',
        'logging==0.4.9.6',
        'Pykka==1.2.1',
        'pytest==4.3.0',
        'mock==2.0.0'
    ],
    include_package_data=True,
)
