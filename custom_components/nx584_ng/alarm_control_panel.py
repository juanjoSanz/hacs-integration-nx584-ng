from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NX584 Alarm Control Panel."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NX584AlarmPanel(coordinator)])

class NX584AlarmPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """Representation of an NX584 Alarm Control Panel."""

    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "NX584 Alarm Panel"
        self._attr_unique_id = f"nx584_panel_{coordinator.config_entry.entry_id}"

    @property
    def alarm_state(self):
        """Return the state of the alarm based on coordinator data."""
        # Note: pynx584 returns partition info inside zone list or a separate status call.
        # This implementation assumes the standard mapping.
        # You might need to refine this based on your specific panel's flags.
        zones = self.coordinator.data.get("zones", [])
        if not zones:
            return None

        # Logic: If any zone reports armed status, or use partition status if available
        # This is a simplified check for demo:
        return AlarmControlPanelState.DISARMED

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        api = self.coordinator.data["api"]
        await self.hass.async_add_executor_job(api.disarm, code)
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_home(self, code=None):
        """Send arm home command."""
        api = self.coordinator.data["api"]
        await self.hass.async_add_executor_job(api.arm_home)
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        api = self.coordinator.data["api"]
        await self.hass.async_add_executor_job(api.arm_away)
        await self.coordinator.async_request_refresh()
