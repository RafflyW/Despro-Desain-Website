# ESP32 Server Integration Guide

## Overview
This guide explains how to integrate your ESP32 microcontroller with the Raspberry Pi Flask server for remote control and telemetry.

## Architecture

```
ESP32 Device
    ↓ (WiFi HTTP Requests)
    ↓
Raspberry Pi Server (Flask)
    ↓ (Web Interface)
    ↓
Dashboard Website
```

## Setup Steps

### 1. Raspberry Pi Server Setup (Already Done)

The server is running on Raspberry Pi with Flask on port 5000.

**Available API Endpoints:**
```
/api/esp32/register           - POST   - Register new ESP32
/api/esp32/unregister/{id}    - POST   - Unregister ESP32
/api/esp32/status/{id}        - GET    - Get device status
/api/esp32/status/{id}        - PUT    - Update device status
/api/esp32/devices            - GET    - List all devices
/api/esp32/commands/{id}      - GET    - Poll for commands
/api/esp32/commands/{id}      - POST   - Send command to ESP32
/api/esp32/telemetry/{id}     - GET    - Get telemetry data
/api/esp32/telemetry/{id}     - POST   - Send telemetry data
/api/esp32/health             - GET    - Health check
```

### 2. ESP32 Arduino Code Setup

#### Prerequisites
- Arduino IDE installed
- ESP32 board support installed in Arduino IDE
- Required Library: **ArduinoJson**

#### Install ArduinoJson Library
1. Open Arduino IDE
2. Go to `Sketch > Include Library > Manage Libraries`
3. Search for "ArduinoJson"
4. Install by Benoit Blanchon (latest version)

#### Configure ESP32_Client.ino

Edit these lines in `ESP32_Client.ino`:

```cpp
// WiFi Configuration
const char* SSID = "YOUR_SSID";              // Your WiFi network name
const char* PASSWORD = "YOUR_PASSWORD";      // Your WiFi password

// Server Configuration
const char* SERVER_IP = "192.168.1.X";       // Raspberry Pi IP address
const int SERVER_PORT = 5000;                // Flask server port
const String DEVICE_ID = "ESP32_001";        // Unique device ID
```

#### Upload to ESP32

1. Connect ESP32 to computer via USB
2. In Arduino IDE:
   - Go to `Tools > Board` and select "ESP32 Dev Module" (or your board model)
   - Go to `Tools > Port` and select the COM port
3. Click Upload button (→)
4. Wait for upload to complete

### 3. Device Registration

When ESP32 boots up:
1. Connects to WiFi
2. Automatically registers with server (calls `/api/esp32/register`)
3. Starts polling for commands every 5 seconds
4. Sends telemetry every 10 seconds
5. Sends heartbeat every 30 seconds

## How It Works

### Device Lifecycle

#### Startup
```
ESP32 Power On
  ↓
Connect to WiFi
  ↓
POST /api/esp32/register (device_id, firmware_version, mac_address)
  ↓
Server registers device in memory
  ↓
Start polling for commands and reporting telemetry
```

#### During Operation
```
Every 5 seconds:  GET /api/esp32/commands/{device_id}
Every 10 seconds: POST /api/esp32/telemetry/{device_id} (battery, position, etc)
Every 30 seconds: PUT /api/esp32/status/{device_id} (heartbeat)
```

#### Receiving Commands
```
1. ESP32 polls: GET /api/esp32/commands/ESP32_001
2. Server returns pending commands (if any)
3. ESP32 processes each command (MOVE, STOP, RETURN, etc)
4. Server clears processed commands
```

#### Sending Commands from Dashboard
```
1. User selects destination on web dashboard
2. Dashboard calls route calculation
3. Generated instructions sent to:
   a. Database (via mqtt_connection.py)
   b. MQTT broker (for other subscribers)
   c. Now ALSO queued for ESP32 via esp32_connection.py
4. ESP32 polls commands and receives route instructions
5. ESP32 executes movement commands
6. ESP32 reports position updates via telemetry
```

## API Endpoint Details

### Register Device
```
POST /api/esp32/register
Content-Type: application/json

Request Body:
{
  "device_id": "ESP32_001",
  "firmware_version": "1.0.0",
  "mac_address": "AA:BB:CC:DD:EE:FF"
}

Response (200):
{
  "success": true,
  "message": "Device ESP32_001 berhasil terdaftar",
  "device_id": "ESP32_001"
}
```

### Update Device Status
```
PUT /api/esp32/status/{device_id}
Content-Type: application/json

Request Body:
{
  "status": "MOVING",
  "data": {
    "current_position": {"x": 10, "y": 20},
    "speed": 0.5,
    "battery": 85
  }
}

Response (200):
{
  "success": true,
  "message": "Status updated ke MOVING",
  "device_id": "ESP32_001"
}
```

### Poll Commands
```
GET /api/esp32/commands/{device_id}

Response (200):
{
  "device_id": "ESP32_001",
  "commands": [
    {
      "command": "MOVE",
      "params": {
        "destination": "AREA_10",
        "speed": 0.5
      },
      "timestamp": "2025-12-09T10:30:00"
    }
  ],
  "count": 1
}
```

