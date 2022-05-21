"""Platform for sensor integration."""
from __future__ import annotations

import logging
from config.custom_components.edilkamin.edilkamin_wrapper import EdilkaminWrapper
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from config.custom_components.edilkamin.edilkamin_wrapper import EdilkaminWrapper

from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .edilkamin_async_api import EdilkaminAsyncApi, HttpException
from .coordinator import Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)

    edilkamin_api = EdilkaminAsyncApi(mac_address=mac_address, session=session)

    coordinator = Coordinator(hass, "switch", edilkamin_api)

    async_add_entities(
        [
            EdilkaminAirekareSwitch(coordinator, mac_address, edilkamin_api),
            EdilkaminPowerSwitch(coordinator, mac_address, edilkamin_api),
            EdilkaminRelaxSwitch(coordinator, mac_address, edilkamin_api),
        ]
    )


class EdilkaminAirekareSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Sensor."""

    def __init__(
        self, coordinator: CoordinatorEntity, mac_address: str, api: EdilkaminAsyncApi
    ):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address
        self.api = api
        self._attr_icon = "mdi:air-filter"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_airekare_switch"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.api.enable_airkare()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.api.disable_airkare()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = EdilkaminWrapper.get_airkare_status(self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Sensor."""

    def __init__(
        self, coordinator: CoordinatorEntity, mac_address: str, api: EdilkaminAsyncApi
    ):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address
        self.api = api

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_power_switch"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.api.enable_power()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.api.disable_power()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._state = EdilkaminWrapper.get_power_status(self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminRelaxSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Sensor."""

    def __init__(
        self, coordinator: CoordinatorEntity, mac_address: str, api: EdilkaminAsyncApi
    ):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address
        self.api = api
        self._attr_icon = "mdi:weather-night"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_relax_switch"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.api.enable_relax()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.api.disable_relax()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = EdilkaminWrapper.get_relax_status(self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return
