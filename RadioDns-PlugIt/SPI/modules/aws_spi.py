from flask import redirect

import SPI.utils
import config
from SPI.modules.base_spi import BaseSPI
from aws.awsutils import get_or_create_bucket
from models import ServiceProvider, Channel


class AWSSPI(BaseSPI):
    """
    Implements BaseSPI for AWS cloudfront integration. On event will upload/delete the file to an s3 bucket and
    on request will redirect with a 304 to the bucket.
    """

    def __init__(self):
        bucket, _ = get_or_create_bucket(config.SPI_BUCKET_NAME)
        self.bucket = bucket

    def on_si_resource_changed(self, event_name, service_provider, client=None):
        if event_name == SPI.modules.base_spi.EVENT_SI_PI_UPDATED:
            self.upload_file(
                AWSSPI.get_static_bucket_si_filename(service_provider.codops, "1",
                                                     client.identifier if client else "default"),
                SPI.utils.generate_si_file(service_provider, client, "radioepg/servicefollowing/xml1.html")
            )
            self.upload_file(
                AWSSPI.get_static_bucket_si_filename(service_provider.codops, "3",
                                                     client.identifier if client else "default"),
                SPI.utils.generate_si_file(service_provider, client, "radioepg/servicefollowing/xml3.html")
            )
        elif event_name == SPI.modules.base_spi.EVENT_SI_PI_DELETED:
            self.delete_si_file(service_provider["codops"], "1")
            self.delete_si_file(service_provider["codops"], "3")

    def on_pi_resource_changed(self, event_name, station):
        import datetime

        if event_name == SPI.modules.base_spi.EVENT_SI_PI_UPDATED:
            today = datetime.date.today()
            start_of_the_week = datetime.datetime.combine(today - datetime.timedelta(days=today.weekday()),
                                                          datetime.time())
            for i in range(0, 7):
                start_date = (start_of_the_week + datetime.timedelta(days=i)).strftime("%Y%m%d")
                contents = SPI.utils.generate_pi_file(start_date, station=station)
                if not contents:
                    continue

                filtered = Channel.query.filter(Channel.station_id == station.id and Channel.type_id in ["fm", "dab"])
                for channel in filtered:
                    try:
                        self.upload_file(
                            AWSSPI.get_static_bucket_pi_filename(channel.service_identifier, start_date),
                            contents,
                            station.id,
                        )
                    except AttributeError as e:
                        print("[WARN][AWS] in pi resource changed handler", e)
        elif event_name == SPI.modules.base_spi.EVENT_SI_PI_DELETED:
            for key in [key for key in self.bucket.get_all_keys() if key.get_metadata("station_id") == station.id]:
                self.bucket.delete_key(key)

    def on_request_epg_1(self, codops, client_identifier):
        return redirect(AWSSPI.get_file_url({"codops": codops, "version": "1", "client_identifier": client_identifier}),
                        code=304)

    def on_request_epg_3(self, codops, client_identifier):
        return redirect(AWSSPI.get_file_url({"codops": codops, "version": "3", "client_identifier": client_identifier}),
                        code=304)

    def on_request_schedule_1(self, path, date):
        return redirect(AWSSPI.get_file_url({"path": path, "date": str(date)}, type="pi"), code=304)

    @staticmethod
    def get_file_url(options, type="si"):
        if type == "si":
            return "https://" + config.SPI_CLOUDFRONT_DOMAIN + "/" + AWSSPI.get_static_bucket_si_filename(
                options["codops"], options["version"], options["client_identifier"])
        elif type == "pi":
            return "https://" + config.SPI_CLOUDFRONT_DOMAIN + "/" + AWSSPI.get_static_bucket_pi_filename(
                options["path"],
                options["date"],
            )
        else:
            return None

    @staticmethod
    def get_static_bucket_si_filename(service_provider_codops, version, client_identifier):
        """
        Returns the name of an SPI file that is hosted in the s3 bucket.

        The scheme of the name is the following: <codops>.<verison>.<client_identifier>.xml
        The <client_identifier> is optional. If there is no client the value will be "default".

        :param service_provider_codops: The service provider codops.
        :param version: The version of the file ("1" or "3").
        :param client_identifier: The client identifier or None.
        :return: The full filename of the SPI file.
        """
        return service_provider_codops + "." + version + "." + (
            client_identifier if client_identifier else "default") + ".xml"

    @staticmethod
    def get_static_bucket_pi_filename(path, date):
        return ("schedule/" + path + "/" + date + ".xml").lower()

    def upload_file(self, file_key, contents, station_id=None):
        key = self.bucket.new_key(file_key)
        key.content_type = 'text/xml'
        if station_id:
            key.set_metadata('station_id', station_id)
        key.set_contents_from_string(contents)

    def delete_si_file(self, service_provider_meta, version):
        """q
        Deletes a file that is hosted on a s3 bucket.

        :param service_provider_meta: a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
        :param version: The version of the file ("1" or "3").
        """
        bucket_name = AWSSPI.get_static_bucket_si_filename(service_provider_meta["codops"], version, None)
        for key in [key for key in self.bucket.get_all_keys() if key.startswith(bucket_name)]:
            self.bucket.delete_key(key)
