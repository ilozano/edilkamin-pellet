"""Platform for sensor integration."""
from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_PROBLEM,
    BinarySensorEntity,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .edilkamin_async_api import EdilkaminAsyncApi, HttpException

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)

    async_add_devices(
        [
            EdilkaminTankBinarySensor(
                EdilkaminAsyncApi(mac_address=mac_address, session=session)
            ),
            EdilkaminCheckBinarySensor(
                EdilkaminAsyncApi(mac_address=mac_address, session=session)
            ),
        ]
    )


class EdilkaminTankBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the sensor."""
        self._state = None
        self.api = api
        self.mac_address = api.get_mac_address()
        self._attr_icon = "mdi:propane-tank"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return DEVICE_CLASS_PROBLEM

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_tank_binary_sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Réservoir pellet"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            self._state = await self.api.get_status_tank()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminCheckBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the sensor."""
        self._state = None
        self.api = api
        self.mac_address = api.get_mac_address()

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return DEVICE_CLASS_PROBLEM

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_check_binary_sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Check config"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.api.check()
            self._state = False
            self.async_write_ha_state()
        except HttpException as err:
            self._state = True
            _LOGGER.error(str(err))
            return
