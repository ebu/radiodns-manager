# -*- coding: utf-8 -*-

# Utils
#from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile
#import re

import config
import re

import boto
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat
import boto.route53

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''


s3 = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_KEY,  host='s3-eu-west-1.amazonaws.com', calling_format=OrdinaryCallingFormat())

bucket = None
bucketName = "eis-static.ebu.io"
bucket = s3.get_bucket(bucketName)

f = open('vbc_files.txt','w')

for key in bucket.list(prefix="generated-vbc15/"):
    fname = key.name
    print fname
    f.write('%s\t%s\n' % (key.name, key.last_modified))
    if (not os.path.basename(fname)==""):
                try:
                    key.get_contents_to_filename(fname)
                except OSError,e:
                    print e

    except:
        pass


http://eis-static.ebu.io/generated-vbc15/06cfb672-f95d-41d5-a3c4-3299c42fe102.png
http://eis-static.ebu.io/generated-vbc15/0dd943b8-9684-4c4c-89ec-c246dc1e7dad.png
http://eis-static.ebu.io/generated-vbc15/07425335-e115-44cf-aec2-1fc3e339048d.png
http://eis-static.ebu.io/generated-vbc15/14cd34d9-3310-4b1a-be48-a7a007825a0c.png
http://eis-static.ebu.io/generated-vbc15/1359e0d7-ea7a-4726-a58d-cc6d8829ad62.png
http://eis-static.ebu.io/generated-vbc15/02b2f5ea-681c-4ac3-8e76-f44ff32b9dd0.png
http://eis-static.ebu.io/generated-vbc15/068a0c44-17b8-477f-8e47-280e9e9df0d8.png
http://eis-static.ebu.io/generated-vbc15/092f3d80-e380-420a-a1ee-599cc6641ce3.png
http://eis-static.ebu.io/generated-vbc15/1aa6b3dc-3cc5-4a30-a16c-574e81137b12.png
http://eis-static.ebu.io/generated-vbc15/0d72e5e7-4a2d-40bf-b33f-b55eca9dca40.png
http://eis-static.ebu.io/generated-vbc15/135c0db1-b0b0-44aa-92ad-837dd185be26.png
http://eis-static.ebu.io/generated-vbc15/0ed959b0-e23e-471e-8f3e-27e3704f2c2a.png
http://eis-static.ebu.io/generated-vbc15/0a00648a-3241-4dfe-93ad-a92232dd9ddc.png
http://eis-static.ebu.io/generated-vbc15/1196d62b-c99c-4be9-b5ac-3d3af625b2be.png
http://eis-static.ebu.io/generated-vbc15/01548ae9-71a3-40cc-b4c2-eab1056eec21.png
http://eis-static.ebu.io/generated-vbc15/0f912b9d-7382-47cb-8fcd-c95f8f39f39c.png
http://eis-static.ebu.io/generated-vbc15/0d662e81-5762-4516-80e3-dc12f620eda6.png
http://eis-static.ebu.io/generated-vbc15/10af11a6-8e04-461f-becf-39a9e1942457.png
http://eis-static.ebu.io/generated-vbc15/059485f7-b5ab-4c06-8212-d612d2011209.png
http://eis-static.ebu.io/generated-vbc15/14af1995-1553-4f8b-b574-dcdbc500d97d.png
http://eis-static.ebu.io/generated-vbc15/0b3f315b-40e2-4dc4-b32f-9405fbac4411.png
http://eis-static.ebu.io/generated-vbc15/0ced6a28-019d-431b-8f43-979e07808646.png
http://eis-static.ebu.io/generated-vbc15/084743f3-a3a9-4e8e-8443-4fb13ece5ae2.png
http://eis-static.ebu.io/generated-vbc15/05fee272-06e8-4afd-ab0b-2d0fdebc0fc4.png
http://eis-static.ebu.io/generated-vbc15/0d3102a7-8681-4b9e-aa2f-6812ebd443a4.png
http://eis-static.ebu.io/generated-vbc15/06912368-aa0a-4cf2-87a3-25fa829d98e9.png