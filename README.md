# Galactic Unicorn Advanced Weather Clock

An advanced weather clock built for the Pimoroni Galactic Unicorn display.

![Galactic Unicorn Display](link-to-image-of-your-clock-if-you-have-one.jpg)

## Features

- Displays current time with a gradient based on the time of day.
- Shows the date with a gradient based on the season.
- Fetches and displays live weather data:
  - Current temperature with a color gradient based on comfort levels.
  - Humidity with a gradient indicating moisture level.
  - Wind speed in mph with a gradient indicating wind strength.
  - Atmospheric pressure in inHg.
  - Cloud coverage percentage.
  - Visibility in meters.
- Button controls to toggle between time, date, and various weather metrics.
- Adjusts display brightness.

## Setup

1. Clone this repository
2. Navigate to the project directory
3. Update the `WIFI_SSID`, `WIFI_PASSWORD`, and `OPEN_WEATHER_MAP_API_KEY` constants in the main script with your credentials.
4. Deploy the script and icons to your Pimoroni Galactic Unicorn display.
5. Power on the display and enjoy your advanced weather clock!
6. Press buttons A/B/C/D/Zzz to switch between screens

## Buttons

A = Temperature and Humidity
B = Low and High Temperatures
C = Pressure and Wind Speed
D = Cloud Coverage and Visibility
Zzz = Date
Lux -/+ = Change Brightness


## Dependencies

- `galactic`: Library for the Pimoroni Galactic Unicorn display.
- `picographics`: Graphics library for displays.
- `network`: For connecting to Wi-Fi.
- `ntptime`: For syncing time.
- `urequests`: For making API requests.
- `jpegdec`: For decoding and displaying JPEG images.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

[MIT License](LICENSE)

## Acknowledgements

Thanks to Pimoroni for the Galactic Unicorn display and the community for their support and contributions.
