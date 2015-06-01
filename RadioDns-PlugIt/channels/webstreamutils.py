import urllib2
import contextlib

# based on http://codereview.stackexchange.com/questions/23364/get-metadata-from-an-icecast-radio-stream
def parse_headers(response):
    headers = {}
    while True:
        line = response.readline()
        if line == '\r\n':
            break # end of headers
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key] = value
    return headers

def poll_radio():
    request = urllib2.Request("http://stream.srg-ssr.ch/couleur3/mp3_128.m3u", headers = {
        'User-Agent' : 'User-Agent: VLC/2.0.5 LibVLC/2.0.5',
        'Icy-MetaData' : '1',
        'Range' : 'bytes=0-',
    })
    # the connection will be close on exit from with block
    with contextlib.closing(urllib2.urlopen(request)) as response:

        headers = parse_headers(response)

        meta_interval = int(headers['icy-metaint'])
        response.read(meta_interval) # throw away the data until the meta interval

        length = ord(response.read(1)) * 16 # length is encoded in the stream
        metadata = response.read(length)
        print metadata