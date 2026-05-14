from __future__ import annotations

import logging

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelState,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NX584DataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator: NX584DataCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([NX584NGAlarmPanel(coordinator)])


class NX584NGAlarmPanel(CoordinatorEntity, AlarmControlPanelEntity):
    """NX584-NG Alarm Panel (HA-core-aligned design)."""

    _attr_name = "NX584-NG"
    _attr_unique_id = "nx584_ng_alarm_panel"

    def __init__(self, coordinator: NX584DataCoordinator):
        super().__init__(coordinator)

    # -----------------------------
    # STATE MAPPING (CORE STYLE)
    # -----------------------------

    @property
    def alarm_state(self) -> AlarmControlPanelState:
        """Map system state -> HA alarm state."""

        state = self.coordinator.data.get("system_state")

        if state == "armed_home":
            return AlarmControlPanelState.ARMED_HOME

        if state == "armed_away":
            return AlarmControlPanelState.ARMED_AWAY

        if state == "triggered":
            return AlarmControlPanelState.TRIGGERED

        if state == "arming":
            return AlarmControlPanelState.ARMING

        if state == "disarming":
            return AlarmControlPanelState.DISARMING

        return AlarmControlPanelState.DISARMED

    # -----------------------------
    # FEATURES (IMPORTANT)
    # -----------------------------

    @property
    def supported_features(self) -> AlarmControlPanelEntityFeature:
        return (
            AlarmControlPanelEntityFeature.ARM_HOME
            | AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.DISARM
        )

    # -----------------------------
    # ARM / DISARM ACTIONS
    # -----------------------------

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm home."""

        await self.coordinator.client.arm_home()
        await self.coordinator.async_request_refresh()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Arm away."""

        await self.coordinator.client.arm_away()
        await self.coordinator.async_request_refresh()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm."""

        await self.coordinator.client.disarm()
        await self.coordinator.async_request_refresh()

    # -----------------------------
    # OPTIONAL UX SAFETY
    # -----------------------------

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success