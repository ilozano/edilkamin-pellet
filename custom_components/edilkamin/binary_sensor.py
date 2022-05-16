"""Platform for sensor integration."""
from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_PROBLEM,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .edilkamin_async_api import EdilkaminAsyncApi, HttpException
from .edilkamin_coordinator import EdilkaminCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)

    edilkamin_api = EdilkaminAsyncApi(mac_address=mac_address, session=session)

    coordinator = EdilkaminCoordinator(hass, "binary_sensor", edilkamin_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_devices(
        [
            EdilkaminTankBinarySensor(coordinator, mac_address),
            EdilkaminCheckBinarySensor(coordinator, mac_address),
        ]
    )


class EdilkaminTankBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, mac_address: str):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address
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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.info(self.coordinator.data)
        # self._state = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            #self._state = await self.api.get_status_tank()
            self._state = None
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminCheckBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, mac_address: str):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address

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
