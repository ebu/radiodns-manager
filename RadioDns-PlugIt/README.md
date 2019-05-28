RadioDns - PlugIt
=================

This folder contains the RadioDns API server. The API is also called by the RadioVisServer.

# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and
testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- python 2.7
- docker 18.06.1+
- virtualenv 16.0.0+
- docker-compose 1.23.2+

### Installing
#### Preparing the `venv`

    virtualenv --python=$(which python2) venv
    source venv/bin/activate
    cd RadioDNS-Plugit
    
Install the required PIP dependencies:

    pip install .
    
To deactivate the running environment:

    deactivate
    
## Running the Server

Remember that you must have a running PlugIt Proxy and database in order to test the service.

    python server.py
    

### Extra steps for mac users

You need the mysql connector

    brew install mysql-connector-c
    
Then you must edit the mysql_config file located in ```/usr/local/bin/mysql_config```

You must edit those lines

    # Create options 
    libs="-L$pkglibdir"
    libs="$libs -l "
    
To

    # Create options 
    libs="-L$pkglibdir"
    libs="$libs -lmysqlclient -lssl -lcrypto"
    
Finally you have to add those lines to your .bash_profile (in your home directory)(If this file dosen't exist just create it).

    LDFLAGS:  -L/usr/local/opt/openssl/lib
    CPPFLAGS: -I/usr/local/opt/openssl/include

## Test
Integration tests are available in the tests folder of the root folder.

Unit testing for XML publishing feature can be found within the `tests` folder of this project.

##3 Running the tests

In order to run theses tests you'll need to ensure that docker is up and running and that nothing runs on port `3306`.
Then you may use the tests run script to starts the tests:

    source venv/bin/activate
    cd tests
    python run.py
    
In this revision (11.03.2019) the tests cover the XML publishing aggregator part. Unit testing for AWS will come
with the upcoming migration to boto3.

## Database
Sqlalchemy is used for database access. Models are defined inside the `models.py` file.

## Database migrations
For easy model upgrade, alembic is used. When a model is modified it's possible to run the command
`alembic revision --autogenerate -m 'message'` to create a new revision of the database.
`alembic upgrade head` is used to apply changes, upgrading the database to the latest version.
Details are available in the official documentation of alembic.

Migrations are done automatically by the server at startup if needed.

# Configuration
The configuration is stored inside `config.py`. You can change it by setting environment variables corresponding to the config parameters.

Here is a list of the options you can configure through environment variables:
- **RADIO_DNS_PORT**: Port where the app will listen to. Numeric. Defaults to `4000`.
- **API_URL**: Url to the PlugIt Proxy (either EBU.io or Lightweight Plugit Proxy (LPP)). Defaults to `http://127.0.0.1:4000/`.
The api url must end with a `/`.
- **SQLALCHEMY_URL**: Url of the following scheme: `mysql://<msql_user>:<password>@<host>:<port>/<database_name>`. Defaults to
`mysql://root:<password>@127.0.0.1:3306/radiodns`.
- **API_SECRET**: Random string defined by hand. Defaults to `dev-secret`.
- **AWS_ACCESS_KEY**: AWS access key, in case the apps needs to use AWS resources.
- **AWS_SECRET_KEY**: AWS secret key, in case the apps needs to use AWS resources.
- **AWS_ZONE**: AWS zone. Defaults to `eu-west-1`.
- **DOMAIN**: Domain name base for all services. Defaults to `radio.ebu.io`.
- **RADIOTAG_ENABLED**: TAG service switch. Can be `True|False`. Defaults to `True`.
- **XSISERVING_ENABLED**: EPG and SPI services switch. Can be `True|False`. Defaults to `True`.
- **XSISERVING_DOMAIN**: Domain where the EPG and SPI services will be served. Defaults to `127.0.0.1:5000`. In doubt, give
to this parameter the same value as the **DOMAIN** parameter.
- **RADIOVIS_DNS**: Domain name where the VIS service will be accessible. Defaults to `127.0.0.1`. In doubt, give
to this parameter the following value: `vis.DOMAIN`.
- **RADIOEPG_DNS**: Domain name where the EPG service will be accessible. Defaults to `127.0.0.1`. In doubt, give
to this parameter the following value: `epg.DOMAIN`.
- **RADIOTAG_DNS**: Domain name where the TAG service will be accessible. Defaults to `127.0.0.1`. In doubt, give
to this parameter the following value: `tag.DOMAIN`.
- **RADIOSPI_DNS**: Domain name where the SPI service will be accessible. Defaults to `127.0.0.1`. In doubt, give
to this parameter the following value: `spi.DOMAIN`.
- **RADIOVIS_PORT**: Port where the VIS service will be accessible. Defaults to `61613`.
- **RADIOEPG_PORT**: Port where the EPG service will be accessible. Defaults to `5000`.
- **RADIOTAG_PORT**: Port where the TAG service will be accessible. Defaults to `5000`.
- **RADIOSPI_PORT**: Port where the SPI service will be accessible. Defaults to `5000`.
- **DEBUG**: Can be True|False. Defaults to True. If True we Flask app will run in debug mode. Otherwise, it will run in production mode.
- **STANDALONE**: Wherever the app should run without external dependencies such as AWS, EBU.IO, etc.
Mostly for local testing.
- **PI_BASE_URL**: The base URL for the PlugIi API - prefix url to access utilities of this server (e.g. <PI_BASE_URL>/radiodns/ping).
In staging and production mode, that should be the **API_SECRET** parameter. Defaults to `dev-secret`.
- **PI_ALLOWED_NETWORKS**: Allowed hosts for this service. List of hosts commas separated. Defaults to `0.0.0.0/0`.
- **PI_API_VERSION**: Version of this service. 
- **PI_API_NAME**: Name of this service.
- **XML_CACHE_TIMEOUT**: Time in seconds before discarding XML cache. Numeric. Defaults to `0`.
- **DATABASE_CONNECTION_MERCY_TIME**: Time to wait (in seconds) until each reset of the backoff database connection retry 
function. Numeric. Default to `60`. The application will wait an increasingly longer time for each failed database connection attempts.
This is done in order to avoid having multiple apps connecting to a database at the same time but rather spread those
connections so all app can reconnect smoothly. After X seconds (X being the time chosen for this parameter) the increasing
 time to wait between each attempt will be reset so an application doesn't take 300 seconds to reconnect to its database.
- **VIS_WEB_SOCKET_ENDPOINT_HOST**: Endpoint to the VIS player of RadioDns manager. Used by the HTML vis player. Defaults to
`127.0.0.1`.

**STANDALONE OPTIONS**
- **LOGO_INTERNAL_URL**: Logo upload url. This has to point to the MockApi inside the docker network. Defaults to `http://127.0.0.1:8000/uploads`.
- **LOGO_PUBLIC_URL**: Url of the docker host were the browser can access logos. Defaults to `http://127.0.0.1:8000/uploads`.
- **IMG_CACHE_TIMEOUT**: Time in seconds before discarding images cache. Numeric. Defaults to `0`.

**CDN OPTIONS**
- **USES_CDN**: If you want to use the aws cloudfront integration to deliver spi files. String. Defaults to `False`.
- **SPI_BUCKET_NAME**: name of the bucket that will hold the SPI files. String. Please ensure that this name follow this set of rules:
https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
- **SPI_GENERATION_INTERVAL**: The SPI file generator executor will batch SPI file updates in order to be more efficient.
Here you can specify how much time shall pass between each updates. Numeric. In seconds. Defaults to `300`.
- **SPI_CLOUDFRONT_DOMAIN**: The cloudfront domain that will serve the SPI files. String.
