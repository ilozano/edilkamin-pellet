"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)

from .const import DOMAIN
from .edilkminApi import EdilkaminApi

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)

# https://github.com/home-assistant/example-custom-config/blob/master/custom_components/detailed_hello_world_push/sensor.py


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    _LOGGER.debug(mac_address)

    async_add_devices(
        [EdilkaminTemperatureSensor(mac_address), EdilkaminFan1Sensor(mac_address)]
    )


class EdilkaminTemperatureSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, mac_address):
        """Initialize the sensor."""
        self._state = None
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return TEMP_CELSIUS

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_temperature"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.mac_address} temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.api.get_temperature()


class EdilkaminFan1Sensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, mac_address):
        """Initialize the sensor."""
        self._state = None
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)
        self._attr_icon = "mdi:fan"

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_fan1_sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.mac_address} fan 1"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.api.get_fan_1_speed()
