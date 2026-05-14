from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SERVER_HOST, CONF_SERVER_PORT, CONF_ALARM_NAME
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, DEFAULT_ALARM_NAME

_LOGGER = logging.getLogger(__name__)


class NX584NGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NX584-NG."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        errors = {}

        if user_input is not None:
            host = user_input[CONF_SERVER_HOST]
            port = user_input[CONF_SERVER_PORT]
            name = user_input[CONF_ALARM_NAME]
            

            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"NX584-NG ({host})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERVER_HOST, default="DEFAULT_SERVER_HOST"): str,
                    vol.Optional(CONF_SERVER_PORT, default=DEFAULT_SERVER_PORT): int,
                    vol.Optional(CONF_ALARM_NAME, default="DEFAULT_ALARM_NAME"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NX584NGOptionsFlowHandler(config_entry)


class NX584NGOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle NX584-NG options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )