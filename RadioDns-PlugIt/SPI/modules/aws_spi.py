from flask import redirect

import SPI.utils
import config
from SPI.modules.base_spi import BaseSPI
from aws.awsutils import get_or_create_bucket
from models import Channel


class AWSSPI(BaseSPI):
    """
    Implements BaseSPI for AWS CloudFront integration. On event will upload/delete the SI/PI files to an s3 bucket and
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
            for key in [key for key in self.bucket.get_all_keys() if key.get_metadata("x-amz-meta-station_id") == station.id]:
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
    def get_file_url(data, type="si"):
        """
        Returns public endpoint to get the SI/PI file.
        :param data: Data specific to the type url.
        :param type: Can either be "si" or "pi".
        :return: The endpoint if the type is supported. Otherwise None.
        """
        if type == "si":
            return "https://" + config.SPI_CLOUDFRONT_DOMAIN + "/" + AWSSPI.get_static_bucket_si_filename(
                data["codops"], data["version"], data["client_identifier"])
        elif type == "pi":
            return "https://" + config.SPI_CLOUDFRONT_DOMAIN + "/" + AWSSPI.get_static_bucket_pi_filename(
                data["path"],
                data["date"],
            )
        else:
            return None

    @staticmethod
    def get_static_bucket_si_filename(service_provider_codops, version, client_identifier):
        """
        Returns the name of a SI file that is hosted in the s3 bucket.

        The scheme of the name is the following: <codops>.<verison>.<client_identifier>.xml
        The <client_identifier> is optional. If there is no client the value will be "default".

        :param service_provider_codops: The service provider codops.
        :param version: The version of the file ("1" or "3").
        :param client_identifier: The client identifier or None.
        :return: The full filename of the SI file.
        """
        return service_provider_codops + "." + version + "." + (
            client_identifier if client_identifier else "default") + ".xml"

    @staticmethod
    def get_static_bucket_pi_filename(path, date):
        """
        Returns the name of a PI file that is hosted in the s3 bucket.

        The scheme of the name is the following: schedule/<service_identifier>/<date>.xml

        :param path: The path or <service_identifier> is described here:
            https://www.etsi.org/deliver/etsi_ts/102800_102899/102818/03.01.01_60/ts_102818v030101p.pdf
            Currently <service_identifier> supports only fm and dab schemes.
        :param date: The <date> is of the shape <YEAR><MONTH><DAY>.
            - <YEAR> is a four digit number representing the current year, eg: 2019
            - <MONTH> is a two digit number representing the current month in the current year, eg: 01
            - <DAY> is a two digit number representing the current day in the current month, eg: 01
        :return: The full filename and path of the PI file.
        """
        return ("schedule/" + path + "/" + date + ".xml").lower()

    def upload_file(self, file_key, contents, station_id=None):
        """
        Uploads a file to the s3 bucket.

        :param file_key: The name/path of the file.
        :param contents: The contents of the file.
        :param station_id: (optional) The station id with which the file is associated.
        """
        key = self.bucket.new_key(file_key)
        key.content_type = 'text/xml'
        if station_id:
            key.set_metadata("x-amz-meta-station_id", station_id)
        key.set_contents_from_string(contents)

    def delete_si_file(self, service_provider_meta, version):
        """
        Deletes a file that is hosted on a s3 bucket.

        :param service_provider_meta: a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
        :param version: The version of the file ("1" or "3").
        """
        bucket_name = service_provider_meta["codops"] + "." + version
        for key in [key for key in self.bucket.get_all_keys() if key.startswith(bucket_name)]:
            self.bucket.delete_key(key)
