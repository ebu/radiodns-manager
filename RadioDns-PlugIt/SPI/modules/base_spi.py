EVENT_SI_PI_UPDATED = "UPDATE"
EVENT_SI_PI_DELETED = "DELETE"


class BaseSPI:
    """
    Abstract class that describes the events that can happen to an SPI file. Basically an SPI file can
    change or be requested.
    """

    def on_si_resource_changed(self, event_name, service_provider, client=None):
        """
        A class must implement this event listener to receive events that state that a resource of a SI file
        has changed and that the said file needs to be re-generated or deleted.

        :param event_name: The name of the event. Can be either be "UPDATE" or "DELETE".
        :param service_provider: a dict of shape: {"id": integer, "codops": string} containing the metadata of a
        service provider if case of a delete events or the service provider model instance for create/update events.
        :param client: The client of the modified resource if any for create/update events.
        """
        pass

    def on_pi_resource_changed(self, event_name, station):
        """
        A class must implement this event listener to receive events that state that a resource of a PI file
        has changed and that the said file needs to be re-generated or deleted.

        :param event_name: The name of the event. Can be either be "UPDATE" or "DELETE".
        :param station: A station model instance for create/update events or a station id for delete events.
        """
        pass

    def on_request_xsi_1(self, codops, client_identifier):
        """
        A class must implement this event listener and return the requested RadioEPG XSI file version 1.
        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        SI file a soon as possible.

        :param codops: the codops of the service provider.
        :param client_identifier: the identifier of the client if any.
        :return: The requested file or a redirection to the requested file.
        """
        pass

    def on_request_si_3(self, codops, client_identifier):
        """
        A class must implement this event listener and return the requested SPI SI file version 3.1.
        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        SI file a soon as possible.

        :param codops: the codops of the service provider.
        :param client_identifier: the identifier of the client if any.
        :return: The requested file or a redirection to the requested file.
        """
        pass

    def on_request_pi_1(self, path, date):
        """
        A class must implement this event listener and return the requested schedule RadioEPG file version 1.

        NOTE: If possible avoid to access the database in this handler. The goal of this method is to return the
        PI file a soon as possible.

        :param path: the service identifier of the requested file. The service identifier is described
                     in the RadioDNS Lookup specification
        :param date: date in format YYYYMMDD
        :return: The requested file or a redirection to the requested file.
        """
        pass

    def on_request_pi_3(self, path, date):
        """
        A class must implement this event listener and return the requested SPI PI file version 3.1.

        :param path: the service identifier of the requested file. The service identifier is described
                     in the RadioDNS Lookup specification
        :param date: date in format YYYYMMDD
        :return: The requested file or a redirection to the requested file.
        """
        pass
