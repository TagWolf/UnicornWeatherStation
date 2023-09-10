from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN
import network
import ntptime
import time
import urequests as requests
import jpegdec

WIFI_SSID = "YOUR SSID"  # Replace with your SSID
WIFI_PASSWORD = "YOUR WIFI PASSWORD"  # Replace with your password
OPEN_WEATHER_MAP_API_KEY = "YOUR OPENWEATHER API KEY"  # Replace with your API key
CITY = "San Jose"  # Replace with your city
COUNTRY_CODE = "US"  # Replace with your country code
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY_CODE}&units=imperial&APPID={OPEN_WEATHER_MAP_API_KEY}'
UTC_OFFSET = -7 * 3600  # Example for PDT. Adjust as needed.
BUTTON_PRESS_TIMEOUT = 10  # Time in seconds after which the clock will be displayed again

gu = GalacticUnicorn()
graphics = PicoGraphics(display=DISPLAY_GALACTIC_UNICORN)
graphics.set_font("bitmap8")
width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT
WHITE = graphics.create_pen(109, 131, 176)
BLACK = graphics.create_pen(0, 0, 0)
RED = graphics.create_pen(255, 0, 0)
BLUE = graphics.create_pen(0, 0, 255)
display_clock = True
last_button_press_time = None
weather_data = ""
last_weather_fetch_time = 0
WEATHER_FETCH_INTERVAL = 60

button_a_pressed = False
button_b_pressed = False
button_c_pressed = False
button_d_pressed = False

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return True

    wlan.active(True)
    wlan.config(pm=0xa11140)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(0.2)

    return wlan.isconnected()

def sync_time():
    if connect_to_wifi():
        try:
            ntptime.settime()
            tm = time.localtime(time.mktime(time.localtime()) + UTC_OFFSET)
            machine.RTC().datetime((tm[0], tm[1], tm[2], 0, tm[3], tm[4], tm[5], 0))
            print("Time set")
        except OSError:
            pass

def get_weather_data():
    global last_weather_fetch_time, weather_data

    if time.time() - last_weather_fetch_time < WEATHER_FETCH_INTERVAL and weather_data:
        return weather_data

    for _ in range(3):
        try:
            sync_time()
            weather_data = requests.get(URL).json()
            last_weather_fetch_time = time.time()
            print(weather_data)
            return weather_data
        except OSError as e:
            print("Error fetching weather data:", e)
            time.sleep(5)
    else:
        return

def hpa_to_inHg(hpa):
    return hpa * 0.02953

def get_temperature_color(temp):
    if temp <= 32:
        return graphics.create_pen(255, 255, 255)  # White
    elif 32 < temp <= 65:
        decrease_value = int((temp - 32) * (255 / 33))
        return graphics.create_pen(255 - decrease_value, 255 - decrease_value, 255)  # Transition from white to blue
    elif 65 < temp <= 72:
        return graphics.create_pen(0, 0, 255)  # Blue
    elif 72 < temp <= 85:
        red_value = int((temp - 72) * (255 / 13))
        return graphics.create_pen(red_value, red_value, 255 - red_value)  # Transition from blue to yellow
    else:
        return graphics.create_pen(255, 0, 0)  # Red

def get_humidity_color(humidity):
    green_value = int(255 - humidity * 2.55)
    return graphics.create_pen(0, green_value, 255)  # Cyan to blue gradient

def get_wind_speed_color(speed):
    green_value = int(255 - speed * 2.55)  # Assuming max speed is 100mph for full blue
    return graphics.create_pen(0, green_value, 255)  # Cyan to blue gradient

def get_pressure_color(pressure):
    if pressure <= 980:
        return graphics.create_pen(0, 0, 255)  # Dark blue for low pressure
    elif 980 < pressure <= 1013:
        blue_value = int(255 - (pressure - 980) * (255 / 33))
        return graphics.create_pen(0, 255 - blue_value, blue_value)  # Gradient from dark blue to light blue
    elif 1013 < pressure <= 1040:
        green_value = int((pressure - 1013) * (255 / 27))
        return graphics.create_pen(0, green_value, 255 - green_value)  # Gradient from light blue to green
    else:
        return graphics.create_pen(0, 255, 0)  # Bright green for high pressure

