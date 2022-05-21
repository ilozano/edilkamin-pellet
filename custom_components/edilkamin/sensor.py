"""Platform for sensor integration."""
from __future__ import annotations

import logging
import time
from typing import Any

from config.custom_components.edilkamin.edilkamin_wrapper import EdilkaminWrapper
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Coordinator
from .edilkamin_async_api import EdilkaminAsyncApi, HttpException

_LOGGER = logging.getLogger(__name__)


# https://github.com/home-assistant/example-custom-config/blob/master/custom_components/detailed_hello_world_push/sensor.py
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""

    mac_address = hass.data[DOMAIN][config_entry.entry_id]

    session = async_get_clientsession(hass)

    edilkamin_api = EdilkaminAsyncApi(mac_address=mac_address, session=session)

    coordinator = Coordinator(hass, "sensor", edilkamin_api)

    async_add_entities(
        [
            EdilkaminTemperatureSensor(coordinator, mac_address),
            EdilkaminFan1Sensor(coordinator, mac_address),
            EdilkaminAlarmSensor(coordinator, mac_address),
            EdilkaminActualPowerSensor(coordinator, mac_address),
        ]
    )


class EdilkaminTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, mac_address: str):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address

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
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = EdilkaminWrapper.get_temperature(self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminFan1Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, mac_address: str):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address
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
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = EdilkaminWrapper.get_fan_1_speed(self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminAlarmSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, mac_address: str):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address
        self._attr_icon = "mdi:alert"
        self._attributes: dict[str, Any] = {}

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_nb_alarms_sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return attributes for the sensor."""
        return self._attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = EdilkaminWrapper.get_nb_alarms(self.coordinator.data)
        alarms = EdilkaminWrapper.get_alarms(self.coordinator.data)

        errors = {
            "errors": [],
        }

        for alarm in alarms:
            data = {
                "type": alarm["type"],
                "timestamp": time.strftime(
                    "%d-%m-%Y %H:%M:%S", time.localtime(alarm["timestamp"])
                ),
            }
            errors["errors"].append(data)

        self._attributes = errors
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return


class EdilkaminActualPowerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator: CoordinatorEntity, mac_address: str):
        """Initialize the sensor."""
        self._state = None
        self.coordinator = coordinator
        self.mac_address = mac_address

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_POWER

    @property
    def native_unit_of_measurement(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return None

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_actual_power"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = EdilkaminWrapper.get_actual_power(self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            await self.async_write_ha_state()
        except HttpException as err:
            _LOGGER.error(str(err))
            return
