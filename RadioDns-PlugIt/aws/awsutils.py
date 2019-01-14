# -*- coding: utf-8 -*-

import re

import boto
import boto.route53
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key

import config


# BUCKETS AND FILES

def get_or_create_bucket(service_provider):
    """Returns the bucket or creates a new one according to service_provider"""
    s3 = boto.connect_s3(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY,
                         host='s3-eu-west-1.amazonaws.com',
                         calling_format=OrdinaryCallingFormat())  # host='s3-eu-central-1.amazonaws.com')
    bucket = None
    bucket_name = "static.%s" % (service_provider.fqdn.lower().rstrip('.'))

    try:
        bucket = s3.get_bucket(bucket_name)
        return bucket
    except boto.exception.S3ResponseError:
        bucket = s3.create_bucket(bucket_name, location='eu-west-1')
        set_right_bucket(bucket)
        endpoint = get_website_endpoint(bucket)
        update_or_create_provider_cname("static", service_provider, endpoint)
        return bucket
    except Exception as e:
        print(e)


def get_website_endpoint(bucket):
    """Bypasses the us-east vs. eu-west issue on website endpoint"""
    endpoint = bucket.get_website_endpoint()
    return endpoint  # .replace("us-east-1", "eu-west-1") works with spec connection


def set_right_bucket(bucket):
    """Sets the rights and website access on the bucket"""
    bucket.set_acl('public-read')
    bucket.configure_website("index.html")
    bucket.make_public(True, None)


def upload_public_image(service_provider, filename, filepath):
    """upload image to service_provider bucket"""

    bucket = get_or_create_bucket(service_provider)
    newFile = Key(bucket)
    newFile.key = filename
    newFile.set_contents_from_filename(filepath)
    newFile.set_acl('public-read')

    return filename


def delete_public_image(service_provider, filename):
    """Upload image to service_provider bucket"""

    bucket = get_or_create_bucket(service_provider)
    bucket.delete_key(filename)

    return filename


def get_public_urlprefix(service_provider):
    """Public Url to filename"""
    # TODO Handle https depending on AWS
    return "http://%s.%s/" % ('static', service_provider.fqdn.lower().rstrip('.'))


def get_public_image_url(service_provider, filename):
    """Public Url to filename"""
    return "%s%s" % (get_public_urlprefix(service_provider), filename)


# ROUTE 53

def get_cnames_until_a_record(zone, record_name):
    """
    Returns the A record that is at the end of the CNAME chain in the specified hosted zone. If no A record is found in
    the said chain, returns None.

    Note: this method does no actual DNS resolution. It just looks for DNS records within route53 via boto api.

    :param zone: The zone of the researches.
    :param record_name: The name of the record from where to start looking.
    :return: The A record if any found, None otherwise.
    """
    a = zone.get_a(record_name)
    cname = zone.get_cname(record_name)

    if a:
        return a.resource_records[0]
    elif cname:
        return get_cnames_until_a_record(zone, cname.resource_records[0])
    else:
        return None


def verify_srv_records():
    """
    Verifies that srv records points to a correct CNAME of the second hosted zone. Also verifies the CNAMES of the said
    zone.

    :raises: EnvironmentError if any check failed.
    :return: -
    """
    route53 = boto.connect_route53(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY)
    srv_records = []
    second_hosted_zone = route53.get_zone(config.DOMAIN + ".")
    second_hosted_zone_cnames = []

    for zone in route53.get_zones():
        for record in zone.get_records():
            if record.type == 'SRV':
                srv_records.append((record.name, record.resource_records[0].split(' ')[3], zone.name))

    for record in second_hosted_zone.get_records():
        if record.type == 'A':
            print("INFO! Main A record is pointing to " + record.resource_records[0])
        elif record.type == "CNAME":
            second_hosted_zone_cnames.append((record.name, record.resource_records[0]))

    # Check SRV records
    for srv_rec in srv_records:
        if srv_rec[1] + "." not in map(lambda x: x[0], second_hosted_zone_cnames):
            raise EnvironmentError(
                """The SRV record {name} -> {target} of the hosted zone {zone} was not found in the second hosted 
                zone cnames records.""".format(name=srv_rec[0], target=srv_rec[1], zone=srv_rec[2]))

    # Check second hosted zone CNAMES
    for cname_rec in second_hosted_zone_cnames:
        if get_cnames_until_a_record(second_hosted_zone, cname_rec[1]) is None:
            raise EnvironmentError(
                """The CNAME record {cname_rec} of the second hosted zone isn't pointing on the A record"""
                    .format(cname_rec=cname_rec))


