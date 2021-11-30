"""Edilkamin api."""
import json
import logging

import requests

_LOGGER = logging.getLogger(__name__)


class EdilkaminApi:
    """Edilkamin API."""

    endpoint_api = "https://fxtj7xkgc6.execute-api.eu-central-1.amazonaws.com"
    url_command = "{}{}".format(endpoint_api, "/prod/mqtt/command")

    def __init__(self, mac_address):
        """Initialize API."""
        self.mac_address = mac_address
        self.url_info = f"{self.endpoint_api}/prod/device/{mac_address}/info"
        _LOGGER.debug("Url info = %s", self.url_info)
        _LOGGER.debug("Url command = %s", self.url_command)

    def get_temperature(self):
        """Get the temperature."""
        _LOGGER.debug("Get temperature")
        response = self.execute_request()
        result = response.get("status").get("temperatures").get("enviroment")
        _LOGGER.debug("Get temperature response  = %s", result)
        return result

    def set_temperature(self, value):
        """Modify the temperature."""
        _LOGGER.debug("Set temperature to = %s", value)
        self.execute_post_request("enviroment_1_temperature", value)

    def get_power_status(self):
        """Get the power status."""
        _LOGGER.debug("Get power")
        response = self.execute_request()
        result = response.get("status").get("commands").get("power")
        _LOGGER.debug("Get power response  = %s", result)
        return result

    def enable_power(self):
        """Enable the pellet."""
        _LOGGER.debug("Enable power")
        self.execute_post_request("power", 1)

    def disable_power(self):
        """Disable the pellet."""
        _LOGGER.debug("Disable power")
        self.execute_post_request("power", 0)

    def get_airkare_status(self):
        """Get status of airekare."""
        _LOGGER.debug("Get airkare status")
        response = self.execute_request()
        return response.get("status").get("flags").get("is_airkare_active")

    def enable_airkare(self):
        """Enable airkare."""
        _LOGGER.debug("Enable airkare")
        self.execute_post_request("airkare_function", 1)

    def disable_airkare(self):
        """Disable airkare."""
        _LOGGER.debug("Disable airkare")
        self.execute_post_request("airkare_function", 0)

    def get_relax_status(self):
        """Get the status of relax mode."""
        _LOGGER.debug("Get relax status")
        response = self.execute_request()
        return response.get("status").get("flags").get("is_relax_active")

    def enable_relax(self):
        """Enable relax."""
        _LOGGER.debug("Enable relax")
        self.execute_post_request("relax_mode", True)

    def disable_relax(self):
        """Disable relax."""
        _LOGGER.debug("Disable relax")
        self.execute_post_request("relax_mode", False)

    def get_status_tank(self):
        """Get the status of the tank."""
        _LOGGER.debug("Get tank status")
        response = self.execute_request()
        return response.get("status").get("flags").get("is_pellet_in_reserve")

    def get_fan_1_speed(self):
        """Get the speed of fan 1."""
        _LOGGER.debug("Get speed for fan 1")
        response = self.execute_request()
        return response.get("status").get("fans").get("fan_1_speed")

    def set_fan_1_speed(self, value):
        """Set the speed of fan 1."""
        _LOGGER.debug("Set speed for fan 1 to %s", value)
        self.execute_post_request("fan_1_speed", value)

    def check(self):
        """Call check config."""
        _LOGGER.debug("Check config")
        self.execute_post_request("check", False)

    def execute_request(self):
        """Execute a GET request and return the result in JSON."""
        retry = False
        try:
            response = requests.get(self.url_info, timeout=5)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                _LOGGER.error(response.status_code, response.text)
        except requests.exceptions.HTTPError as err:
            _LOGGER.error(err)
        except requests.exceptions.ConnectionError as err:
            _LOGGER.error(err)
        except requests.exceptions.Timeout as err:
            _LOGGER.error("Retry request")
            if retry is False:
                retry = True
                self.execute_request()
            else:
                _LOGGER.error(err)
        except requests.exceptions.RequestException as err:
            _LOGGER.error(err)

    def execute_post_request(self, attributes, value):
        """Execute an POST request."""
        retry = False
        try:
            body = {"name": attributes, "value": value, "mac_address": self.mac_address}
            _LOGGER.debug("Body to PUT = %s", body)
            response = requests.put(self.url_command, timeout=5, data=json.dumps(body))
            if response.status_code != 200:
                _LOGGER.error(response.status_code, response.text)
        except requests.exceptions.HTTPError as err:
            _LOGGER.error(err)
        except requests.exceptions.ConnectionError as err:
            _LOGGER.error(err)
        except requests.exceptions.Timeout as err:
            if retry is False:
                retry = True
                self.execute_request()
            else:
                _LOGGER.error(err)
        except requests.exceptions.RequestException as err:
            _LOGGER.error(err)
