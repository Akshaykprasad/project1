#include <Wire.h>
#include <SPI.h>
#include <MPU9250_asukiaaa.h>
#include <MadgwickAHRS.h>
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "hope";
const char* password = "12345678";

MPU9250_asukiaaa mpu;
Madgwick filter;
WebServer server(80);

void handleSensorData() {
    mpu.accelUpdate();
    mpu.gyroUpdate();
    mpu.magUpdate();

    float ax = mpu.accelX();
    float ay = mpu.accelY();
    float az = mpu.accelZ();
    float gx = mpu.gyroX();
    float gy = mpu.gyroY();
    float gz = mpu.gyroZ();
    float mx = mpu.magX();
    float my = mpu.magY();
    float mz = mpu.magZ();

    filter.updateIMU(gx, gy, gz, ax, ay, az);

    String json = "{\"ax\":" + String(ax) + ", \"ay\":" + String(ay) + ", \"az\":" + String(az) +
                  ", \"gx\":" + String(gx) + ", \"gy\":" + String(gy) + ", \"gz\":" + String(gz) +
                  ", \"mx\":" + String(mx) + ", \"my\":" + String(my) + ", \"mz\":" + String(mz) + "}";

    server.sendHeader("Access-Control-Allow-Origin", "*");  // ✅ Allow all origins
    server.sendHeader("Access-Control-Allow-Methods", "GET");
    server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
    server.send(200, "application/json", json);
}

void setup() {
    Serial.begin(115200);
    Wire.begin();

    Serial.println("Initializing MPU9250...");
    mpu.setWire(&Wire);

    mpu.beginAccel();
    mpu.beginGyro();
    mpu.beginMag();

    delay(1000);

    mpu.accelUpdate();
    mpu.gyroUpdate();
    mpu.magUpdate();

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }
    Serial.println("\nConnected to WiFi!");
    Serial.println(WiFi.localIP());

    server.on("/sensor", handleSensorData);
    
    // ✅ Handle CORS Preflight Request
    server.on("/sensor", HTTP_OPTIONS, []() {
        server.sendHeader("Access-Control-Allow-Origin", "*");
        server.sendHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
        server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
        server.send(204);  // No content response
    });

    server.begin();
}


void loop() {
    server.handleClient();
}
