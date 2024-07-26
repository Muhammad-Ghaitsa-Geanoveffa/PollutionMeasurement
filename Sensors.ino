#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>

// WiFi Connection Details
const char* ssid = "LABOR SAMSUNG";
const char* password = "hhpsamsung02";

// HiveMQ Cloud Broker settings
const char* mqtt_server = "a40113311e554f6daff3add1404152bb.s1.eu.hivemq.cloud";
const char* mqtt_username = "MuhammadGhaitsa";
const char* mqtt_password = "Polumer24";
const char* topic = "/MuhammadGhaitsa/Polumer/";
const int mqtt_port = 8883;

// HiveMQ Cloud Let's Encrypt CA certificate
static const char *root_ca PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljqoyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)EOF";

// DHT setup
#define DHTPIN 33
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// MQ135 setup
const int MQ135_PIN = 32;

// LDR setup
const int ldrPin = 35; // Pin for LDR
const int ledPin = 18; // Pin for LED

// UV sensor setup
const int SENSOR_PIN = 34;

// set the LCD number of columns and rows
int lcdColumns = 20;
int lcdRows = 4;

// set LCD address, number of columns and rows
// if you don't know your display address, run an I2C scanner sketch
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);

WiFiClientSecure espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (500)
char msg[MSG_BUFFER_SIZE];

int displayState = 0; // Initial display state

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    randomSeed(micros());

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection… ");
        String clientId = "ESP32Client";
        if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("connected");
            client.subscribe(topic);
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(9600);
    delay(500);

    // LCD setup
    lcd.init();
    lcd.backlight();

    setup_wifi();

    espClient.setCACert(root_ca);
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);

    dht.begin();
    pinMode(ledPin, OUTPUT);
}

String getAirQualityCategory(float ppmCO) {
  if (ppmCO <= 1000) {
    return "Baik";
  } else if (ppmCO <= 2000) {
    return "Buruk";
  } else if (ppmCO <= 5000) {
    return "Sangat Buruk";
  } else {
    return "Bahaya";
  }
}

String getLightIntensityCategory(int value) {
    if (value < 819) {
        return "Sangat Terang"; // Very Bright
    } else if (value < 1638) {
        return "Terang"; // Bright
    } else if (value < 2457) {
        return "Sedang"; // Moderate
    } else if (value < 3276) {
        return "Gelap"; // Dark
    } else {
        return "Sangat Gelap"; // Very Dark
    }
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();

    unsigned long currentMillis = millis();
    if (currentMillis - lastMsg >= 2000) {
        lastMsg = currentMillis;

        float suhu = dht.readTemperature();
        float kelembapan = dht.readHumidity();

        if (isnan(suhu) || isnan(kelembapan)) {
            Serial.println("Failed to read from DHT sensor!");
            return;
        }

    int sensorValue = analogRead(MQ135_PIN);
    float voltage = sensorValue * (3.3 / 4095.0);
    float ppmCO = (voltage - 0.1) * 9.23;
    float ppmCO2 = voltage * 900; // Example conversion, modify as necessary
    
    String airQuality = getAirQualityCategory(ppmCO);

        // Read LDR value
        int ldrValue = analogRead(ldrPin);

        // Get light intensity category
        String lightIntensity = getLightIntensityCategory(ldrValue);

        // Control LED based on light intensity category
        if (lightIntensity == "Gelap" || lightIntensity == "Sangat Gelap") {
            digitalWrite(ledPin, HIGH); // LED menyala
        } else {
            digitalWrite(ledPin, LOW); // LED mati
        }

        // Read UV sensor value
        float sensorVoltage;
        float uvIndex;
        sensorValue = analogRead(SENSOR_PIN);
        sensorVoltage = sensorValue;

if (sensorVoltage < 5) uvIndex = 0;
else if (sensorVoltage <= 78) uvIndex = 1;
else if (sensorVoltage <= 556) uvIndex = 2;
else if (sensorVoltage <= 833) uvIndex = 3;
else if (sensorVoltage <= 1111) uvIndex = 4;
else if (sensorVoltage <= 1389) uvIndex = 5;
else if (sensorVoltage <= 1667) uvIndex = 6;
else if (sensorVoltage <= 1944) uvIndex = 7;
else if (sensorVoltage <= 2222) uvIndex = 8;
else if (sensorVoltage <= 2500) uvIndex = 9;
else if (sensorVoltage <= 3034) uvIndex = 10;
else if (sensorVoltage <= 4095) uvIndex = 11;
else uvIndex = 0;

        // Publish data to MQTT
        snprintf(msg, MSG_BUFFER_SIZE, "Suhu: %.2f, Kelembapan: %.2f, CO2: %.2f ppm, CO: %.2f ppm, Udara: %s, Intensitas Cahaya: %d, Cahaya: %s, UV Index: %.2f",
                 suhu, kelembapan, ppmCO2, ppmCO, airQuality.c_str(), ldrValue, lightIntensity.c_str(), uvIndex);
        Serial.print("Publish message: ");
        Serial.println(msg);

        client.publish("dht11/Suhu", String(suhu).c_str());
        client.publish("dht11/Kelembapan", String(kelembapan).c_str());
        client.publish("mq135/CO2", String(ppmCO2).c_str());
        client.publish("mq135/CO", String(ppmCO).c_str());
        client.publish("mq135/Udara", airQuality.c_str());
        client.publish("ldr/IntensitasCahaya", String(ldrValue).c_str());
        client.publish("ldr/Cahaya", lightIntensity.c_str());
        client.publish("uv/Index", String(uvIndex).c_str());
        
        // Increment display state
        displayState = (displayState + 1) % 3;

        // Update LCD display based on displayState
        lcd.clear();
        switch (displayState) {
            case 0:
                lcd.setCursor(0, 0);
                lcd.print("POLLUMER SICTIM17");
                lcd.setCursor(0, 2);
                lcd.print("Suhu: ");
                lcd.print(suhu);
                lcd.print(" C");
                lcd.setCursor(0, 3);
                lcd.print("Kelembapan: ");
                lcd.print(kelembapan);
                lcd.print(" %");
                break;
            case 1:
                lcd.setCursor(0, 0);
                lcd.print("POLLUMER SICTIM17");
                lcd.setCursor(0, 1);
                lcd.print("CO2: ");
                lcd.print(ppmCO2);
                lcd.print(" ppm");
                lcd.setCursor(0, 2);
                lcd.print("CO: ");
                lcd.print(ppmCO);
                lcd.print(" ppm");
                lcd.setCursor(0, 3);
                lcd.print("Udara: ");
                lcd.print(airQuality);
                break;
            case 2:
                lcd.setCursor(0, 0);
                lcd.print("POLLUMER SICTIM17");
                lcd.setCursor(0, 2);
                lcd.print("Cahaya:");
                lcd.print(lightIntensity);
                lcd.setCursor(0, 3);
                lcd.print("UV : ");
                lcd.print(uvIndex);
                break;
            default:
                break;
        }
    }
    delay(100);
}