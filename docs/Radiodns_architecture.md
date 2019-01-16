# Architecture
## Stacks architecture
### RadioDns with EBU.io
Currently EBU.io provides the user and organisation management. That means that the PlugIt Proxy from EBU.io will provide
RadioDns with information about users, their organisation and their access level. RadioDns will be charged of managing
service providers, stations, channel, SPI xml file generation, etc.

![architecture_ebu.io.png](/docs/images/architecture_ebu.io.png)

The diagram above explains the current state of the RadioDns stack for EBU.io. It is composed of the PlugIt proxy in EBU.io that
serves the frontend and communicate with the RadioDns docker instance in an AWS EC2 instance via the PlugIt protocol.
The RadioDns itself is running with a uWSGI server with an NGINX in an other container as a reverse proxy. The NGINX
does also the HTTPS handling. 

Every logo uploaded to RadioDns will be processed into various sizes (parameterizable via RadioDns configuration) then
uploaded into an S3 bucket (one bucket per provider).

XML files are dynamically generated (there is an option to configure a memory cache within the app via RadioDns configuration)
and served by uWSGI. This behaviour will be corrected in the next iterations of the project.

The vis service is hosted on a separated instance because of its scalability and instability issues.

### RadioDns without EBU.io
This mode can be run entirely in docker. 

![architecture_ebu.io.png](/docs/images/architecture_standalone.png)

The diagram above explains the current state of the RadioDns stack for this mode. The LPP image is the LightweightPlugitProxy.
Its provides the PlugIt Bridge between the world and the RadioDns manager. It also manager users, organizations and authentication.

## DNS architecture
All DNS architecture is hosted in amazon web services in route53.
Currently, the RadioDns hostname is radio.ebu.io.

radio.ebu.io contains in its hosted zone an A record pointing to the RadioDns instance. Every service provider's codops is a
subdomain of radio.ebu.io. For example the service provider having 'zzebu' as codops has a registered hosted name of zzebu.radio.ebu.io.
So every service provider has its own hosted zone in the radio.ebu.io hosted zone.

The service providers hosted zones contains SRV records for the discovery of their services per station (EPG, SPI, VIS, TAG).
Theses SRV records points on CNAMEs located in the radio.ebu.io hosted zone.

radio.ebu.io's hosted zone contains CNAME records to map the service providers services (EPG, SPI, VIS, TAG) to the radio.ebu.io
services.

An example of the full chain would be:

===== SERVICE PROVIDER HOSTED ZONE =====

    SRV: _radioepg._tcp.demofm.zzebu.radio.ebu.io. -> 0 100 443 zzebu.spi.radio.ebu.io.

===== radio.ebu.io HOSTED ZONE =====

    CNAME: zzebu.spi.radio.ebu.io. -> spi.radio.ebu.io.
    CNAME: spi.radio.ebu.io. -> radio.ebu.io.
    A: radio.ebu.io. -> `<INSTANCE IP>`

## HTTPS considerations
It is the system admin's responsibility to ensure HTTPS certificates renewal. Currently
there is support for letsencrypt.org certificates via a cron job that runs on the EC2 instance itself. But the application
does not provide a way to handle automated certificate renewal from within its docker containers. This is because
in the future RadioDns would be something that will be deployable by everyone and EBU don't want to impose constraints.

If you want/require automated certificate renewal within the NGINX docker container, feel free to use a custom one.
In the future, an example container with letsencrypt.org certificates auto renewal will be made.
