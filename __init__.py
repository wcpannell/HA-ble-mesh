"""The BLE Mesh Environmental Sensing integration."""
from __future__ import annotations

import async_timeout
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_DEVICE
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .mesh_gateway import (
    Interface as MeshInterface,
    EnviroNode as MeshEnviroNode,
)
from .const import DOMAIN, DATA_KEY_API, COORDINATOR, PLATFORMS

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BLE Mesh Environmental Sensing from a config entry."""
    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    device = entry.data[CONF_DEVICE]
    try:
        api = MeshInterface(device)
    except Exception as e:
        raise ConfigEntryNotReady(
            f" Unable to open BLEMesh device on port: {device}"
        ) from e

    async def async_update_data():
        """Grab message from Gateway Node"""
        async with async_timeout.timeout(10):
            return await hass.async_add_executor_job(api.update_nodes)

    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {DATA_KEY_API: api}
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="BLEMesh Message Updates",
            update_method=async_update_data,
            update_interval=timedelta(seconds=5),
        ),
    }

    await hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ].async_config_entry_first_refresh()

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        # If implement a close in api, assign this to api and call
        # api.close()
        hass.data[DOMAIN].pop(entry.entry_id)[DATA_KEY_API]

    return unload_ok
