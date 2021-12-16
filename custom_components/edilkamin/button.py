"""Platform for sensor integration."""
from __future__ import annotations

import logging
from homeassistant.components.button import ButtonEntity
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
            EdilkaminChecConfigButton(
                EdilkaminAsyncApi(mac_address=mac_address, session=session)
            )
        ]
    )


class EdilkaminChecConfigButton(ButtonEntity):
    """Representation of a Sensor."""

    def __init__(self, api: EdilkaminAsyncApi):
        """Initialize the sensor."""
        self._state = None
        self.api = api
        self.mac_address = api.get_mac_address()
        self._attr_icon = "mdi:robot"

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.mac_address}_check_config_button"

    async def async_press(self) -> None:
        """Check configuration."""
        try:
            await self.api.check()
            self._state = False
            self.async_write_ha_state()
            self.hass.components.persistent_notification.async_create(
                "Button pressed", title="Button"
            )
        except HttpException as err:
            self._state = True
            _LOGGER.error(str(err))
            return