def get_or_create_mainzone():
    """Returns the zone or creates a new one according to service_provider"""
    route53 = boto.connect_route53(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY)

    zone_name = config.DOMAIN

    zone = route53.get_zone(zone_name)
    if not zone:
        zone = route53.create_zone(zone_name)

    # Make sure parent zone has NS - disabled as there is only the domain in the AWS account now.
    # update_or_create_parent_ns(zone)

    return zone


def get_or_create_zone_forprovider(service_provider):
    """Returns the zone or creates a new one according to service_provider"""
    route53 = boto.connect_route53(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY)

    zone_name = service_provider.fqdn

    zone = route53.get_zone(zone_name)
    if not zone:
        zone = route53.create_zone(zone_name)

    # Make sure parent zone has NS
    update_or_create_parent_ns(zone)

    return zone


def update_or_create_provider_cname(prefix, service_provider, endpoint):
    """Creates a new CNAME entry or updates it"""
    zone = get_or_create_zone_forprovider(service_provider)

    name = "%s.%s" % (prefix.lower(), service_provider.fqdn.lower())
    cname = update_or_create_cname(zone, name, endpoint)

    return cname


def update_or_create_cname(zone, name, value):
    """Creates a new CNAME entry or updates it"""

    cname = zone.get_cname(name)
    if cname:
        if not cname.resource_records[0].rstrip('.') == value.rstrip('.'):
            cname = zone.update_cname(name, value)
    else:
        cname = zone.add_cname(name, value)

    cname = zone.get_cname(name)

    return cname.resource_records[0]


def get_provider_cname(prefix, service_provider, zone):
    """Gets CNAME entry"""

    name = "%s.%s" % (prefix.lower(), service_provider.fqdn.lower())
    cname = zone.get_cname(name)

    return cname


def update_or_create_vissrv_station(station):
    """Creates a new CNAME entry or updates it"""
    if station.radiovis_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radiovis._tcp'

        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())

        regex = re.compile('(?P<host>.+?):(?P<port>\d+)$')
        r = regex.search(station.radiovis_service)
        if r:
            host = r.groupdict()['host']
            port = r.groupdict()['port']
            value = service_string(host, port)
            return update_or_create_srv(zone, name, value)
    return None


def remove_vissrv_station(station):
    """Removes the VIS entry of a station"""
    if station.radiovis_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radiovis._tcp'
        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())
        remove_srv(zone, name)


def update_or_create_epgsrv_station(station):
    """Creates a new CNAME entry or updates it"""

    if station.radioepg_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        name = "%s.%s" % ('_radioepg._tcp'.lower(), station.fqdn.lower())

        regex = re.compile('(?P<host>.+?):(?P<port>\d+)$')
        r = regex.search(station.radioepg_service)
        if r:
            host = r.groupdict()['host']
            port = r.groupdict()['port']
            value = service_string(host, port)
            return update_or_create_srv(zone, name, value)
    return None


def remove_epgsrv_station(station):
    """Removes the EPG entry of a station"""

    if station.radioepg_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        name = "%s.%s" % ('_radioepg._tcp', station.fqdn.lower())
        remove_srv(zone, name)


def update_or_create_spisrv_station(station):
    """Creates a new CNAME entry or updates it"""

    if station.radiospi_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        name = "%s.%s" % ('_radiospi._tcp', station.fqdn.lower())

        regex = re.compile('(?P<host>.+?):(?P<port>\d+)$')
        r = regex.search(station.radiospi_service)
        if r:
            host = r.groupdict()['host']
            port = r.groupdict()['port']
            value = service_string(host, port)
            return update_or_create_srv(zone, name, value)
    return None


def remove_spisrv_station(station):
    """Removes the SPI entry of a station"""

    if station.radiospi_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        name = "%s.%s" % ('_radioepg._tcp', station.fqdn.lower())
        remove_srv(zone, name)


