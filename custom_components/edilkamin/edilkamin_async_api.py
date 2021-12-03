"""Edilkamin async api."""
import json
import logging
import asyncio
import async_timeout
import aiohttp

_LOGGER = logging.getLogger(__name__)

class EdilkaminAsyncApi:
    """Edilkamin async API."""

    endpoint_api = "https://fxtj7xkgc6.execute-api.eu-central-1.amazonaws.com"
    url_command = "{}{}".format(endpoint_api, "/prod/mqtt/command")

    def __init__(self, mac_address, session=None):
        """Initialize the class."""
        self.mac_address = mac_address
        self.url_info = f"{self.endpoint_api}/prod/device/{mac_address}/info"
        _LOGGER.debug("Url info = %s", self.url_info)
        _LOGGER.debug("Url command = %s", self.url_command)
        self.session = session

    def get_mac_address(self):
        return self.mac_address

    async def get_temperature(self):
        """Get the temperature."""
        _LOGGER.debug("Get temperature")
        response = await self.execute_get_request()
        result = response.get("status").get("temperatures").get("enviroment")
        _LOGGER.debug("Get temperature response  = %s", result)
        return result

    async def set_temperature(self, value):
        """Modify the temperature."""
        _LOGGER.debug("Set temperature to = %s", value)
        await self.execute_put_request("enviroment_1_temperature", value)

    async def get_power_status(self):
        """Get the power status."""
        _LOGGER.debug("Get power")
        response = await self.execute_get_request()
        result = response.get("status").get("commands").get("power")
        _LOGGER.debug("Get power response  = %s", result)
        return result

    async def enable_power(self):
        """Enable the pellet."""
        _LOGGER.debug("Enable power")
        await self.execute_put_request("power", 1)

    async def disable_power(self):
        """Disable the pellet."""
        _LOGGER.debug("Disable power")
        await self.execute_put_request("power", 0)

    async def get_airkare_status(self):
        """Get status of airekare."""
        _LOGGER.debug("Get airkare status")
        response = await self.execute_get_request()
        return response.get("status").get("flags").get("is_airkare_active")

    async def enable_airkare(self):
        """Enable airkare."""
        _LOGGER.debug("Enable airkare")
        await self.execute_put_request("airkare_function", 1)

    async def disable_airkare(self):
        """Disable airkare."""
        _LOGGER.debug("Disable airkare")
        await self.execute_put_request("airkare_function", 0)

    async def get_relax_status(self):
        """Get the status of relax mode."""
        _LOGGER.debug("Get relax status")
        response = await self.execute_get_request()
        return response.get("status").get("flags").get("is_relax_active")

    async def enable_relax(self):
        """Enable relax."""
        _LOGGER.debug("Enable relax")
        await self.execute_put_request("relax_mode", True)

    async def disable_relax(self):
        """Disable relax."""
        _LOGGER.debug("Disable relax")
        await self.execute_put_request("relax_mode", False)

    async def get_status_tank(self):
        """Get the status of the tank."""
        _LOGGER.debug("Get tank status")
        response = await self.execute_get_request()
        return response.get("status").get("flags").get("is_pellet_in_reserve")

    async def get_fan_1_speed(self):
        """Get the speed of fan 1."""
        _LOGGER.debug("Get speed for fan 1")
        response = await self.execute_get_request()
        return response.get("status").get("fans").get("fan_1_speed")

    async def set_fan_1_speed(self, value):
        """Set the speed of fan 1."""
        _LOGGER.debug("Set speed for fan 1 to %s", value)
        await self.execute_put_request("fan_1_speed", value)

    async def check(self):
        """Call check config."""
        _LOGGER.debug("Check config")
        await self.execute_put_request("check", False)

    async def get_target_temperature(self):
        """Get the target temperature."""
        _LOGGER.debug("Get the target temperature")
        response = await self.execute_get_request()
        return (
            response.get("nvm").get("user_parameters").get("enviroment_1_temperature")
        )

    async def get_alarms(self):
        """Get the target temperature."""
        _LOGGER.debug("Get the target temperature")
        response = await self.execute_get_request()
        alarms_info = response.get("nvm").get("alarms_log")
        index = alarms_info.get("index")
        alarms = []

        for i in range(index):
            alarms.append(alarms_info.get("alarms")[i])

        return alarms

    async def get_nb_alarms(self):
        """Get the target temperature."""
        _LOGGER.debug("Get the target temperature")
        response = await self.execute_get_request()
        return response.get("nvm").get("alarms_log").get("index")

    async def execute_get_request(self):
        """Call the API."""
        data = None
        try:
            async with async_timeout.timeout(5):
                _LOGGER.debug("Endpoint URL: %s", str(self.url_info))
                response = await self.session.get(url=self.url_info)
                if response.status == 200:
                    try:
                        data = await response.json()
                    except ValueError as exception:
                        message = "Server gave incorrect data"
                        raise Exception(message) from exception

                elif response.status == 401:
                    message = "401: Access token might be incorrect"
                    raise HttpException(message, await response.text(), response.status)

                elif response.status == 404:
                    message = "404: incorrect API request"
                    raise HttpException(message, await response.text(), response.status)

                else:
                    message = f"Unexpected status code {response.status}."
                    raise HttpException(message, await response.text(), response.status)

        except aiohttp.ClientError as error:
            _LOGGER.error("Error connecting to Edilkamin API: %s", error)
        except asyncio.TimeoutError as error:
            _LOGGER.debug("Timeout connecting to Edilkamin API: %s", error)
        return data

    async def execute_put_request(self, attributes, value):
        """Call the API."""
        body = None
        if self.session is None:
            self.session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(5):
                body = {
                    "name": attributes,
                    "value": value,
                    "mac_address": self.mac_address,
                }
                _LOGGER.debug("Endpoint URL: %s", str(self.url_command))
                response = await self.session.put(
                    url=self.url_command, data=json.dumps(body)
                )
                if response.status == 200:
                    try:
                        data = await response.json()
                    except ValueError as exception:
                        message = "Server gave incorrect data"
                        raise Exception(message) from exception

                else:
                    message = f"Unexpected status code {response.status}."
                    raise HttpException(message, await response.text(), response.status)

        except aiohttp.ClientError as error:
            _LOGGER.error("Error connecting to Edilkamin API: %s", error)
            message = f"Timeout connecting to Edilkamin API, body = {body}."
            raise HttpException(message, "Time out", 500)
        except asyncio.TimeoutError as error:
            _LOGGER.debug("Timeout connecting to Edilkamin API: %s", error)
            message = f"Timeout connecting to Edilkamin API, body = {body}."
            raise HttpException(message, "Time out", 408)
        return data


class HttpException(Exception):
    """HTTP exception class with message text, and status code."""

    def __init__(self, message, text, status_code):
        """Initialize the class."""
        super().__init__(message)

        self.status_code = status_code
        self.text = text
