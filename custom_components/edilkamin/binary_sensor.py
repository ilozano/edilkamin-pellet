"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_PROBLEM,
    BinarySensorEntity,
)

from .const import DOMAIN
from .edilkminApi import EdilkaminApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    mac_address = hass.data[DOMAIN][config_entry.entry_id]
    async_add_devices([EdilkaminTankBinarySensor(mac_address)])


class EdilkaminTankBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, mac_address):
        """Initialize the sensor."""
        self._state = None
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)
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
        return f"{self.mac_address} tank"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self.api.get_status_tank()
