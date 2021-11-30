"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .edilkminApi import EdilkaminApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    mac_address = hass.data[DOMAIN][config_entry.entry_id]
    async_add_devices(
        [
            EdilkaminAirekareSwitch(mac_address),
            EdilkaminPowerSwitch(mac_address),
            EdilkaminRelaxSwitch(mac_address),
        ]
    )


class EdilkaminAirekareSwitch(SwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, mac_address):
        """Initialize the sensor."""
        self._state = None
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)
        self._attr_icon = "mdi:air-filter"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_airekare_switch"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.mac_address} airekare"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.api.enable_airkare()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self.api.disable_airkare()

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self.api.get_airkare_status()
        _LOGGER.debug("update State airkare= %s", self.state)


class EdilkaminPowerSwitch(SwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, mac_address):
        """Initialize the sensor."""
        self._state = None
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_power_switch"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.mac_address} power"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.api.enable_power()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self.api.disable_power()

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self.api.get_power_status()
        _LOGGER.debug("update State power= %s", self.state)


class EdilkaminRelaxSwitch(SwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, mac_address):
        """Initialize the sensor."""
        self._state = None
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)
        self._attr_icon = "mdi:weather-night"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_relax_switch"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.mac_address} relax"

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.api.enable_relax()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self.api.disable_relax()

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self.api.get_relax_status()
