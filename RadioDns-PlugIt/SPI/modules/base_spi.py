class BaseSPI:

    def on_event_epg_1(self, event_name, service_provider_meta, client=None):
        pass

    def on_event_epg_3(self, event_name, service_provider_meta, client=None):
        pass

    def on_request_epg_1(self, codops, client):
        pass

    def on_request_epg_3(self, codops, client):
        pass
