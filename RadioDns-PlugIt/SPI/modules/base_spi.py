EVENT_SPI_UPDATED = "UPDATE"
EVENT_SPI_DELETED = "DELETE"


class BaseSPI:
    """
    Abstract class that describes the events that can happen to an SPI file. Basically an SPI file can
    change or be requested.
    """

    def on_event_epg_1(self, event_name, service_provider_meta, client=None):
        """
        A class must implement this event listener to receive events on a modified SPI file version 1.
        The implementer is expected to update its SPI file so it reflects the new state of the file.

        :param event_name: The name of the event. Can be either be "UPDATE" or "DELETE".
        :param service_provider_meta: a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
        :param client: The client of the modified resource if any.
        """
        pass

    def on_event_epg_3(self, event_name, service_provider_meta, client=None):
        """
        A class must implement this event listener to receive events on a modified SPI file version 3.
        The implementer is expected to update its SPI file so it reflects the new state of the file.

        :param event_name: The name of the event. Can be either be "UPDATE" or "DELETE".
        :param service_provider_meta: a dict containing the metadata of a service provider.
        The dict is of shape: {"id": integer, "codops": string}
        :param client: The client of the modified resource if any.
        :return:
        """
        pass

    def on_request_epg_1(self, codops, client_identifier):
        """
        A class must implement this event listener and return the requested SPI file version 1.
        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        SPI file a soon as possible.

        :param codops: the codops of the service provider.
        :param client_identifier: the identifier of the client if any.
        """
        pass

    def on_request_epg_3(self, codops, client_identifier):
        """
        A class must implement this event listener and return the requested SPI file version 3.
        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        SPI file a soon as possible.

        :param codops: the codops of the service provider.
        :param client_identifier: the identifier of the client if any.
        """
        pass
