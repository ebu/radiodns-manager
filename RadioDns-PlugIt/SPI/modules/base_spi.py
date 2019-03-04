EVENT_SI_PI_UPDATED = "UPDATE"
EVENT_SI_PI_DELETED = "DELETE"


class BaseSPI:
    """
    Abstract class that describes the events that can happen to an SPI file. Basically an SPI file can
    change or be requested.
    """

    def on_si_resource_changed(self, event_name, service_provider, client=None):
        """
        A class must implement this event listener to receive events that state that a resource of an SI/PI file
        has changed and that the said file needs to be re-generated.

        :param event_name: The name of the event. Can be either be "UPDATE" or "DELETE".
        :param service_provider: a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
        :param client: The client of the modified resource if any.
        """
        pass

    def on_pi_resource_changed(self, event_name, station):
        pass

    def on_request_epg_1(self, codops, client_identifier):
        """
        A class must implement this event listener and return the requested EPG file version 1.
        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        SPI file a soon as possible.

        :param codops: the codops of the service provider.
        :param client_identifier: the identifier of the client if any.
        """
        pass

    def on_request_epg_3(self, codops, client_identifier):
        """
        A class must implement this event listener and return the requested EPG file version 3.
        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        SPI file a soon as possible.

        :param codops: the codops of the service provider.
        :param client_identifier: the identifier of the client if any.
        """
        pass

    def on_request_schedule_1(self, path, date):
        pass
