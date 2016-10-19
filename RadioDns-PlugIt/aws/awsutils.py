# -*- coding: utf-8 -*-

# Utils
# from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile
# import re

import config
import re

import boto
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key
import boto.route53


### BUCKETS AND FILES

def get_or_create_bucket(service_provider):
    """Returns the bucket or creates a new one according to service_provider"""
    # s3 = boto.s3.connect_to_region('eu-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    s3 = boto.connect_s3(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY,
                         host='s3-eu-west-1.amazonaws.com',
                         calling_format=OrdinaryCallingFormat())  # host='s3-eu-central-1.amazonaws.com')
    bucket = None
    bucketName = "static.%s" % (service_provider.fqdn.lower().rstrip('.'))

    try:
        bucket = s3.get_bucket(bucketName)
        return bucket
    except boto.exception.S3ResponseError:
        bucket = s3.create_bucket(bucketName, location='eu-west-1')
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


### ROUTE 53

def get_or_create_mainzone():
    """Returns the zone or creates a new one according to service_provider"""
    route53 = boto.connect_route53(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY)

    zoneName = config.DOMAIN

    zone = route53.get_zone(zoneName)
    if not zone:
        zone = route53.create_zone(zoneName)

    # Make sure parent zone has NS
    update_or_create_parent_ns(zone)

    return zone


def get_or_create_zone_forprovider(service_provider):
    """Returns the zone or creates a new one according to service_provider"""
    route53 = boto.connect_route53(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY)

    zoneName = service_provider.fqdn

    zone = route53.get_zone(zoneName)
    if not zone:
        zone = route53.create_zone(zoneName)

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
    if station.radiovis_enabled and station.service_provider:
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
    if station.radiovis_enabled and station.service_provider:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radiovis._tcp'
        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())
        remove_srv(zone, name)


def update_or_create_epgsrv_station(station):
    """Creates a new CNAME entry or updates it"""

    if station.radioepg_enabled and station.service_provider:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radioepg._tcp'

        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())

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
    if station.radioepg_enabled and station.service_provider:
        zone = get_or_create_zone_forprovider(station.service_provider)
        prefix = '_radioepg._tcp'
        name = "%s.%s" % (prefix.lower(), station.fqdn.lower())
        remove_srv(zone, name)


def update_or_create_tagsrv_station(station):
    """Creates a new CNAME entry or updates it"""

    if station.radiotag_enabled and station.service_provider:
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
    if station.radioepg_enabled and station.service_provider:
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
    parentName = re.search(find, zone.name).group(2)

    parentzone = route53.get_zone(parentName)

    return parentzone.find_records(zone.name, 'NS')


def update_or_create_parent_ns(zone):
    """Creates a new CNAME entry or updates it"""
    route53 = zone.route53connection

    find = re.compile(r"^([^.]+).(.+)$")
    parentName = re.search(find, zone.name).group(2)
    parentZone = route53.get_zone(parentName)
    parentNSE = parentZone.find_records(zone.name, 'NS')

    NSE = zone.get_nameservers()
    if not parentNSE:
        # Create Parent NS entries if missing
        parentZone.add_record('NS', zone.name, NSE)
    else:
        # Check if correct
        if NSE not in parentNSE.resource_records:
            parentZone.update_record(parentNSE, NSE)

    return zone


### REMOVAL

def remove_station(st):
    if st:
        # _radiovis._tcp
        remove_vissrv_station(st)
        # _radioepg._tcp
        remove_epgsrv_station(st)
        # _radiotag._tcp
        remove_tagsrv_station(st)


### CHECKS

def check_mainzone():
    mainzone = get_or_create_mainzone()
    mainns = mainzone.get_nameservers()
    parent = get_parent_ns(mainzone)
    parentns = parent.resource_records
    visserver = update_or_create_a(mainzone, config.RADIOVIS_DNS, config.RADIOVIS_A)
    epgserver = update_or_create_a(mainzone, config.RADIOEPG_DNS, config.RADIOEPG_A)
    tagserver = update_or_create_a(mainzone, config.RADIOTAG_DNS, config.RADIOTAG_A)
    # WILDCARD Not Working in BOTO at this time : #1216 https://github.com/boto/boto/pull/1216
    # viswildcard = update_or_create_cname(mainzone, '*.'+config.RADIOVIS_DNS, config.RADIOVIS_DNS)
    # epgwildcard = update_or_create_cname(mainzone, '*.'+config.RADIOEPG_DNS, config.RADIOEPG_DNS)
    # tagwildcard = update_or_create_cname(mainzone, '*.'+config.RADIOTAG_DNS, config.RADIOTAG_DNS)
    isvalid = set(parentns) == set(mainns) and visserver and epgserver and tagserver

    return {'isvalid': isvalid, 'name': mainzone.name, 'mainzone': {'zone': mainzone.name, 'ns': mainns},
            'parentns': {'entry': parent.name, 'value': parentns},
            'services': {'vis': {'name': config.RADIOVIS_DNS, 'ip': visserver},  # 'wildcard': viswildcard},
                         'epg': {'name': config.RADIOEPG_DNS, 'ip': epgserver},  # 'wildcard': epgwildcard},
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
        tagservice = update_or_create_cname(mainzone, sp.tag_fqdn, config.RADIOTAG_DNS)

        isvalid = nsisvalid and bucketisvalid and visservice and epgservice and tagservice

        return {'isvalid': isvalid, 'name': zone.name, 'zone': {'isvalid': nsisvalid, 'zone': zone.name, 'ns': zonens},
                'parentns': {'entry': parent.name, 'value': parentns},
                'bucket': {'isvalid': bucketisvalid, 'name': bucket.name, 'publicendpoint': bucketendpoint,
                           'cname': {'name': staticcnamename, 'record': staticnamerecord}},
                'services': {'vis': {'name': sp.vis_fqdn, 'value': visservice},
                             'epg': {'name': sp.epg_fqdn, 'value': epgservice},
                             'tag': {'name': sp.tag_fqdn, 'value': tagservice}}}

    return {'isvalid': False}


def check_station(st):
    if st:
        # _radiovis._tcp
        vis = update_or_create_vissrv_station(st)
        # _radioepg._tcp
        epg = update_or_create_epgsrv_station(st)
        # _radiotag._tcp
        tag = update_or_create_tagsrv_station(st)

        visisvalid = not st.radiovis_enabled
        epgisvalid = not st.radioepg_enabled
        tagisvalid = not st.radiotag_enabled

        if vis:
            visisvalid = True
        if epg:
            epgisvalid = True
        if tag:
            tagisvalid = True

        isvalid = visisvalid and epgisvalid and tagisvalid

        return {'isvalid': isvalid, 'name': st.fqdn,
                'radiovis': {'isvalid': visisvalid, 'enabled': st.radiovis_enabled, 'fqdn': vis},
                'radioepg': {'isvalid': epgisvalid, 'enabled': st.radioepg_enabled, 'fqdn': epg},
                'radiotag': {'isvalid': tagisvalid, 'enabled': st.radiotag_enabled, 'fqdn': tag}}

    return {'isvalid': False}
