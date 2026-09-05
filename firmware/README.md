# RPHMS Firmware (ESP32)

This folder has 4 sketches. Upload and test them **in this order** — each
one proves one part works before you combine everything. Don't skip to
the final firmware first; if something's wired wrong, you want to know
that on the simple sketch, not the complicated one.

```
firmware/
├── stage1_wifi_test/        <- upload this first
├── stage2_ds18b20_test/     <- then this
├── stage3_max30102_test/    <- then this
└── rphms_firmware/          <- finally, the real combined firmware
```

## 1. Install Arduino IDE + ESP32 board support

1. Download Arduino IDE (2.x) from arduino.cc if you don't have it.
2. File → Preferences → "Additional Boards Manager URLs" → paste:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Tools → Board → Boards Manager → search "esp32" → install the one by
   **Espressif Systems**.
4. Tools → Board → select **ESP32 Dev Module** (or your exact board name).
5. Plug in your ESP32 via USB → Tools → Port → select the COM port that
   appears (Windows) or `/dev/cu.usbserial-...` (Mac).

## 2. Install libraries

Sketch → Include Library → Manage Libraries, then search and install each:

| Library | Author | Needed for |
|---|---|---|
| OneWire | Jim Studt / Paul Stoffregen | DS18B20 |
| DallasTemperature | Miles Burton | DS18B20 |
| SparkFun MAX3010x Pulse and Proximity Sensor Library | SparkFun | MAX30102 |
| ArduinoJson | Benoit Blanchon | Building the JSON payload (final firmware only) |

`WiFi.h` and `HTTPClient.h` are built into the ESP32 board package — no
separate install needed.

## 3. Wiring

**DS18B20** (3-wire probe):
| DS18B20 wire | ESP32 pin |
|---|---|
| Red (VCC) | 3.3V |
| Black (GND) | GND |
| Yellow (Data) | GPIO4 |

Also connect a **4.7kΩ resistor** between the Yellow wire and 3.3V (the
required pull-up resistor for 1-Wire communication).

**MAX30102** (I2C):
| MAX30102 pin | ESP32 pin |
|---|---|
| VIN | 3.3V |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |

## 4. Stage 1 — Wi-Fi test

Open `stage1_wifi_test/stage1_wifi_test.ino`. Edit `WIFI_SSID` and
`WIFI_PASSWORD` at the top. Upload it (the arrow button), then open
**Tools → Serial Monitor**, set baud rate to **115200**.

You should see your ESP32's IP address printed. If not, see the
troubleshooting notes printed in the Serial Monitor output.

> ESP32 only supports 2.4GHz Wi-Fi networks, not 5GHz. If your router
> broadcasts both, make sure you're connecting to the 2.4GHz one.

## 5. Stage 2 — DS18B20 test

Wire up the DS18B20 as described above. Open
`stage2_ds18b20_test/stage2_ds18b20_test.ino`, upload it, open Serial
Monitor. You should see a temperature printed every 2 seconds
(room temperature, ~20-25°C, if you're not touching the probe).

## 6. Stage 3 — MAX30102 test

Wire up the MAX30102 as described above (you can leave the DS18B20
connected too — they use different pins). Open
`stage3_max30102_test/stage3_max30102_test.ino`, upload it, open Serial
Monitor.

Place your fingertip gently on the sensor, covering the LED window, and
hold still. After a few seconds you should see heart rate and SpO2
values printed.

## 7. Final firmware

Once all 3 stages work independently, open
`rphms_firmware/rphms_firmware.ino`. Edit the top section:

```cpp
const char* WIFI_SSID = "...";
const char* WIFI_PASSWORD = "...";
const char* SERVER_URL = "http://YOUR_SERVER_IP:8000";
const char* DEVICE_ID = "ESP32_001";
```

See the main `README.md` → **"Connecting a real device"** section for how
to find the right `SERVER_URL`.

**Important:** the patient with `device_id = "ESP32_001"` (or whatever you
set) must already be registered in the RPHMS dashboard before the ESP32
sends its first reading, or the backend will reject it with a 404.

Upload, open Serial Monitor, place your finger on the MAX30102, and watch
readings get sent every 10 seconds. Then open the dashboard in your
browser and confirm the patient's row updates live.