def get_cloud_coverage_color(coverage):
    gray_value = int(255 - coverage * 2.55)
    return graphics.create_pen(gray_value, gray_value, gray_value)  # Gray gradient for cloud coverage

def get_visibility_color(visibility):
    green_value = int(visibility * 0.0255)  # Assuming max visibility of 10,000 meters for full green
    return graphics.create_pen(0, green_value, 255 - green_value)  # Blue to green gradient for visibility

def get_clock_color(hour):
    if 0 <= hour < 6:
        blue_value = int(128 + hour * (127 / 6))
        return graphics.create_pen(0, 0, blue_value)
    elif 6 <= hour < 12:
        red_value = int((hour - 6) * (255 / 6))
        green_value = int((hour - 6) * (255 / 6))
        return graphics.create_pen(red_value, green_value, 255 - red_value)
    elif 12 <= hour < 18:
        red_value = int(255 - (hour - 12) * (127 / 6))
        green_value = int(255 - (hour - 12) * (85 / 6))
        return graphics.create_pen(255, green_value, red_value)
    else:  # 18 <= hour < 24
        blue_value = int(255 - (hour - 18) * (127 / 6))
        return graphics.create_pen(255, 0, blue_value)

def get_date_color(month):
    if month in [12, 1, 2]:  # Winter
        return graphics.create_pen(0, 0, 255)
    elif month in [3, 4, 5]:  # Spring
        green_value = int(85 + (month - 3) * (85 / 3))
        return graphics.create_pen(0, green_value, 0)
    elif month in [6, 7, 8]:  # Summer
        return graphics.create_pen(255, 255, 0)
    else:  # Autumn
        red_value = int(255 - (month - 9) * (85 / 3))
        green_value = int(128 + (month - 9) * (42 / 3))
        return graphics.create_pen(red_value, green_value, 0)

def display_time():
    _, _, _, hour, minute, second, _, _ = time.localtime()
    clock = "{:02}:{:02}:{:02}".format(hour, minute, second)

    # calculate text position so that it is centred
    w = graphics.measure_text(clock, 1)
    x = int(width / 2 - w / 2 + 1)
    y = 2

    clock_color = get_clock_color(hour)
    outline_text(clock, x, y, clock_color, BLACK)

def display_date():
    # Fetch current date
    year, month, day, _, _, _, _, _ = time.localtime()
    date_str = "{:04}-{:02}-{:02}".format(year, month, day)
    
    # Calculate text position so that it is centered
    w = graphics.measure_text(date_str, 1)
    x = int(width / 2 - w / 2 + 1)
    y = 2

    date_color = get_date_color(month)
    outline_text(date_str, x, y, date_color, BLACK)

