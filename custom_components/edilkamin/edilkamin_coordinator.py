from datetime import timedelta
import logging

import async_timeout
from config.custom_components.edilkamin.edilkamin_async_api import (
    EdilkaminAsyncApi,
    HttpException,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)


class EdilkaminCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, name: str, edilkamin_api: EdilkaminAsyncApi):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=name,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self.edilkamin_api = edilkamin_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with async_timeout.timeout(10):
                return await self.edilkamin_api.fetch_data()
        except HttpException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
