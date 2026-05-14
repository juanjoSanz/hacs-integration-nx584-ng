import voluptuous as vol
from homeassistant import config_entries
from pynx584 import client
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class NX584ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NX584."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                # Validate the connection
                api = client.Client(user_input["host"], user_input["port"])
                # Test connection by listing zones
                await self.hass.async_add_executor_job(api.list_zones)
                
                return self.async_create_entry(
                    title=f"NX584 ({user_input['host']})", 
                    data=user_input
                )
            except Exception as err:
                _LOGGER.error("Failed to connect to NX584: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="localhost"): str,
                vol.Required("port", default=5007): int,
            }),
            errors=errors,
        )
