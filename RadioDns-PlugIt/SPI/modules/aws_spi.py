from flask import redirect

import SPI.utils
import config
from SPI.modules.base_spi import BaseSPI
from aws.awsutils import get_or_create_bucket, get_website_endpoint
from models import ServiceProvider


class AWSSPI(BaseSPI):

    def __init__(self):
        bucket, _ = get_or_create_bucket(config.SPI_BUCKET_NAME)
        self.bucket = bucket

    def on_event_epg_1(self, event_name, service_provider_meta, client=None):
        if event_name == SPI.utils.EVENT_SPI_UPDATED:
            service_provider = ServiceProvider.query.filter_by(id=service_provider_meta["id"]).first()
            self.upload_spi_file(
                service_provider,
                client,
                "1",
                SPI.utils.generate_spi_file(service_provider, client, "radioepg/servicefollowing/xml1.html")
            )
        elif event_name == SPI.utils.EVENT_SPI_DELETED:
            self.delete_spi_file(service_provider_meta["codops"], "1")

    def on_event_epg_3(self, event_name, service_provider_meta, client=None):
        if event_name == SPI.utils.EVENT_SPI_UPDATED:
            service_provider = ServiceProvider.query.filter_by(id=service_provider_meta["id"]).first()
            self.upload_spi_file(
                service_provider,
                client,
                "3",
                SPI.utils.generate_spi_file(service_provider, client, "radioepg/servicefollowing/xml3.html")
            )
        elif event_name == SPI.utils.EVENT_SPI_DELETED:
            self.delete_spi_file(service_provider_meta["codops"], "3")

    def on_request_epg_1(self, codops, client_identifier):
        return redirect(AWSSPI.get_bucket_endpoint(codops, "1", client_identifier), code=304)

    def on_request_epg_3(self, codops, client_identifier):
        return redirect(AWSSPI.get_bucket_endpoint(codops, "3", client_identifier), code=304)

    @staticmethod
    def get_bucket_name(service_provider_codops, version, client_identifier):
        return service_provider_codops + "." + version + "." + (client_identifier if client_identifier else "default") + ".xml"

    @staticmethod
    def get_bucket_endpoint(codops, version, client_identifier):
        return "https://" + config.SPI_CLOUDFRONT_DOMAIN + "/" + AWSSPI.get_bucket_name(codops, version, client_identifier)

    def upload_spi_file(self, service_provider, client, version, contents):
        key = self.bucket.new_key(AWSSPI.get_bucket_name(service_provider.codops, version, client.identifier if client else "default"))
        key.content_type = 'text/xml'
        key.set_contents_from_string(contents)

    def delete_spi_file(self, service_provider_meta, version):
        bucket_name = AWSSPI.get_bucket_name(service_provider_meta["codops"], version, None)
        for key in [key for key in self.bucket.get_all_keys() if key.startswith(bucket_name)]:
            self.bucket.delete_key(key)
