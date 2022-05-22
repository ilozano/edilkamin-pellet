"""Platform for climate integration."""
from __future__ import annotations

import logging
import logging
from datetime import timedelta
from homeassistant.components.climate import (
    ClimateEntity,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .edilkamin_async_api import EdilkaminAsyncApi, HttpException

_LOGGER = logging.getLogger(__name__)

CLIMATE_HVAC_MODE_MANAGED = [
    HVAC_MODE_HEAT
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)

    async_add_devices(
        [
            EdilkaminClimateEntity(
                EdilkaminAsyncApi(mac_address=mac_address, session=session)
            )
        ]
    )


class EdilkaminClimateEntity(ClimateEntity):
    """Representation of a Climate."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the climate."""
        self._state = None
        self._current_temperature = None
        self._target_temperature = None
        self._fan1_speed = None
        self._hvac_mode = None
        self.api = api
        self.mac_address = api.get_mac_address()
        self._attr_max_temp = 24
        self._attr_min_temp = 14

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_climate"

    @property
    def temperature_unit(self):
        """The unit of temperature measurement"""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """The current temperature."""
        return self._current_temperature

    @property
    def hvac_mode(self):
        """The current operation ."""
        return self._hvac_mode

    @property
    def hvac_modes(self):
        """List of available operation modes."""
        return CLIMATE_HVAC_MODE_MANAGED

    @property
    def fan_mode(self):
        """Returns the current fan mode.."""
        return self._fan1_speed

    @property
    def fan_modes(self):
        """List of available fan modes."""
        return ["1", "2", "3", "4", "5"]

    @property
    def target_temperature(self):
        """The current temperature."""
        return self._target_temperature

    @property
    def supported_features(self):
        """Bitmap of supported features"""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        try:
            await self.api.set_fan_1_speed(fan_mode)
        except HttpException as err:
            _LOGGER.error(str(err))
            return
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            target_tmp = kwargs.get(ATTR_TEMPERATURE)
            await self.api.set_temperature(target_tmp)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            self._current_temperature = await self.api.get_temperature()
            self._target_temperature = await self.api.get_target_temperature()
            self._fan1_speed = await self.api.get_fan_1_speed()

            power = await self.api.get_power_status()
            if power is True:
                self._hvac_mode = HVAC_MODE_HEAT
            else:
                self._hvac_mode = HVAC_MODE_OFF

        except HttpException as err:
            _LOGGER.error(str(err))
            return

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.error(hvac_mode)

        if hvac_mode not in CLIMATE_HVAC_MODE_MANAGED:
            raise ValueError(f"Unsupported HVAC mode: {hvac_mode}")

        if hvac_mode == HVAC_MODE_OFF:
            return await self.async_turn_off()

        if self._hvac_mode == HVAC_MODE_HEAT and hvac_mode == HVAC_MODE_HEAT:
            return await self.async_turn_off()

        await self.async_turn_on()
        _LOGGER.debug("Setting operation mode to %s", hvac_mode)
        self.async_write_ha_state()

    async def async_turn_on(self):
        """Turn on."""
        _LOGGER.debug("Turning %s on", self.unique_id)
        await self.api.enable_power()

    async def async_turn_off(self):
        """Turn off."""
        _LOGGER.debug("Turning %s off", self.unique_id)
        await self.api.disable_power()
        self.async_write_ha_state()
