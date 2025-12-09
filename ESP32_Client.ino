/*
 * ESP32 Server Communication Library
 * For connecting ESP32 to Raspberry Pi Server (Flask)
 * 
 * Features:
 * - Device registration/unregistration
 * - Command polling from server
 * - Telemetry reporting
 * - Status updates
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION ====================

// WiFi Configuration
const char* SSID = "YOUR_SSID";
const char* PASSWORD = "YOUR_PASSWORD";

// Server Configuration
const char* SERVER_IP = "192.168.1.X";      // Raspberry Pi IP Address
const int SERVER_PORT = 5000;               // Flask server port (default 5000)
const String DEVICE_ID = "ESP32_001";       // Unique device ID

// Endpoints
String REGISTER_URL;
String UNREGISTER_URL;
String STATUS_URL;
String COMMANDS_URL;
String TELEMETRY_URL;

// Timing Configuration (in milliseconds)
const unsigned long HEARTBEAT_INTERVAL = 30000;    // Send heartbeat every 30s
const unsigned long COMMAND_POLL_INTERVAL = 5000;  // Poll commands every 5s
const unsigned long TELEMETRY_INTERVAL = 10000;    // Send telemetry every 10s

// ==================== GLOBAL VARIABLES ====================

unsigned long lastHeartbeat = 0;
unsigned long lastCommandPoll = 0;
unsigned long lastTelemetry = 0;

// Device status variables
String currentStatus = "IDLE";
int battery = 100;
float temperature = 25.0;
float posX = 0, posY = 0;
int signalStrength = -50;

// ==================== SETUP FUNCTIONS ====================

void setupWiFi() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\nStarting WiFi connection...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.println("IP address: " + WiFi.localIP().toString());
  } else {
    Serial.println("\nFailed to connect to WiFi!");
  }
}

void setupServerURLs() {
  String baseURL = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/esp32";
  
  REGISTER_URL = baseURL + "/register";
  UNREGISTER_URL = baseURL + "/unregister/" + DEVICE_ID;
  STATUS_URL = baseURL + "/status/" + DEVICE_ID;
  COMMANDS_URL = baseURL + "/commands/" + DEVICE_ID;
  TELEMETRY_URL = baseURL + "/telemetry/" + DEVICE_ID;
  
  Serial.println("Server URLs configured:");
  Serial.println("Base URL: " + baseURL);
}

// ==================== REGISTRATION & HEARTBEAT ====================

void registerDevice() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[ERROR] WiFi not connected");
    return;
  }
  
  HTTPClient http;
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["firmware_version"] = "1.0.0";
  doc["mac_address"] = WiFi.macAddress();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Send POST request
  http.begin(REGISTER_URL);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.POST(jsonData);
  
  if (httpCode == 200) {
    Serial.println("[✓] Device registered successfully");
    Serial.println("Response: " + http.getString());
  } else {
    Serial.println("[✗] Registration failed. HTTP Code: " + String(httpCode));
    Serial.println("Response: " + http.getString());
  }
  
  http.end();
}

void unregisterDevice() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[ERROR] WiFi not connected");
    return;
  }
  
  HTTPClient http;
  http.begin(UNREGISTER_URL);
  
  int httpCode = http.POST("");
  
  if (httpCode == 200) {
    Serial.println("[✓] Device unregistered successfully");
  } else {
    Serial.println("[✗] Unregistration failed. HTTP Code: " + String(httpCode));
  }
  
  http.end();
}

void sendHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  
  // Create JSON payload for status update
  StaticJsonDocument<200> doc;
  doc["status"] = currentStatus;
  
  JsonObject data = doc.createNestedObject("data");
  data["battery"] = battery;
  data["signal_strength"] = WiFi.RSSI();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Send PUT request
  http.begin(STATUS_URL);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.PUT(jsonData);
  
  if (httpCode == 200) {
    Serial.println("[✓] Heartbeat sent. Status: " + currentStatus);
  } else {
    Serial.println("[✗] Heartbeat failed. HTTP Code: " + String(httpCode));
  }
  
  http.end();
}

// ==================== COMMAND POLLING ====================

void pollCommands() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  http.begin(COMMANDS_URL);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    
    // Parse JSON response
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (error) {
      Serial.println("[✗] JSON parse error: " + String(error.c_str()));
      http.end();
      return;
    }
    
    JsonArray commands = doc["commands"];
    int count = doc["count"];
    
    if (count > 0) {
      Serial.println("[✓] Received " + String(count) + " command(s)");
      
      for (JsonObject cmd : commands) {
        processCommand(cmd);
      }
    }
  } else {
    Serial.println("[!] Command poll - HTTP Code: " + String(httpCode));
  }
  
  http.end();
}

void processCommand(JsonObject command) {
  String cmd = command["command"];
  JsonObject params = command["params"];
  
  Serial.println("Processing command: " + cmd);
  
  // Add your command handlers here
  if (cmd == "MOVE") {
    String destination = params["destination"];
    float speed = params["speed"];
    handleMoveCommand(destination, speed);
  } 
  else if (cmd == "STOP") {
    handleStopCommand();
  } 
  else if (cmd == "RETURN") {
    handleReturnCommand();
  } 
  else if (cmd == "EMERGENCY_STOP") {
    handleEmergencyStop();
  }
  else {
    Serial.println("[?] Unknown command: " + cmd);
  }
}

// ==================== TELEMETRY REPORTING ====================

void sendTelemetry() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  
  // Create JSON payload with telemetry
  StaticJsonDocument<300> doc;
  doc["battery"] = battery;
  doc["temperature"] = temperature;
  doc["signal_strength"] = WiFi.RSSI();
  
  JsonObject position = doc.createNestedObject("position");
  position["x"] = posX;
  position["y"] = posY;
  
  doc["status"] = currentStatus;
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Send POST request
  http.begin(TELEMETRY_URL);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.POST(jsonData);
  
  if (httpCode == 200) {
    Serial.println("[✓] Telemetry sent");
  } else {
    Serial.println("[✗] Telemetry failed. HTTP Code: " + String(httpCode));
  }
  
  http.end();
}

// ==================== COMMAND HANDLERS ====================
// Add your actual robot control logic here

void handleMoveCommand(String destination, float speed) {
  Serial.println("Moving to: " + destination + " at speed: " + String(speed));
  currentStatus = "MOVING";
  // TODO: Implement actual motor control
}

void handleStopCommand() {
  Serial.println("Stopping...");
  currentStatus = "STOPPED";
  // TODO: Stop motors
}

void handleReturnCommand() {
  Serial.println("Returning to start...");
  currentStatus = "RETURNING";
  // TODO: Implement return to start logic
}

void handleEmergencyStop() {
  Serial.println("[EMERGENCY] STOP!");
  currentStatus = "EMERGENCY_STOP";
  // TODO: Implement emergency stop
}

// ==================== SENSOR/STATUS UPDATE FUNCTIONS ====================
// Call these to update device state

void updateBattery(int percentage) {
  battery = constrain(percentage, 0, 100);
}

void updateTemperature(float temp) {
  temperature = temp;
}

void updatePosition(float x, float y) {
  posX = x;
  posY = y;
}

void updateStatus(String newStatus) {
  currentStatus = newStatus;
}

// ==================== MAIN SETUP & LOOP ====================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========== ESP32 Server Client ==========");
  
  setupWiFi();
  setupServerURLs();
  
  // Register device on startup
  delay(1000);
  registerDevice();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Send heartbeat periodically
  if (currentTime - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    lastHeartbeat = currentTime;
    sendHeartbeat();
  }
  
  // Poll for commands periodically
  if (currentTime - lastCommandPoll >= COMMAND_POLL_INTERVAL) {
    lastCommandPoll = currentTime;
    pollCommands();
  }
  
  // Send telemetry periodically
  if (currentTime - lastTelemetry >= TELEMETRY_INTERVAL) {
    lastTelemetry = currentTime;
    sendTelemetry();
  }
  
  // Add your other code here
  delay(100);
}

/* ==================== API QUICK REFERENCE ====================

1. REGISTER DEVICE
   POST /api/esp32/register
   Body: {"device_id": "ESP32_001", "firmware_version": "1.0.0"}
   
2. GET STATUS
   GET /api/esp32/status/{device_id}
   
3. UPDATE STATUS
   PUT /api/esp32/status/{device_id}
   Body: {"status": "MOVING", "data": {...}}
   
4. POLL COMMANDS
   GET /api/esp32/commands/{device_id}
   Returns: List of pending commands to execute
   
5. SEND COMMAND TO ESP32
   POST /api/esp32/commands/{device_id}
   Body: {"command": "MOVE", "params": {"destination": "AREA_10"}}
   
6. SEND TELEMETRY
   POST /api/esp32/telemetry/{device_id}
   Body: {"battery": 85, "temperature": 28.3, "position": {"x": 10, "y": 20}}
   
7. GET ALL DEVICES
   GET /api/esp32/devices
   
====== REQUIRED LIBRARIES ======
   - WiFi (built-in)
   - HTTPClient (built-in)
   - ArduinoJson (https://github.com/bblanchon/ArduinoJson)
     Installation: Sketch > Include Library > Manage Libraries
     Search: ArduinoJson by Benoit Blanchon
     
====== LIBRARY INSTALLATION ======
   Sketch > Include Library > Manage Libraries
   Search "ArduinoJson" > Install (latest version)

*/