def display_weather(button):
    # Fetch weather data
    weather_data = get_weather_data()
    
    if not weather_data:
        outline_text("No Data", 11, 2)
        return

    if button == "a":
        # Display Weather Icon, Temperature, and Humidity
        icon_id = weather_data['weather'][0]['icon']
        icon_file = f"{icon_id}.jpg"
        # Assuming you have a function to display the jpeg image
        display_jpeg(icon_file, 0, 0)

        temp = round(weather_data['main']['temp'])
        humidity = weather_data['main']['humidity']
        temp_color = get_temperature_color(temp)
        outline_text(f"{temp}°F", 14, 2, temp_color, BLACK)
        humidity_color = get_humidity_color(humidity)
        outline_text(f"{humidity}%", 36, 2, humidity_color, BLACK)

    elif button == "b":
        # Display Min Temp and Max Temp
        temp_min = round(weather_data['main']['temp_min'])
        temp_max = round(weather_data['main']['temp_max'])
        # Display thermometer icons (assuming you have them as jpeg)
        #display_jpeg("cold_thermometer.jpg", 10, 10)
        #display_jpeg("hot_thermometer.jpg", 10, 50)
        outline_text(f"{temp_min}°F", 7, 2, BLUE, BLACK)
        outline_text(f"{temp_max}°F", 30, 2, RED, BLACK)
        
    elif button == "c":
        # Display Pressure and Wind Speed and Direction
        pressure = weather_data['main']['pressure']
        pressure_inHg = hpa_to_inHg(pressure)
        pressure_color = get_pressure_color(pressure)
        wind_speed = round(weather_data['wind']['speed'])
        wind_dir = weather_data['wind']['deg']
        wind_speed_color = get_wind_speed_color(wind_speed)
        #outline_text(f"{pressure}h", 2, 2, pressure_color, BLACK)
        outline_text(f"{pressure_inHg:.2f}", 2, 2, get_pressure_color(pressure))
        outline_text(f"{wind_speed}mph", 25, 2, wind_speed_color, BLACK)
        # Displaying wind direction as an arrow or text can be added here

    elif button == "d":
        # Display Cloud coverage % and visibility
        cloud_coverage = weather_data['clouds']['all']
        cloud_coverage_color = get_cloud_coverage_color(cloud_coverage)
        visibility = weather_data.get('visibility', 'N/A')  # Some data might not always be present
        visibility_color = get_visibility_color(visibility)
        #display_jpeg("cloud_icon.jpg", 10, 10)
        outline_text(f"{cloud_coverage}%", 2, 2, cloud_coverage_color, BLACK)
        outline_text(f"{visibility}m", 20, 2, visibility_color, BLACK)

    # Additional screens for rain or snow can be added similarly
    rain = weather_data.get('rain', {})
    snow = weather_data.get('snow', {})
    
    if rain:
        # Display 1h and 3h rain amount
        rain_1h = rain.get('1h', 'N/A')
        rain_3h = rain.get('3h', 'N/A')
        #display_jpeg("rain_icon.jpg", 10, 10)
        outline_text(f"1h: {rain_1h} mm", 0, 2)
        outline_text(f"3h: {rain_3h} mm", 25, 2)
    elif snow:
        # Display 1h and 3h snow amount
        snow_1h = snow.get('1h', 'N/A')
        snow_3h = snow.get('3h', 'N/A')
        #display_jpeg("snow_icon.jpg", 10, 10)
        outline_text(f"1h: {snow_1h} mm", 0, 2)
        outline_text(f"3h: {snow_3h} mm", 25, 2)
        
def display_jpeg(filename, x, y):
    j = jpegdec.JPEG(graphics)
    j.open_file(filename)
    j.decode(x, y, jpegdec.JPEG_SCALE_FULL)

def adjust_brightness(delta):
    gu.adjust_brightness(delta)

def clear_screen():
    graphics.clear()

def outline_text(text, x, y, text_color=WHITE, bg_color=BLACK):
    graphics.set_pen(bg_color)
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)

    graphics.set_pen(text_color)
    graphics.text(text, x, y, -1, 1)
    graphics.set_pen(WHITE)

# Main loop
button_actions = {
    GalacticUnicorn.SWITCH_A: "a",
    GalacticUnicorn.SWITCH_B: "b",
    GalacticUnicorn.SWITCH_C: "c",
    GalacticUnicorn.SWITCH_D: "d"
}

gu.set_brightness(0.5)

current_display = "clock"

sync_time()

while True:
    clear_screen()

    for button, action in button_actions.items():
        if gu.is_pressed(button):
            print(f"Button {action.upper()} Pressed")
            current_display = action
            last_button_press_time = time.time()

    if gu.is_pressed(GalacticUnicorn.SWITCH_SLEEP) and current_display != "date":
        print("SLEEP Button Pressed")
        current_display = "date"
        last_button_press_time = time.time()

    if current_display in button_actions.values():
        display_weather(current_display)
    elif current_display == "clock":
        display_time()
    elif current_display == "date":
        display_date()

    if last_button_press_time and (time.time() - last_button_press_time) > BUTTON_PRESS_TIMEOUT:
        current_display = "clock"

    brightness = gu.get_brightness()
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        adjust_brightness(+0.005)
        print(brightness)
    elif gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        adjust_brightness(-0.005)
        print(brightness)

    gu.update(graphics)
