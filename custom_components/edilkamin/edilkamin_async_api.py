"""Edilkamin async api."""
import json
import logging
import asyncio
import async_timeout
import aiohttp
from aiohttp import ClientSession

from custom_components.edilkamin.auth import Auth

_LOGGER = logging.getLogger(__name__)


class EdilkaminAsyncApi:
    """Edilkamin async API."""

    endpoint_api = "https://fxtj7xkgc6.execute-api.eu-central-1.amazonaws.com"
    url_command = "{}{}".format(endpoint_api, "/prod/mqtt/command")

    def __init__(self, mac_address, session=ClientSession):
        """Initialize the class."""
        self.mac_address = mac_address
        self.url_info = f"{self.endpoint_api}/prod/device/{mac_address}/info"
        _LOGGER.debug("Url info = %s", self.url_info)
        _LOGGER.debug("Url command = %s", self.url_command)
        self.session = session
        self.auth = Auth(self.session)

    def get_mac_address(self):
        """Get the mac address."""
        return self.mac_address

    async def set_temperature(self, value):
        """Modify the temperature."""
        _LOGGER.debug("Set temperature to = %s", value)
        await self.execute_put_request("enviroment_1_temperature", value)

    async def enable_power(self):
        """Enable the pellet."""
        _LOGGER.debug("Enable power")
        await self.execute_put_request("power", 1)

    async def disable_power(self):
        """Disable the pellet."""
        _LOGGER.debug("Disable power")
        await self.execute_put_request("power", 0)

    async def enable_airkare(self):
        """Enable airkare."""
        _LOGGER.debug("Enable airkare")
        await self.execute_put_request("airkare_function", 1)

    async def disable_airkare(self):
        """Disable airkare."""
        _LOGGER.debug("Disable airkare")
        await self.execute_put_request("airkare_function", 0)

    async def enable_relax(self):
        """Enable relax."""
        _LOGGER.debug("Enable relax")
        await self.execute_put_request("relax_mode", True)

    async def disable_relax(self):
        """Disable relax."""
        _LOGGER.debug("Disable relax")
        await self.execute_put_request("relax_mode", False)

    async def set_fan_1_speed(self, value):
        """Set the speed of fan 1."""
        _LOGGER.debug("Set speed for fan 1 to %s", value)
        await self.execute_put_request("fan_1_speed", value)

    async def check(self):
        """Call check config."""
        _LOGGER.debug("Check config")
        await self.execute_put_request("check", False)

    async def fetch_data(self):
        return await self.execute_request("GET", self.url_info, None)

    async def execute_put_request(self, attributes, value):
        body = {
            "name": attributes,
            "value": value,
            "mac_address": self.mac_address,
        }
        return await self.execute_request("PUT", self.url_command, json.dumps(body))

    async def execute_request(self, method: str, url: str, body: str):
        """Call the API."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        try:
            async with async_timeout.timeout(5):
                _LOGGER.debug(
                    "Endpoint URL: %s , method: %s, body: %s",
                    str(url),
                    str(method),
                    str(body),
                )
                headers = await self.get_headers()
                response = await self.session.request(
                    method, url, headers=headers, data=body
                )

                if response.status == 200:
                    try:
                        data = await response.json()
                    except ValueError as exception:
                        message = "Server gave incorrect data"
                        raise Exception(message) from exception

                elif response.status == 401:
                    message = "401: Access token might be incorrect"
                    raise HttpException(message, await response.text(), response.status)

                elif response.status == 403:
                    message = "403: Access token might be incorrect"
                    raise HttpException(message, await response.text(), response.status)

                elif response.status == 404:
                    message = "404: incorrect API request"
                    raise HttpException(message, await response.text(), response.status)

                else:
                    message = f"Unexpected status code {response.status}. \nResponse body = {await response.text()}"
                    _LOGGER.error(message)
                    raise HttpException(message, await response.text(), response.status)

        except aiohttp.ClientError as error:
            _LOGGER.error("Error connecting to Edilkamin API: %s", error)
            message = "Timeout connecting to Edilkamin API, body = {body}."
            raise HttpException(message, "Time out", 500) from error
        except asyncio.TimeoutError as error:
            _LOGGER.debug("Timeout connecting to Edilkamin API: %s", error)
            message = "Timeout connecting to Edilkamin API, body = {body}."
            raise HttpException(message, "Time out", 408) from error
        return data

    async def get_headers(self):
        headers = {}
        token = await self.auth.get_token()
        headers["Authorization"] = f"Bearer {token}"
        return headers


class HttpException(Exception):
    """HTTP exception class with message text, and status code."""

    def __init__(self, message, text, status_code):
        """Initialize the class."""
        super().__init__(message)

        self.status_code = status_code
        self.text = text
