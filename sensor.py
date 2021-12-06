"""Platform for Environmental Sensor Integration"""
from __future__ import annotations

import logging

from .mesh_gateway import (
    SensorTypes as MeshSensorTypes,
    Interface as MeshInterface,
    EnviroNode as MeshEnviroNode,
)

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    DEVICE_CLASS_HUMIDITY,
    PERCENTAGE,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    PLATFORMS,
    DOMAIN,
    COORDINATOR,
)

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BLE Mesh sensor from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    entities = []
    # You could also enumerate the results in coordinator.data to build the
    # list inside async_add_entities
    entities.append(
        MeshSensorNode(coordinator, 0, MeshSensorTypes.Temperature)
    )
    entities.append(MeshSensorNode(coordinator, 0, MeshSensorTypes.Humidity))
    entities.append(
        MeshSensorNode(coordinator, 1, MeshSensorTypes.Temperature)
    )
    entities.append(MeshSensorNode(coordinator, 1, MeshSensorTypes.Humidity))
    async_add_entities(entities)


class MeshSensorNode(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, idx: int, sensor_type: MeshSensorTypes):
        super().__init__(coordinator)
        self.idx = idx
        self._type = sensor_type
        if self._type == MeshSensorTypes.Temperature:
            self._attr_device_class = DEVICE_CLASS_TEMPERATURE
            self._attr_native_unit_of_measurement = TEMP_CELSIUS
        elif self._type == MeshSensorTypes.Humidity:
            self._attr_device_class = DEVICE_CLASS_HUMIDITY
            self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def name(self) -> str | None:
        if self.coordinator.data is None:
            return None
        if self.idx < len(self.coordinator.data):
            return self.coordinator.data[self.idx].node_name
        else:
            return None

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return str(self.coordinator.data[self.idx].state[self._type])
