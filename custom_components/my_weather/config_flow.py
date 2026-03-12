"""Config flow for Weather Combined."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

DOMAIN = "my_weather"

WEATHER_ENTITY_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="weather")
)

TEMPERATURE_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
)
PRESSURE_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="pressure")
)
WIND_SPEED_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="wind_speed")
)
HUMIDITY_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="humidity")
)
VISIBILITY_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor", device_class="distance")
)
UV_INDEX_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor")
)
# No standard device_class for wind bearing — allow any sensor
GENERIC_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain="sensor")
)
RAIN_SENSOR_SELECTOR = selector.EntitySelector(
    selector.EntitySelectorConfig(domain=["sensor", "binary_sensor"])
)

# Maps each sensor key to its selector
SENSOR_SELECTORS: dict[str, selector.EntitySelector] = {
    "temperature_sensor": TEMPERATURE_SENSOR_SELECTOR,
    "apparent_temperature_sensor": TEMPERATURE_SENSOR_SELECTOR,
    "dew_point_sensor": TEMPERATURE_SENSOR_SELECTOR,
    "pressure_sensor": PRESSURE_SENSOR_SELECTOR,
    "humidity_sensor": HUMIDITY_SENSOR_SELECTOR,
    "wind_speed_sensor": WIND_SPEED_SENSOR_SELECTOR,
    "wind_bearing_sensor": GENERIC_SENSOR_SELECTOR,
    "visibility_sensor": VISIBILITY_SENSOR_SELECTOR,
    "cloud_coverage_sensor": GENERIC_SENSOR_SELECTOR,
    "uv_index_sensor": UV_INDEX_SENSOR_SELECTOR,
    "ozone_sensor": GENERIC_SENSOR_SELECTOR,
    "rain_sensor": RAIN_SENSOR_SELECTOR,
}

SENSOR_KEYS = list(SENSOR_SELECTORS.keys())

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="My Weather"): str,
        vol.Required("base_weather"): WEATHER_ENTITY_SELECTOR,
        **{vol.Optional(k): s for k, s in SENSOR_SELECTORS.items()},
    }
)


def _build_options_schema(
    defaults: dict[str, Any],
) -> vol.Schema:
    """Build the options schema with current values as defaults."""
    schema = {}
    for key, sel in SENSOR_SELECTORS.items():
        current = defaults.get(key)
        schema[vol.Optional(key, description={"suggested_value": current})] = sel
    return vol.Schema(schema)


class MyWeatherConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle a config flow for My Weather."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MyWeatherOptionsFlow:
        """Get the options flow."""
        return MyWeatherOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Store sensor config in options, keep name + base_weather in data
            data = {
                CONF_NAME: user_input[CONF_NAME],
                "base_weather": user_input["base_weather"],
            }
            options = {k: user_input[k] for k in SENSOR_KEYS if k in user_input}
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=data,
                options=options,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )


class MyWeatherOptionsFlow(config_entries.OptionsFlow):
    """Handle options for My Weather."""


    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage sensor options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema(dict(self.config_entry.options)),
        )
