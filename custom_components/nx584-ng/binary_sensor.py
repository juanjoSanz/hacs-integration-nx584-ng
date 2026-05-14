from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up NX584 binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        NX584ZoneSensor(coordinator, zone["number"], zone["name"])
        for zone in coordinator.data["zones"]
    )

class NX584ZoneSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an NX584 zone."""

    def __init__(self, coordinator, zone_number, name):
        super().__init__(coordinator)
        self._zone_number = zone_number
        self._attr_name = name
        self._attr_unique_id = f"nx584_zone_{zone_number}_{coordinator.config_entry.entry_id}"
        self._attr_device_class = BinarySensorDeviceClass.OPENING

    @property
    def is_on(self):
        """Check if the specific zone is faulted."""
        zones = self.coordinator.data.get("zones", [])
        zone = next((z for z in zones if z["number"] == self._zone_number), None)
        # In pynx584, 'faulted' is usually a boolean or key in flags
        return zone.get("faulted", False) if zone else False
