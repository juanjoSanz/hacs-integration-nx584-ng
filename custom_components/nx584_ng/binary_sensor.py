from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NX584DataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up binary sensors for NX584-NG."""

    coordinator: NX584DataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        NX584ZoneBinarySensor(coordinator, zone)
        for zone in coordinator.data.get("zones", [])
    ]

    async_add_entities(entities)


class NX584ZoneBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an NX584 zone."""

    def __init__(self, coordinator: NX584DataCoordinator, zone: dict):
        super().__init__(coordinator)

        self._zone_number = zone["number"]
        self._initial_name = zone.get("name", f"Zone {self._zone_number}")

        self._attr_unique_id = f"nx584_ng_zone_{self._zone_number}"
        self._attr_device_class = BinarySensorDeviceClass.MOTION

    # -------------------------
    # Core state logic
    # -------------------------

    @property
    def is_on(self) -> bool:
        """Return True if zone is open/triggered."""

        zone = self._get_zone()
        if not zone:
            return False

        return bool(zone.get("is_open", False))

    # -------------------------
    # Attributes
    # -------------------------

    @property
    def name(self) -> str:
        """Entity name."""

        zone = self._get_zone()
        if not zone:
            return self._initial_name

        return zone.get("name", self._initial_name)

    @property
    def extra_state_attributes(self):
        """Expose NX-specific metadata."""

        zone = self._get_zone()
        if not zone:
            return {}

        return {
            "zone_number": zone.get("number"),
            "bypassed": zone.get("bypassed"),
            "faulted": zone.get("is_faulted"),
            "condition_flags": zone.get("condition_flags", []),
            "type_flags": zone.get("type_flags", []),
        }

    # -------------------------
    # Helpers
    # -------------------------

    def _get_zone(self) -> dict | None:
        """Find zone in coordinator data."""

        zones = self.coordinator.data.get("zones", [])

        for zone in zones:
            if zone.get("number") == self._zone_number:
                return zone

        return None