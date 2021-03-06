import logging
import XenAPI as xenapi

from xapi_openstack import models

from formencode import validators, Schema, Invalid


logger = logging.getLogger(__name__)


def get_session(options):
    logger.debug('New session to: %s', options.xapi_url)
    session = xenapi.Session(options.xapi_url)
    logger.debug('Authenticating...')
    session.xenapi.login_with_password(
        options.username, options.password)
    return session


def get_vbd(session, vbdref):
    return session.xenapi.VBD.get_all_records()[vbdref]


def get_vdi(session, vdiref):
    vdi = session.xenapi.VDI.get_all_records()[vdiref]
    logger.debug('VDI: %s', vdi)
    return models.VDI(vdi)


def add_vbds(session, machine):
    if machine.vbdrefs:
        for vbdref in machine.vbdrefs:
            machine.vbds.append(models.VBD(get_vbd(session, vbdref)))


def add_sr(session, vdi):
    vdi.sr = models.SR(session.xenapi.SR.get_all_records()[vdi.sr_ref])


def machines(session):
    machine_records = session.xenapi.VM.get_all_records()
    machines = dict()

    for k, v in machine_records.items():
        logging.debug(v)
        machine = models.Machine(v)
        machines[k] = machine
        add_vbds(session, machine)

    return machines


class ValidatingCommand(object):
    schema = None

    def __init__(self, args=None):
        self.args = args or dict()

    def validate(self):
        self.schema().to_python(self.args, None)


class ConnectRequest(Schema):
    user = validators.String(not_empty=True)
    password = validators.String(not_empty=True)
    tenant_name = validators.String(not_empty=True)
    auth_url = validators.String(not_empty=True)


class ConnectToKeystone(ValidatingCommand):
    schema = ConnectRequest

    def __call__(self, ksclient=None):
        return models.KSClient(ksclient.Client(
            username=self.args['user'],
            password=self.args['password'],
            insecure=False,
            tenant_name=self.args['tenant_name'],
            auth_url=self.args['auth_url'],
            tenant_id=None))


class ConnectToXAPISchema(Schema):
    url = validators.String(not_empty=True)
    user = validators.String(not_empty=True)
    password = validators.String(not_empty=True)


class ConnectToXAPI(ValidatingCommand):
    schema = ConnectToXAPISchema

    def __call__(self, xapi=None):
        session = xapi.Session(self.args['url'])
        session.login_with_password(
            self.args['user'],
            self.args['password'])
        return models.XAPISession(session)
