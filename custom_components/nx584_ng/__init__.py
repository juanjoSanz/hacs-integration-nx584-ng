import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pynx584 import client

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List the platforms that this integration supports
PLATFORMS: list[str] = ["binary_sensor", "alarm_control_panel"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NX584 from a config entry."""
    host = entry.data["host"]
    port = entry.data["port"]
    
    # Initialize the synchronous pynx584 client
    api = client.Client(host, port)

    async def async_update_data():
        """Fetch data from NX584 with auto-reconnect logic."""
        try:
            # We fetch zones using the executor loop since pynx584 is blocking I/O.
            # In pynx584, zone updates typically carry the connection/state 
            # flags needed for the alarm system as well.
            zones = await hass.async_add_executor_job(api.list_zones)
            return {
                "zones": zones,
                "api": api  # Keep the api instance handy for sending commands
            }
        except Exception as err:
            # If this raises UpdateFailed, the DataUpdateCoordinator will automatically 
            # catch it, set entities to 'unavailable', and retry next interval.
            raise UpdateFailed(f"Error communicating with NX584 gateway: {err}")

    # Configure the global polling manager
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="NX584 Zones",
        update_method=async_update_data,
        update_interval=timedelta(seconds=10),
    )

    # Perform the first refresh immediately during startup/setup
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator instance so platforms can access it
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to binary_sensor.py and alarm_control_panel.py
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register the manual "refresh_data" service declared in services.yaml
    async def handle_refresh(call: ServiceCall) -> None:
        """Force the coordinator to pull fresh data immediately."""
        _LOGGER.debug("Forcing immediate NX584 data refresh via service call")
        await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, "refresh_data", handle_refresh)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an NX584 config entry (e.g., when deleting or reloading)."""
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Remove the stored data tracking
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # If no entries are left for this integration, unregister the service
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "refresh_data")
            hass.data.pop(DOMAIN)

    return unload_ok