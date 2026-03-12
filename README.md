# My Weather

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS Action](https://github.com/DOliana/ha-my-weather/actions/workflows/validate.yml/badge.svg)](https://github.com/DOliana/ha-my-weather/actions/workflows/validate.yml)

A Home Assistant custom integration that combines a base weather forecast entity with local sensors. Local sensor values override the base weather data when available, giving you more accurate current conditions while keeping forecasts from your preferred weather provider.

## Features

- Use any weather integration as a base (e.g. Met.no, OpenWeatherMap)
- Override individual weather attributes with local sensor data
- Supports: temperature, apparent temperature, dew point, pressure, humidity, wind speed, wind bearing, visibility, cloud coverage, UV index, ozone
- Rain sensor support — binary sensor or numeric rain rate to override the weather condition
- Daily and hourly forecasts passed through from the base weather entity
- Full config flow UI — no YAML needed

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right and select **Custom repositories**
3. Add `https://github.com/DOliana/ha-my-weather` with category **Integration**
4. Click **Install**
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/my_weather` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **My Weather**
3. Select a base weather entity and optionally assign local sensors for each attribute
4. Sensors can be changed later via the integration's **Configure** button

## How it works

The integration creates a weather entity that reads current conditions from your local sensors (when available) and falls back to the base weather entity's values otherwise. Forecasts (daily and hourly) are always sourced from the base weather entity.

## License

[MIT](LICENSE)
