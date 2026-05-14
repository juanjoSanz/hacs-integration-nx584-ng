from __future__ import annotations

import logging

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NX584DataCoordinator

_LOGGER = logging.getLogger(__name__)


# -----------------------------
# SETUP
# -----------------------------

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up NX584-NG alarm panel."""

    coordinator: NX584DataCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        NX584AlarmPanel(coordinator)
    ])


# -----------------------------
# ENTITY
# -----------------------------

class NX584AlarmPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """NX584-NG alarm control panel."""

    def __init__(self, coordinator: NX584DataCoordinator):
        super().__init__(coordinator)

        self._attr_unique_id = "nx584_ng_panel"
        self._attr_name = "NX584-NG Alarm Panel"

    # -------------------------
    # STATE MAPPING
    # -------------------------

    @property
    def alarm_state(self) -> AlarmControlPanelState:
        """
        Derive panel state from zone data.

        Logic:
        - If any zone is in alarm → TRIGGERED
        - If any zone is faulted → TRIGGERED (optional safety choice)
        - If system armed flag exists → ARMED_AWAY
        - Else → DISARMED
        """

        zones = self.coordinator.data.get("zones", [])

        if not zones:
            return AlarmControlPanelState.UNKNOWN

        any_open = any(z.get("is_open") for z in zones)
        any_fault = any(z.get("is_faulted") for z in zones)

        # If something is actively triggered
        if any_open or any_fault:
            return AlarmControlPanelState.TRIGGERED

        # If backend exposes armed state later, plug it here
        system_state = self.coordinator.data.get("system_state")

        if system_state == "armed_away":
            return AlarmControlPanelState.ARMED_AWAY
        if system_state == "armed_home":
            return AlarmControlPanelState.ARMED_HOME

        return AlarmControlPanelState.DISARMED

    # -------------------------
    # ARM / DISARM ACTIONS
    # -------------------------

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm home mode."""
        _LOGGER.debug("Arming NX584-NG HOME")

        await self.coordinator.client.arm_home()
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Arm away mode."""
        _LOGGER.debug("Arming NX584-NG AWAY")

        await self.coordinator.client.arm_away()
        await self.coordinator.async_request_refresh()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm system."""
        _LOGGER.debug("Disarming NX584-NG")

        await self.coordinator.client.disarm()
        await self.coordinator.async_request_refresh()

    # -------------------------
    # OPTIONAL UI ENHANCEMENTS
    # -------------------------

    @property
    def available(self) -> bool:
        """Entity availability based on coordinator."""
        return self.coordinator.last_update_success

    @property
    def name(self) -> str:
        return "NX584-NG Alarm Panel"