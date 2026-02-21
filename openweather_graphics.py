# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import json
import gc
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

cwd = ("/"+__file__).rsplit('/', 1)[0]

small_font  = cwd+"/fonts/Arial-12.bdf"
medium_font = cwd+"/fonts/Arial-16.bdf"
large_font  = cwd+"/fonts/Arial-Bold-24.bdf"

COND_SHORT = {
    'Clear': 'Clear', 'Clouds': 'Cloudy', 'Rain': 'Rain',
    'Drizzle': 'Drzl', 'Snow': 'Snow', 'Thunderstorm': 'Storm',
    'Mist': 'Mist', 'Fog': 'Fog', 'Haze': 'Haze',
    'Smoke': 'Smoke', 'Dust': 'Dust', 'Tornado': 'Torn',
}
DOW  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FC_X = [4, 68, 132, 196, 260]
DIRS = ['N','NE','E','SE','S','SW','W','NW']


class OpenWeather_Graphics(displayio.Group):

    def __init__(self, root_group, *, am_pm=True, celsius=False):
        super().__init__()
        self.am_pm   = am_pm
        self.celsius = celsius

        root_group.append(self)
        self._icon_group = displayio.Group()
        self.append(self._icon_group)
        self._text_group = displayio.Group()
        self.append(self._text_group)

        self._icon_sprite = None
        self._icon_file   = None
        self.set_icon(cwd+"/weather_background.bmp")

        self.small_font  = bitmap_font.load_font(small_font)
        self.medium_font = bitmap_font.load_font(medium_font)
        self.large_font  = bitmap_font.load_font(large_font)
        glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: /%'
        for f in (self.small_font, self.medium_font, self.large_font):
            f.load_glyphs(glyphs)
            f.load_glyphs(('°',))

        self.city_text = None

        # Row 1: city (left, lazy) + time (right)
        self.time_text = Label(self.large_font)
        self.time_text.x = 165
        self.time_text.y = 215
        self.time_text.color = 0xFFFF00
        self._text_group.append(self.time_text)

        # Row 2: condition (left) + temp (right)
        self.main_text = Label(self.medium_font)
        self.main_text.x = 88
        self.main_text.y = 30
        self.main_text.color = 0xFFCC00
        self._text_group.append(self.main_text)

        self.temp_text = Label(self.large_font)
        self.temp_text.x = 10
        self.temp_text.y = 215
        self.temp_text.color = 0x00FF00
        self._text_group.append(self.temp_text)

        # Row 3: description (left) + feels like (right)
        self.description_text = Label(self.medium_font)
        self.description_text.x = 10
        self.description_text.y = 178
        self.description_text.color = 0x55AAFF
        self._text_group.append(self.description_text)

        self.feels_text = Label(self.medium_font)
        self.feels_text.x = 88
        self.feels_text.y = 50
        self.feels_text.color = 0xFFAA44
        self._text_group.append(self.feels_text)

        # Row 4: wind (left) + humidity (right)
        self.wind_text = Label(self.medium_font)
        self.wind_text.x = 10
        self.wind_text.y = 70
        self.wind_text.color = 0x00CCFF
        self._text_group.append(self.wind_text)

        self.humidity_text = Label(self.medium_font)
        self.humidity_text.x = 10
        self.humidity_text.y = 90
        self.humidity_text.color = 0x00FFCC
        self._text_group.append(self.humidity_text)

        # Row 5: pressure
        self.pressure_text = Label(self.small_font)
        self.pressure_text.x = 10
        self.pressure_text.y = 108
        self.pressure_text.color = 0xCC88FF
        self._text_group.append(self.pressure_text)

        # 5-day forecast: 3 rows x 5 columns
        self.fc_day  = []
        self.fc_hilo = []
        self.fc_cond = []
        for x in FC_X:
            d = Label(self.small_font, text="---")
            d.x = x; d.y = 126; d.color = 0xFFFFFF
            self._text_group.append(d)
            self.fc_day.append(d)

            h = Label(self.small_font, text="--/--")
            h.x = x; h.y = 142; h.color = 0xFFFFFF
            self._text_group.append(h)
            self.fc_hilo.append(h)

            c = Label(self.small_font, text="----")
            c.x = x; c.y = 158; c.color = 0xFFFFFF
            self._text_group.append(c)
            self.fc_cond.append(c)

    def display_weather(self, weather):
        weather = json.loads(weather)

        weather_icon = weather['weather'][0]['icon']
        self.set_icon(cwd+"/icons/"+weather_icon+".bmp")

        city_name = weather['name']
        if not self.city_text:
            self.city_text = Label(self.medium_font, text=city_name)
            self.city_text.x = 88
            self.city_text.y = 10
            self.city_text.color = 0xFFFFFF
            self._text_group.append(self.city_text)

        self.update_time()

        self.main_text.text = weather['weather'][0]['main']

        description = weather['weather'][0]['description']
        self.description_text.text = description[0].upper() + description[1:]

        temperature = weather['main']['temp'] - 273.15
        feels_like  = weather['main']['feels_like'] - 273.15
        humidity    = weather['main']['humidity']
        pressure    = weather['main']['pressure']
        wind_ms     = weather['wind']['speed']
        wind_mph    = wind_ms * 2.237
        wind_dir    = DIRS[int((weather['wind'].get('deg', 0) + 22.5) / 45) % 8]

        if self.celsius:
            self.temp_text.text  = "%d °C" % temperature
            self.feels_text.text = "Feels %d °C" % feels_like
        else:
            self.temp_text.text  = "%d °F" % ((temperature * 9/5) + 32)
            self.feels_text.text = "Feels %d °F" % ((feels_like * 9/5) + 32)

        self.wind_text.text     = "Wind: %.1f mph %s" % (wind_mph, wind_dir)
        self.humidity_text.text = "Humid: %d%%" % humidity
        self.pressure_text.text = "Pres: %.2f in/Hg" % (pressure * 0.02953)

    def display_forecast(self, forecast_json):
        """Show next 5 three-hour forecast slots from the list."""
        try:
            data  = json.loads(forecast_json)
            items = data['list']
            for i in range(min(5, len(items))):
                item = items[i]
                # Time label: e.g. "3PM" from "2026-02-21 15:00:00"
                hour = int(item['dt_txt'][11:13])
                if hour == 0:
                    label = "12AM"
                elif hour < 12:
                    label = "%dAM" % hour
                elif hour == 12:
                    label = "12PM"
                else:
                    label = "%dPM" % (hour - 12)
                hi = int(round((item['main']['temp_max'] - 273.15) * 9/5 + 32))
                lo = int(round((item['main']['temp_min'] - 273.15) * 9/5 + 32))
                cond = item['weather'][0]['main']
                self.fc_day[i].text  = label
                self.fc_hilo[i].text = "%d/%d" % (hi, lo)
                self.fc_cond[i].text = COND_SHORT.get(cond, cond[:5])
            del data, items
            gc.collect()
        except Exception as e:
            print("Forecast error:", e)

    def update_time(self):
        now    = time.localtime()
        hour   = now[3]
        minute = now[4]
        fmt    = "%d:%02d"
        if self.am_pm:
            if hour >= 12:
                hour -= 12
                fmt  += " PM"
            else:
                fmt  += " AM"
            if hour == 0:
                hour = 12
        self.time_text.text = fmt % (hour, minute)

    def set_icon(self, filename):
        print("Set icon to", filename)
        if self._icon_group:
            self._icon_group.pop()
        # Release old sprite and bitmap before loading new one to free memory/file handles
        self._icon_sprite = None
        self._icon_file = None
        gc.collect()
        if not filename:
            return
        self._icon_file = displayio.OnDiskBitmap(filename)
        self._icon_sprite = displayio.TileGrid(self._icon_file, pixel_shader=self._icon_file.pixel_shader)
        self._icon_group.append(self._icon_sprite)
