from setuptools import setup
# from distutils.core import setup


setup(
    name="RadioDns-VIS",
    packages=[],
    version="1.0.0",
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
        'dnspython==1.15.0',
        'haigha==0.9.0',
        'gevent==1.3.7',
        'greenlet==0.4.15',
        'requests==2.20.1',
        'beaker==1.10.0',
        'nose==1.3.7',
        'psutil==5.4.8',
        'pylibmc==1.6.0',
    ],
    include_package_data=True,
)