### Send Command to ESP32
```
POST /api/esp32/commands/{device_id}
Content-Type: application/json

Request Body:
{
  "command": "MOVE",
  "params": {
    "destination": "AREA_12",
    "speed": 0.75
  }
}

Response (200):
{
  "success": true,
  "message": "Command \"MOVE\" queued untuk device ESP32_001",
  "device_id": "ESP32_001",
  "command": "MOVE"
}
```

### Send Telemetry
```
POST /api/esp32/telemetry/{device_id}
Content-Type: application/json

Request Body:
{
  "battery": 85.5,
  "temperature": 28.3,
  "position": {"x": 15, "y": 20},
  "signal_strength": -60,
  "status": "MOVING"
}

Response (200):
{
  "success": true,
  "message": "Telemetry recorded",
  "device_id": "ESP32_001"
}
```

### Get Telemetry History
```
GET /api/esp32/telemetry/{device_id}

Response (200):
{
  "device_id": "ESP32_001",
  "latest": {
    "battery": 85.5,
    "temperature": 28.3,
    "position": {"x": 15, "y": 20},
    "timestamp": "2025-12-09T10:30:00"
  },
  "history": [
    {...last 100 telemetry entries...}
  ]
}
```

### Get All Devices
```
GET /api/esp32/devices

Response (200):
{
  "devices": [
    {
      "device_id": "ESP32_001",
      "status": "MOVING",
      "connected_at": "2025-12-09T10:00:00",
      "last_seen": "2025-12-09T10:30:00",
      "ip_address": "192.168.1.100",
      "firmware_version": "1.0.0",
      "battery": 85
    }
  ],
  "count": 1
}
```

## Testing Connection

### Test from Command Line

1. **Check if server is running:**
```bash
curl http://{RASPBERRY_PI_IP}:5000/api/esp32/health
```

2. **List connected devices:**
```bash
curl http://{RASPBERRY_PI_IP}:5000/api/esp32/devices
```

3. **Manually register a test device:**
```bash
curl -X POST http://{RASPBERRY_PI_IP}:5000/api/esp32/register \
  -H "Content-Type: application/json" \
  -d '{"device_id":"TEST_001","firmware_version":"1.0.0"}'
```

4. **Send command to device:**
```bash
curl -X POST http://{RASPBERRY_PI_IP}:5000/api/esp32/commands/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"command":"MOVE","params":{"destination":"AREA_10","speed":0.5}}'
```

### Monitor ESP32 Serial Output

When ESP32 is connected:
1. Open Arduino IDE
2. Go to `Tools > Serial Monitor`
3. Set baud rate to 115200
4. Watch for connection and command messages

Expected output:
```
Starting WiFi connection...
WiFi connected!
IP address: 192.168.1.100
[✓] Device registered successfully
[✓] Heartbeat sent. Status: IDLE
[✓] Telemetry sent
[✓] Received 1 command(s)
Processing command: MOVE
Moving to: AREA_10 at speed: 0.5
```

## Integration with Existing System

### Sending Instructions from Dashboard

The route_instructions are now automatically sent to ESP32:

1. User selects destination on web dashboard
2. Server calculates route and generates instructions
3. Instructions are sent to:
   - **MQTT Broker** (existing integration)
   - **ESP32 Devices** (new - via command queue)
   - **Database** (existing)

4. ESP32 receives via: `GET /api/esp32/commands/ESP32_001`

### Modified Files

- `website/__init__.py` - Added ESP32 blueprint registration
- `website/esp32_connection.py` - Device management and tracking
- `website/esp32_routes.py` - REST API endpoints
- `website/views.py` - Already integrated MQTT, can add ESP32 integration

## Troubleshooting

### ESP32 Won't Connect to WiFi
- Check SSID and password are correct
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Check WiFi password has no special characters

### Device not registering
- Ensure Raspberry Pi server is running: `python main.py`
- Check firewall allows port 5000
- Verify SERVER_IP is correct (use Raspberry Pi's actual IP)
- Check ESP32 can ping Raspberry Pi: `ping {SERVER_IP}`

### Commands not received
- Check device registered: `curl http://{SERVER_IP}:5000/api/esp32/devices`
- Send test command: `curl -X POST ... /api/esp32/commands/ESP32_001`
- Watch Serial Monitor for polling messages

### Telemetry not received
- Check telemetry interval is reasonable (not too frequent)
- Verify HTTP POST requests are working
- Check server logs for errors

## Future Enhancements

1. **Persistence** - Save device state and commands to database
2. **Authentication** - Add API key/token authentication
3. **Over-the-Air Updates** - Send firmware updates via API
4. **Advanced Routing** - Dynamic route optimization
5. **Real-time Dashboard** - WebSocket updates for live device tracking
6. **Error Recovery** - Automatic retry and reconnection logic

## Support

For issues or questions, check:
1. Serial Monitor output from ESP32
2. Server logs on Raspberry Pi
3. API responses via curl/Postman
4. WiFi connectivity

---

**Last Updated:** December 2025
**System:** Raspberry Pi Flask Server + ESP32 Microcontroller