def update_or_create_tagsrv_station(station):
    """Creates a new CNAME entry or updates it"""

    if station.radiotag_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radiotag._tcp'

        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())

        regex = re.compile('(?P<host>.+?):(?P<port>\d+)$')
        r = regex.search(station.radiotag_service)
        if r:
            host = r.groupdict()['host']
            port = r.groupdict()['port']
            value = service_string(host, port)
            return update_or_create_srv(zone, name, value)
    return None


def remove_tagsrv_station(station):
    """Removes the TAG entry of a station"""
    if station.radioepg_enabled and station.service_provider and not config.STANDALONE:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radiotag._tcp'
        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())
        remove_srv(zone, name)


def update_or_create_srv(zone, name, value):
    """Creates a new CNAME entry or updates it"""
    srv = zone.find_records(name, 'SRV', desired=1)
    if srv:
        if not srv.resource_records[0] == value:
            srv = zone.update_record(srv, value)
    else:
        srv = zone.add_record('SRV', name, value)
    srv = zone.find_records(name, 'SRV', desired=1)
    return srv.resource_records[0]


def update_or_create_a(zone, name, value):
    """Creates a new CNAME entry or updates it"""
    a = zone.find_records(name, 'A', desired=1)
    if a:
        if not a.resource_records[0] == value:
            a = zone.update_record(a, value)
    else:
        a = zone.add_record('A', name, value)
    a = zone.find_records(name, 'A', desired=1)
    return a.resource_records[0]


def remove_srv(zone, name):
    """Removes a SRV entry"""
    srv = zone.find_records(name, 'SRV', desired=1)
    if srv:
        srv = zone.delete_record(srv, 'Removed by RadioDNS Manager')


def service_string(server, port):
    srv = "%d %d %d %s" % (0, 100, int(port), server)
    return srv


def get_parent_ns(zone):
    """Creates a new CNAME entry or updates it"""
    route53 = zone.route53connection

    find = re.compile(r"^([^.]+).(.+)$")
    parent_name = re.search(find, zone.name).group(2)

    parent_zone = route53.get_zone(parent_name)

    return parent_zone.find_records(zone.name, 'NS')


def update_or_create_parent_ns(zone):
    """Creates a new CNAME entry or updates it"""
    route53 = zone.route53connection

    find = re.compile(r"^([^.]+).(.+)$")
    parent_name = re.search(find, zone.name).group(2)
    parent_zone = route53.get_zone(parent_name)
    parent_nse = parent_zone.find_records(zone.name, 'NS')

    NSE = zone.get_nameservers()
    if not parent_nse:
        # Create Parent NS entries if missing
        parent_zone.add_record('NS', zone.name, NSE)
    else:
        # Check if correct
        if NSE not in parent_nse.resource_records:
            parent_zone.update_record(parent_nse, NSE)

    return zone


# REMOVAL

def remove_station(st):
    if st:
        # _radiovis._tcp
        remove_vissrv_station(st)
        # _radioepg._tcp
        remove_epgsrv_station(st)
        # _radiospi._tcp
        remove_spisrv_station(st)
        # _radiotag._tcp
        remove_tagsrv_station(st)


# CHECKS

def check_mainzone():
    mainzone = get_or_create_mainzone()
    mainns = mainzone.get_nameservers()
    # FIXME Skip properly parent ns verification for mainzone
    # parent = get_parent_ns(mainzone)
    # parentns = parent.resource_records
    visserver = get_cnames_until_a_record(mainzone, config.RADIOVIS_DNS)
    epgserver = get_cnames_until_a_record(mainzone, config.RADIOEPG_DNS)
    spiserver = get_cnames_until_a_record(mainzone, config.RADIOSPI_DNS)
    tagserver = get_cnames_until_a_record(mainzone, config.RADIOTAG_DNS)
    # WILDCARD Not Working in BOTO at this time : #1216 https://github.com/boto/boto/pull/1216
    # viswildcard = update_or_create_cname(mainzone, '*.'+config.RADIOVIS_DNS, config.RADIOVIS_DNS)
    # epgwildcard = update_or_create_cname(mainzone, '*.'+config.RADIOEPG_DNS, config.RADIOEPG_DNS)
    # tagwildcard = update_or_create_cname(mainzone, '*.'+config.RADIOTAG_DNS, config.RADIOTAG_DNS)
    isvalid = visserver and epgserver and spiserver and tagserver

    return {'isvalid': isvalid, 'name': mainzone.name, 'mainzone': {'zone': mainzone.name, 'ns': mainns},
            'parentns': {'entry': "Parent zone.", 'value': "Parent zone is now located in the main AWS account of EBU.io"},
            'services': {'vis': {'name': config.RADIOVIS_DNS, 'ip': visserver},  # 'wildcard': viswildcard},
                         'epg': {'name': config.RADIOEPG_DNS, 'ip': epgserver},  # 'wildcard': epgwildcard},
                         'spi': {'name': config.RADIOSPI_DNS, 'ip': spiserver},  # 'wildcard': spiwildcard},
                         'tag': {'name': config.RADIOTAG_DNS, 'ip': tagserver}}}  # 'wildcard': tagwildcard}}}


