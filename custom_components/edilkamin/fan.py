"""Platform for fan integration."""
from __future__ import annotations

import logging
import math

from homeassistant.components.fan import SUPPORT_SET_SPEED, FanEntity
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import DOMAIN
from .edilkminApi import EdilkaminApi

_LOGGER = logging.getLogger(__name__)

SPEED_RANGE = (1, 5)  # away is not included in speeds and instead mapped to off


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    _LOGGER.debug(mac_address)

    async_add_devices([EdilkaminFan(mac_address)])


class EdilkaminFan(FanEntity):
    """Representation of a Fan."""

    def __init__(self, mac_address):
        """Initialize the fan."""
        self.mac_address = mac_address
        self.api = EdilkaminApi(mac_address=self.mac_address)

        self.current_speed = None
        self.current_state = False

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_fan1"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.mac_address} fan 1"

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.current_state is False:
            return None

        if self.current_speed is None:
            return None
        return ranged_value_to_percentage(SPEED_RANGE, self.current_speed)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_SET_SPEED

    def set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        self.current_speed = math.ceil(
            percentage_to_ranged_value(SPEED_RANGE, percentage)
        )

        self.api.set_fan_1_speed(self.current_speed)
        self.schedule_update_ha_state()

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.current_state = self.api.get_power_status()
        if self.current_state is True:
            self.current_speed = self.api.get_fan_1_speed()

    def turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Turn on the entity."""

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
