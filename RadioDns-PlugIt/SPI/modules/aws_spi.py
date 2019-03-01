from flask import redirect

import SPI.utils
import config
from SPI.modules.base_spi import BaseSPI
from aws.awsutils import get_or_create_bucket, get_website_endpoint
from models import ServiceProvider


class AWSSPI(BaseSPI):
    """
    Implements BaseSPI for AWS cloudfront integration. On event will upload/delete the file to an s3 bucket and
    on request will redirect with a 304 to the bucket.
    """

    def __init__(self):
        bucket, _ = get_or_create_bucket(config.SPI_BUCKET_NAME)
        self.bucket = bucket

    def on_event_epg_1(self, event_name, service_provider_meta, client=None):
        if event_name == SPI.modules.base_spi.EVENT_SPI_UPDATED:
            service_provider = ServiceProvider.query.filter_by(id=service_provider_meta["id"]).first()
            self.upload_spi_file(
                service_provider,
                client,
                "1",
                SPI.utils.generate_spi_file(service_provider, client, "radioepg/servicefollowing/xml1.html")
            )
        elif event_name == SPI.modules.base_spi.EVENT_SPI_DELETED:
            self.delete_spi_file(service_provider_meta["codops"], "1")

    def on_event_epg_3(self, event_name, service_provider_meta, client=None):
        if event_name == SPI.modules.base_spi.EVENT_SPI_UPDATED:
            service_provider = ServiceProvider.query.filter_by(id=service_provider_meta["id"]).first()
            self.upload_spi_file(
                service_provider,
                client,
                "3",
                SPI.utils.generate_spi_file(service_provider, client, "radioepg/servicefollowing/xml3.html")
            )
        elif event_name == SPI.modules.base_spi.EVENT_SPI_DELETED:
            self.delete_spi_file(service_provider_meta["codops"], "3")

    def on_request_epg_1(self, codops, client_identifier):
        return redirect(AWSSPI.get_file_url(codops, "1", client_identifier), code=304)

    def on_request_epg_3(self, codops, client_identifier):
        return redirect(AWSSPI.get_file_url(codops, "3", client_identifier), code=304)

    @staticmethod
    def get_spi_bucket_filename(service_provider_codops, version, client_identifier):
        """
        Returns the name of an SPI file that is hosted in the s3 bucket.

        The scheme of the name is the following: <codops>.<verison>.<client_identifier>.xml
        The <client_identifier> is optional. If there is no client the value will be "default".

        :param service_provider_codops: The service provider codops.
        :param version: The version of the file ("1" or "3").
        :param client_identifier: The client identifier or None.
        :return: The full filename of the SPI file.
        """
        return service_provider_codops + "." + version + "." + (client_identifier if client_identifier else "default") + ".xml"

    @staticmethod
    def get_file_url(codops, version, client_identifier):
        """
        Returns the SPI file url for and SPI file that is hosted in the s3 bucket and is only accessible by cloudfront.

        :param codops: The service provider codops.
        :param version: The version of the file ("1" or "3").
        :param client_identifier: The client identifier or None.
        :return: The full url of the SPI file.
        """
        return "https://" + config.SPI_CLOUDFRONT_DOMAIN + "/" + AWSSPI.get_spi_bucket_filename(codops, version, client_identifier)

    def upload_spi_file(self, service_provider, client, version, contents):
        """
        Uploads a file to the s3 bucket.

        :param service_provider: The service provider holding the information for the SPI file.
        :param client: The client if the file contains client overrides or None.
        :param version: The version of the file ("1" or "3").
        :param contents: string contents of the file
        """
        key = self.bucket.new_key(AWSSPI.get_spi_bucket_filename(service_provider.codops, version, client.identifier if client else "default"))
        key.content_type = 'text/xml'
        key.set_contents_from_string(contents)

    def delete_spi_file(self, service_provider_meta, version):
        """
        Deletes a file that is hosted on a s3 bucket.

        :param service_provider_meta: a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
        :param version: The version of the file ("1" or "3").
        """
        bucket_name = AWSSPI.get_spi_bucket_filename(service_provider_meta["codops"], version, None)
        for key in [key for key in self.bucket.get_all_keys() if key.startswith(bucket_name)]:
            self.bucket.delete_key(key)
