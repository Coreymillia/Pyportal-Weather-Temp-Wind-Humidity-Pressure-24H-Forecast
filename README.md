# PyPortal Weather Station

A CircuitPython weather display for the **Adafruit PyPortal** that shows current conditions and a 3-hour forecast using the [OpenWeatherMap API](https://openweathermap.org/).

![PyPortal Weather Station](weather_background.bmp)

---

## Features

- Current temperature (°F), feels like, wind speed & direction, humidity, pressure
- Live weather icon pulled from OpenWeatherMap
- 5-slot rolling 3-hour forecast strip
- Time synced from the internet (12-hour AM/PM)
- Weather refreshes every 10 minutes, time syncs every hour

---

## Hardware Required

- [Adafruit PyPortal](https://www.adafruit.com/product/4116)
- USB cable + power source

---

## Software / Libraries Required

Install **CircuitPython** on your PyPortal and then copy the following libraries from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries) into the `lib/` folder on your CIRCUITPY drive:

| Library | Folder/File |
|---|---|
| adafruit_pyportal | `lib/adafruit_pyportal/` |
| adafruit_portalbase | `lib/adafruit_portalbase/` |
| adafruit_display_text | `lib/adafruit_display_text/` |
| adafruit_bitmap_font | `lib/adafruit_bitmap_font/` |
| adafruit_requests | `lib/adafruit_requests.mpy` |
| adafruit_esp32spi | `lib/adafruit_esp32spi/` |
| neopixel | `lib/neopixel.mpy` |

---

## Setup

### 1. Get API Keys

- **OpenWeatherMap** – Free API key at [openweathermap.org](https://home.openweathermap.org/users/sign_up)
- **Adafruit IO** – Free account & key at [io.adafruit.com](https://io.adafruit.com) (used for time sync)

### 2. Configure `settings.toml`

Copy `settings.toml` to the root of your CIRCUITPY drive and fill in your credentials:

```toml
CIRCUITPY_WIFI_SSID = "your-wifi-ssid"
CIRCUITPY_WIFI_PASSWORD = "your-wifi-password"
ADAFRUIT_AIO_USERNAME = "your-adafruit-io-username"
ADAFRUIT_AIO_KEY = "your-adafruit-io-key"
openweather_token = "your-openweathermap-api-key"
```

### 3. (Optional) Configure `secrets.py`

Some older CircuitPython builds use `secrets.py` instead of `settings.toml`. If needed, copy `secrets.py` to your CIRCUITPY drive and fill in the same values.

### 4. Set Your Location

Open `code.py` and update the latitude/longitude near the top:

```python
LAT = "38.7253"   # <-- your latitude
LON = "-105.1397" # <-- your longitude
```

Find your coordinates at [latlong.net](https://www.latlong.net/).

### 5. Copy Files to PyPortal

Copy all of the following to the **root** of your CIRCUITPY drive:

```
code.py
openweather_graphics.py
settings.toml          ← your filled-in version
secrets.py             ← your filled-in version (if needed)
weather_background.bmp
fonts/
icons/
```

### 6. Power On

The PyPortal will connect to WiFi, sync the time, fetch weather data, and display it automatically.

---

## File Overview

| File | Description |
|---|---|
| `code.py` | Main program — WiFi setup, API calls, refresh loop |
| `openweather_graphics.py` | Display layout — labels, icons, forecast rendering |
| `settings.toml` | **Template** — add your credentials here (do not commit with real values) |
| `secrets.py` | **Template** — legacy credentials file for older CircuitPython builds |
| `weather_background.bmp` | Background image displayed on the PyPortal screen |
| `fonts/` | BDF bitmap fonts used for text rendering |
| `icons/` | BMP weather condition icons from OpenWeatherMap |

---

## Customization

- **Units**: Change `celsius=False` to `celsius=True` in `code.py` line 54 for Celsius.
- **Refresh rate**: Adjust the `> 600` (10 min) and `> 3600` (1 hr) values in `code.py`.
- **Timezone**: Update `'timezone'` in `secrets.py` using a value from [worldtimeapi.org/timezones](http://worldtimeapi.org/timezones).

---

## License

Based on original work by Limor Fried for Adafruit Industries — MIT License.
