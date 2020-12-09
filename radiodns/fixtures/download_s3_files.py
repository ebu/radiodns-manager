import os

import boto3

BUCKET_NAME = ""
s3 = boto3.resource('s3')

os.makedirs("medias/112x32", exist_ok=True)
os.makedirs("medias/128x128", exist_ok=True)
os.makedirs("medias/320x240", exist_ok=True)
os.makedirs("medias/32x32", exist_ok=True)
os.makedirs("medias/600x600", exist_ok=True)

for bucket in s3.buckets.all():
    if bucket.name.endswith(".ebu.io"):
        print(bucket.name)
        for obj in bucket.objects.all():
            object = s3.Object(bucket.name, obj.key)
            object.download_file(f'medias/{object.key}')
