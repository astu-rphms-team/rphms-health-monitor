/*
  RPHMS - Stage 2: DS18B20 temperature sensor test
  ==================================================
  Purpose: confirm your DS18B20 is wired correctly and reads sensible
  temperatures BEFORE combining it with anything else.

  WIRING (DS18B20 has 3 wires: usually Red, Black, Yellow):
    Red    -> ESP32 3.3V
    Black  -> ESP32 GND
    Yellow -> ESP32 GPIO4  (data line)
    Also connect a 4.7k ohm resistor between the Yellow (data) wire and
    the Red (3.3V) wire - this is the required pull-up resistor.

  LIBRARIES NEEDED (install via Arduino IDE: Sketch > Include Library >
  Manage Libraries, search and install both):
    - "OneWire" by Jim Studt / Paul Stoffregen
    - "DallasTemperature" by Miles Burton
*/

#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_PIN 4

OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature tempSensor(&oneWire);

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("RPHMS Stage 2: DS18B20 test starting...");

  tempSensor.begin();

  int deviceCount = tempSensor.getDeviceCount();
  Serial.print("DS18B20 sensors found: ");
  Serial.println(deviceCount);

  if (deviceCount == 0) {
    Serial.println("No sensor detected! Check wiring and the 4.7k pull-up resistor.");
  }
}

void loop() {
  tempSensor.requestTemperatures();
  float tempC = tempSensor.getTempCByIndex(0);

  if (tempC == DEVICE_DISCONNECTED_C) {
    Serial.println("Error: could not read temperature. Check wiring.");
  } else {
    Serial.print("Temperature: ");
    Serial.print(tempC);
    Serial.println(" °C");
  }

  delay(2000);
}
