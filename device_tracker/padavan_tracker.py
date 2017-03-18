"""
Support for Padavan-firmware routers.
"""
import logging
import voluptuous as vol
import re
import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import CONF_URL, CONF_PASSWORD, CONF_USERNAME

REQUIREMENTS = ['requests==2.13.0']

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_URL, default='http://192.168.1.1/'): cv.string,
    vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    vol.Optional(CONF_PASSWORD, default='admin'): cv.string,
})


def get_scanner(hass, config):
    """Validate the configuration and return PadavanDeviceScanner."""
    _LOGGER.debug('Padavan init')
    scanner = PadavanDeviceScanner(config[DOMAIN])
    return scanner if scanner.success_init else None


class PadavanDeviceScanner(DeviceScanner):
    """This class queries a Padavan-based router."""

    def __init__(self, config):
        """Initialize the scanner."""
        self.last_results = None
        self.url = config[CONF_URL]
        self.username = config[CONF_USERNAME]
        self.password = config[CONF_PASSWORD]
        self.last_results = []

        # NOTE: Padavan httpd will even don't check HTTP authorization header if multiple devices connected, if will
        # show "You cannot Login unless logout another user first." page instead with mac/ip of authorized device.
        r = self._request()
        self.success_init = True if 'text' in r or r['error_id'] == 'multiple' else False

        if self.success_init:
            _LOGGER.info('Successfully connected to Padavan-based router')
            if 'error_id' in r:
                _LOGGER.info('But %s', r['error_msg'])
        else:
            _LOGGER.error('Failed to connect to Padavan-based router: %s', r['error_msg'])

    def scan_devices(self):
        self._update_info()
        _LOGGER.debug('active_hosts %s', str(self.last_results))
        return self.last_results

    def get_device_name(self, mac):
        return None

    def _request(self, path=''):
        import requests
        from requests.auth import HTTPBasicAuth
        from requests.exceptions import HTTPError, ConnectionError, RequestException

        error_id = None
        error_msg = None
        r = None

        try:
            r = requests.get(self.url + path, auth=HTTPBasicAuth(self.username, self.password))
            r.raise_for_status()
        except HTTPError as e:
            error_id = 'status'
            error_msg = 'Bad status: ' + str(e)
        except ConnectionError as e:
            error_id = 'connection'
            error_msg = "Can't connect to router: " + str(e)
        except RequestException as e:
            error_id = 'other'
            error_msg = 'Some error during request: ' + str(e)

        if not error_id:
            if r.headers['Server'] is None or r.headers['Server'] != 'httpd':
                error_id = 'not_padavan'
                error_msg = "Router's firmware doesn't look like Padavan. 'Server' HTTP header should be 'httpd'"
            if '<span id="logined_ip_str"></span>' in r.text:
                m = re.search("'((\d{1,3}\.)+\d{1,3})'.*'((\w{2}:)+\w{2})'", r.text, re.S)
                device = m.group(1)+'/'+m.group(3) if m else 'IP unavailable'
                error_id = 'multiple'
                error_msg = "There are multiple connections to web interface ({}). Can't query data".format(device)

        return {'error_id': error_id, 'error_msg': error_msg} if error_id else {'text': r.text}

    def _update_info(self):
        """Retrieve latest information from the router."""
        _LOGGER.debug('Polling')

        r_2g = self._request('Main_WStatus2g_Content.asp')
        r_5g = self._request('Main_WStatus_Content.asp')
        if 'error_id' in r_2g or 'error_id' in r_5g:
            _LOGGER.error("Can't get connected clients: %s", r_2g['error_msg'] if 'error_msg' in r_2g else
                r_5g['error_msg'])
            return

        self.last_results = []
        both = r_2g['text'] + r_5g['text']
        for line in both.split('\n'):
            m = re.match("^((.{2}:){5}.{2}) ", line)
            if m:
                self.last_results.append(m.group(1))

        _LOGGER.debug('results %s', str(self.last_results))

        return