def check_serviceprovider(sp):
    if sp:
        # NS
        zone = get_or_create_zone_forprovider(sp)
        zonens = zone.get_nameservers()
        parent = get_parent_ns(zone)
        parentns = parent.resource_records
        nsisvalid = set(parentns) == set(zonens)

        # Bucket
        bucket = get_or_create_bucket(sp)
        staticcname = get_provider_cname('static', sp, zone)
        staticcnamename = staticcname.name
        staticnamerecord = staticcname.resource_records[0].rstrip('.')
        bucketendpoint = get_website_endpoint(bucket)
        bucketisvalid = bucketendpoint == staticnamerecord

        mainzone = get_or_create_mainzone()
        visservice = update_or_create_cname(mainzone, sp.vis_fqdn, config.RADIOVIS_DNS)
        epgservice = update_or_create_cname(mainzone, sp.epg_fqdn, config.RADIOEPG_DNS)
        spiservice = update_or_create_cname(mainzone, sp.spi_fqdn, config.RADIOSPI_DNS)
        tagservice = update_or_create_cname(mainzone, sp.tag_fqdn, config.RADIOTAG_DNS)

        isvalid = nsisvalid and bucketisvalid and visservice and epgservice and tagservice

        return {'isvalid': isvalid, 'name': zone.name, 'zone': {'isvalid': nsisvalid, 'zone': zone.name, 'ns': zonens},
                'parentns': {'entry': parent.name, 'value': parentns},
                'bucket': {'isvalid': bucketisvalid, 'name': bucket.name, 'publicendpoint': bucketendpoint,
                           'cname': {'name': staticcnamename, 'record': staticnamerecord}},
                'services': {'vis': {'name': sp.vis_fqdn, 'value': visservice},
                             'epg': {'name': sp.epg_fqdn, 'value': epgservice},
                             'spi': {'name': sp.spi_fqdn, 'value': spiservice},
                             'tag': {'name': sp.tag_fqdn, 'value': tagservice}}}

    return {'isvalid': False}


def check_station(st):
    if st:
        # _radiovis._tcp
        vis = update_or_create_vissrv_station(st)
        # _radioepg._tcp
        epg = update_or_create_epgsrv_station(st)
        # _radiospi._tcp
        spi = update_or_create_spisrv_station(st)
        # _radiotag._tcp
        tag = update_or_create_tagsrv_station(st)

        visisvalid = not st.radiovis_enabled
        epgisvalid = not st.radioepg_enabled
        spiisvalid = not st.radiospi_enabled
        tagisvalid = not st.radiotag_enabled

        if vis:
            visisvalid = True
        if epg:
            epgisvalid = True
        if spi:
            spiisvalid = True
        if tag:
            tagisvalid = True

        isvalid = visisvalid and epgisvalid and spiisvalid and tagisvalid

        return {'isvalid': isvalid, 'name': st.fqdn,
                'radiovis': {'isvalid': visisvalid, 'enabled': st.radiovis_enabled, 'fqdn': vis},
                'radioepg': {'isvalid': epgisvalid, 'enabled': st.radioepg_enabled, 'fqdn': epg},
                'radiospi': {'isvalid': spiisvalid, 'enabled': st.radiospi_enabled, 'fqdn': spi},
                'radiotag': {'isvalid': tagisvalid, 'enabled': st.radiotag_enabled, 'fqdn': tag},
                }

    return {'isvalid': False}
