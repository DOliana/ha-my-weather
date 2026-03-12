"""Weather platform for Weather Combined."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required("base_weather"): cv.entity_id,
        vol.Optional("temperature_sensor"): cv.entity_id,
        vol.Optional("apparent_temperature_sensor"): cv.entity_id,
        vol.Optional("dew_point_sensor"): cv.entity_id,
        vol.Optional("pressure_sensor"): cv.entity_id,
        vol.Optional("humidity_sensor"): cv.entity_id,
        vol.Optional("wind_speed_sensor"): cv.entity_id,
        vol.Optional("wind_bearing_sensor"): cv.entity_id,
        vol.Optional("visibility_sensor"): cv.entity_id,
        vol.Optional("cloud_coverage_sensor"): cv.entity_id,
        vol.Optional("uv_index_sensor"): cv.entity_id,
        vol.Optional("ozone_sensor"): cv.entity_id,
        vol.Optional("rain_sensor"): cv.entity_id,
        vol.Optional(CONF_NAME, default="Weather Combined"): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up My Weather platform via YAML."""
    async_add_entities([MyWeatherEntity(hass, config)], True)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up My Weather platform via config entry."""
    # Merge data (name, base_weather) with options (sensors)
    config = {**entry.data, **entry.options}
    async_add_entities([MyWeatherEntity(hass, config)], True)


class MyWeatherEntity(WeatherEntity):
    """Weather entity that combines local sensors with a base weather entity."""

    _attr_has_entity_name = True
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the weather entity."""
        self.hass = hass
        name = config.get(CONF_NAME, "My Weather")
        self._attr_name = None
        self._attr_unique_id = f"my_weather_{name}"
        self._attr_device_info = DeviceInfo(
            identifiers={("my_weather", name)},
            name=name,
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="My Weather",
        )
        
        self._base_weather = config["base_weather"]
        self._temperature_sensor = config.get("temperature_sensor")
        self._apparent_temperature_sensor = config.get("apparent_temperature_sensor")
        self._dew_point_sensor = config.get("dew_point_sensor")
        self._pressure_sensor = config.get("pressure_sensor")
        self._humidity_sensor = config.get("humidity_sensor")
        self._wind_speed_sensor = config.get("wind_speed_sensor")
        self._wind_bearing_sensor = config.get("wind_bearing_sensor")
        self._visibility_sensor = config.get("visibility_sensor")
        self._cloud_coverage_sensor = config.get("cloud_coverage_sensor")
        self._uv_index_sensor = config.get("uv_index_sensor")
        self._ozone_sensor = config.get("ozone_sensor")
        self._rain_sensor = config.get("rain_sensor")
        
        self._attr_condition = None
        self._attr_native_temperature = None
        self._attr_native_apparent_temperature = None
        self._attr_native_dew_point = None
        self._attr_native_pressure = None
        self._attr_native_wind_speed = None
        self._attr_humidity = None
        self._attr_wind_bearing = None
        self._attr_native_visibility = None
        self._attr_cloud_coverage = None
        self._attr_uv_index = None
        self._attr_ozone = None

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        entities_to_track = [self._base_weather]
        for sensor in [
            self._temperature_sensor,
            self._apparent_temperature_sensor,
            self._dew_point_sensor,
            self._pressure_sensor,
            self._humidity_sensor,
            self._wind_speed_sensor,
            self._wind_bearing_sensor,
            self._visibility_sensor,
            self._cloud_coverage_sensor,
            self._uv_index_sensor,
            self._ozone_sensor,
            self._rain_sensor,
        ]:
            if sensor:
                entities_to_track.append(sensor)
        
        async_track_state_change_event(
            self.hass, entities_to_track, self._async_update_event
        )
        
        # Initial update
        await self.async_update()

    @callback
    def _async_update_event(self, event):
        """Update when state changes."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        """Update the entity."""
        base_weather_state = self.hass.states.get(self._base_weather)
        if not base_weather_state:
            return

        # Get base weather attributes
        base_attrs = base_weather_state.attributes
        
        # Temperature - use sensor if available, otherwise base weather
        if self._temperature_sensor:
            temp_state = self.hass.states.get(self._temperature_sensor)
            if temp_state and temp_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_native_temperature = float(temp_state.state)
                except (ValueError, TypeError):
                    self._attr_native_temperature = base_attrs.get("temperature")
            else:
                self._attr_native_temperature = base_attrs.get("temperature")
        else:
            self._attr_native_temperature = base_attrs.get("temperature")

        # Pressure - use sensor if available, otherwise base weather
        if self._pressure_sensor:
            pressure_state = self.hass.states.get(self._pressure_sensor)
            if pressure_state and pressure_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_native_pressure = float(pressure_state.state)
                except (ValueError, TypeError):
                    self._attr_native_pressure = base_attrs.get("pressure")
            else:
                self._attr_native_pressure = base_attrs.get("pressure")
        else:
            self._attr_native_pressure = base_attrs.get("pressure")

        # Wind speed - use sensor if available, otherwise base weather
        if self._wind_speed_sensor:
            wind_state = self.hass.states.get(self._wind_speed_sensor)
            if wind_state and wind_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_native_wind_speed = float(wind_state.state)
                except (ValueError, TypeError):
                    self._attr_native_wind_speed = base_attrs.get("wind_speed")
            else:
                self._attr_native_wind_speed = base_attrs.get("wind_speed")
        else:
            self._attr_native_wind_speed = base_attrs.get("wind_speed")

        # Apparent temperature - use sensor if available, otherwise base weather
        if self._apparent_temperature_sensor:
            at_state = self.hass.states.get(self._apparent_temperature_sensor)
            if at_state and at_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_native_apparent_temperature = float(at_state.state)
                except (ValueError, TypeError):
                    self._attr_native_apparent_temperature = base_attrs.get("apparent_temperature")
            else:
                self._attr_native_apparent_temperature = base_attrs.get("apparent_temperature")
        else:
            self._attr_native_apparent_temperature = base_attrs.get("apparent_temperature")

        # Dew point - use sensor if available, otherwise base weather
        if self._dew_point_sensor:
            dp_state = self.hass.states.get(self._dew_point_sensor)
            if dp_state and dp_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_native_dew_point = float(dp_state.state)
                except (ValueError, TypeError):
                    self._attr_native_dew_point = base_attrs.get("dew_point")
            else:
                self._attr_native_dew_point = base_attrs.get("dew_point")
        else:
            self._attr_native_dew_point = base_attrs.get("dew_point")

        # Visibility - use sensor if available, otherwise base weather
        if self._visibility_sensor:
            vis_state = self.hass.states.get(self._visibility_sensor)
            if vis_state and vis_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_native_visibility = float(vis_state.state)
                except (ValueError, TypeError):
                    self._attr_native_visibility = base_attrs.get("visibility")
            else:
                self._attr_native_visibility = base_attrs.get("visibility")
        else:
            self._attr_native_visibility = base_attrs.get("visibility")

        # Cloud coverage - use sensor if available, otherwise base weather
        if self._cloud_coverage_sensor:
            cc_state = self.hass.states.get(self._cloud_coverage_sensor)
            if cc_state and cc_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_cloud_coverage = float(cc_state.state)
                except (ValueError, TypeError):
                    self._attr_cloud_coverage = base_attrs.get("cloud_coverage")
            else:
                self._attr_cloud_coverage = base_attrs.get("cloud_coverage")
        else:
            self._attr_cloud_coverage = base_attrs.get("cloud_coverage")

        # UV index - use sensor if available, otherwise base weather
        if self._uv_index_sensor:
            uv_state = self.hass.states.get(self._uv_index_sensor)
            if uv_state and uv_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_uv_index = float(uv_state.state)
                except (ValueError, TypeError):
                    self._attr_uv_index = base_attrs.get("uv_index")
            else:
                self._attr_uv_index = base_attrs.get("uv_index")
        else:
            self._attr_uv_index = base_attrs.get("uv_index")

        # Ozone - use sensor if available, otherwise base weather
        if self._ozone_sensor:
            oz_state = self.hass.states.get(self._ozone_sensor)
            if oz_state and oz_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_ozone = float(oz_state.state)
                except (ValueError, TypeError):
                    self._attr_ozone = base_attrs.get("ozone")
            else:
                self._attr_ozone = base_attrs.get("ozone")
        else:
            self._attr_ozone = base_attrs.get("ozone")

        # Condition - check rain sensor, otherwise use base weather
        if self._rain_sensor:
            rain_state = self.hass.states.get(self._rain_sensor)
            if rain_state and rain_state.state not in ["unknown", "unavailable"]:
                state_lower = str(rain_state.state).lower()
                # Binary sensor or boolean-like
                if state_lower in ["on", "yes", "true", "1"]:
                    self._attr_condition = "rainy"
                else:
                    # Numeric rain rate (e.g. mm/h) — treat >0 as rain
                    try:
                        if float(rain_state.state) > 0:
                            self._attr_condition = "rainy"
                        else:
                            self._attr_condition = base_weather_state.state
                    except (ValueError, TypeError):
                        self._attr_condition = base_weather_state.state
            else:
                self._attr_condition = base_weather_state.state
        else:
            self._attr_condition = base_weather_state.state

        # Humidity - use sensor if available, otherwise base weather
        if self._humidity_sensor:
            humidity_state = self.hass.states.get(self._humidity_sensor)
            if humidity_state and humidity_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_humidity = float(humidity_state.state)
                except (ValueError, TypeError):
                    self._attr_humidity = base_attrs.get("humidity")
            else:
                self._attr_humidity = base_attrs.get("humidity")
        else:
            self._attr_humidity = base_attrs.get("humidity")

        # Wind bearing - use sensor if available, otherwise base weather
        if self._wind_bearing_sensor:
            bearing_state = self.hass.states.get(self._wind_bearing_sensor)
            if bearing_state and bearing_state.state not in ["unknown", "unavailable"]:
                try:
                    self._attr_wind_bearing = float(bearing_state.state)
                except (ValueError, TypeError):
                    self._attr_wind_bearing = base_attrs.get("wind_bearing")
            else:
                self._attr_wind_bearing = base_attrs.get("wind_bearing")
        else:
            self._attr_wind_bearing = base_attrs.get("wind_bearing")

    async def _async_get_base_forecast(
        self, forecast_type: str
    ) -> list[dict[str, Any]] | None:
        """Fetch forecast from the base weather entity via the weather.get_forecasts service."""
        try:
            response = await self.hass.services.async_call(
                "weather",
                "get_forecasts",
                {"entity_id": self._base_weather, "type": forecast_type},
                blocking=True,
                return_response=True,
            )
            if response and self._base_weather in response:
                return response[self._base_weather].get("forecast")
        except Exception:
            _LOGGER.debug(
                "Failed to get %s forecast from %s",
                forecast_type,
                self._base_weather,
            )
        return None

    async def async_forecast_daily(self) -> list[dict[str, Any]] | None:
        """Return the daily forecast from the base weather entity."""
        return await self._async_get_base_forecast("daily")

    async def async_forecast_hourly(self) -> list[dict[str, Any]] | None:
        """Return the hourly forecast from the base weather entity."""
        return await self._async_get_base_forecast("hourly")
