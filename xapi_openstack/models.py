from urlparse import urlparse


class Machine(object):
    def __init__(self, data):
        self.data = data
        self.vbds = []

    @property
    def vbdrefs(self):
        return self.data.get('VBDs')

    @property
    def exportable(self):
        if self.disk_vbds:
            for vbd in self.disk_vbds:
                if not vbd.is_vdi:
                    return False
            return True
        return False

    @property
    def disk_vbds(self):
        return [vbd for vbd in self.vbds if vbd.is_disk]

    @property
    def label(self):
        return self.data.get('name_label')

    @property
    def uuid(self):
        return self.data.get('uuid')


class VBD(object):
    def __init__(self, data):
        self.data = data

    @property
    def is_vdi(self):
        return bool(self.data.get('VDI'))

    @property
    def is_disk(self):
        return 'Disk' == self.data.get('type')

    @property
    def vdi_ref(self):
        return self.data.get('VDI')


class VDI(object):
    def __init__(self, data):
        self.data = data

    @property
    def uuid(self):
        return self.data.get('uuid')

    @property
    def sr_ref(self):
        return self.data.get('SR')


class SR(object):
    def __init__(self, data):
        self.data = data

    @property
    def uuid(self):
        return self.data.get('uuid')


class KSClient(object):
    def __init__(self, client):
        self.client = client

    @property
    def auth_token(self):
        return self.client.auth_token

    def _get_endpoint_urlobj(self):
        return urlparse(
            self.client.service_catalog.url_for(
                service_type="image", endpoint_type="publicURL"))

    @property
    def glance_host(self):
        return self._get_endpoint_urlobj().hostname

    @property
    def glance_port(self):
        return self._get_endpoint_urlobj().port


class XAPISession(object):
    def __init__(self, session):
        self.session = session

    def get_single_host(self, session=None):
        host, = self.session.xenapi.host.get_all()
        return host
