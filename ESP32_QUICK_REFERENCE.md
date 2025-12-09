# ESP32 Server Integration - Quick Reference

## 🚀 Quick Start

### 1. Server is Ready (on Raspberry Pi)
```bash
python main.py
# Server runs on http://0.0.0.0:5000
```

### 2. Configure ESP32 Code
Edit `ESP32_Client.ino`:
```cpp
const char* SSID = "YOUR_WIFI";
const char* PASSWORD = "YOUR_PASSWORD";
const char* SERVER_IP = "192.168.X.X";     // Raspberry Pi IP
const String DEVICE_ID = "ESP32_001";
```

### 3. Upload to ESP32 & Run
- Install ArduinoJson library
- Upload `ESP32_Client.ino` to ESP32
- Check Serial Monitor (115200 baud)

---

## 📡 API Endpoints at a Glance

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/esp32/register` | Register new device |
| POST | `/api/esp32/unregister/{id}` | Unregister device |
| GET | `/api/esp32/status/{id}` | Get device status |
| PUT | `/api/esp32/status/{id}` | Update device status |
| GET | `/api/esp32/devices` | List all devices |
| GET | `/api/esp32/commands/{id}` | Poll for commands |
| POST | `/api/esp32/commands/{id}` | Send command to device |
| POST | `/api/esp32/telemetry/{id}` | Send telemetry data |
| GET | `/api/esp32/telemetry/{id}` | Get telemetry history |
| GET | `/api/esp32/health` | Server health check |

---

## 🔧 Common Tasks

### Check Server Status
```bash
curl http://192.168.X.X:5000/api/esp32/health
```

### List Connected Devices
```bash
curl http://192.168.X.X:5000/api/esp32/devices
```

### Manually Register Device
```bash
curl -X POST http://192.168.X.X:5000/api/esp32/register \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32_001","firmware_version":"1.0.0"}'
```

### Send Movement Command
```bash
curl -X POST http://192.168.X.X:5000/api/esp32/commands/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"command":"MOVE","params":{"destination":"AREA_10","speed":0.5}}'
```

### Get Device Status
```bash
curl http://192.168.X.X:5000/api/esp32/status/ESP32_001
```

### Send Telemetry
```bash
curl -X POST http://192.168.X.X:5000/api/esp32/telemetry/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"battery":85,"temperature":28.3,"position":{"x":10,"y":20}}'
```

---

## 🔄 ESP32 Lifecycle

```
┌─────────────────────────────────────────┐
│         ESP32 Boot Sequence             │
├─────────────────────────────────────────┤
│                                         │
│  1. Power On / Reset                    │
│     ↓                                   │
│  2. Connect to WiFi                     │
│     ↓                                   │
│  3. POST /register                      │
│     └─> Server registers device         │
│     ↓                                   │
│  4. Start polling loop:                 │
│     ├─ Every 5s:  GET /commands         │
│     ├─ Every 10s: POST /telemetry       │
│     └─ Every 30s: PUT /status (heartbeat)│
│     ↓                                   │
│  5. Process commands as received        │
│     ├─ MOVE: Move to destination        │
│     ├─ STOP: Stop movement              │
│     ├─ RETURN: Return to start          │
│     └─ EMERGENCY_STOP: Emergency        │
│     ↓                                   │
│  6. Report telemetry continuously       │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📊 Command Types

### MOVE
Move to a destination at specified speed
```json
{
  "command": "MOVE",
  "params": {
    "destination": "AREA_10",
    "speed": 0.5
  }
}
```

### STOP
Stop immediately
```json
{
  "command": "STOP"
}
```

### RETURN
Return to starting position
```json
{
  "command": "RETURN"
}
```

### EMERGENCY_STOP
Stop all operations immediately
```json
{
  "command": "EMERGENCY_STOP"
}
```

---

## 📈 Telemetry Fields

```json
{
  "battery": 85.5,              // Battery percentage (0-100)
  "temperature": 28.3,          // Temperature in Celsius
  "signal_strength": -60,       // WiFi signal dBm
  "position": {                 // Current position
    "x": 15,
    "y": 20
  },
  "status": "MOVING"            // Current status
}
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
python test_esp32_api.py
```

### Test Specific Endpoint
```bash
python test_esp32_api.py health
python test_esp32_api.py register
python test_esp32_api.py devices
python test_esp32_api.py status
python test_esp32_api.py command
python test_esp32_api.py telemetry
```

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Device won't connect to WiFi | Check SSID/password, ensure 2.4GHz band |
| Connection timeout | Verify SERVER_IP is correct, check firewall |
| Device not registering | Start Flask server, check port 5000 is open |
| Commands not received | Check device is registered, verify device_id matches |
| Can't reach from ESP32 but can from PC | Device on different WiFi or network, check IP range |

---

## 📝 Files Created

| File | Purpose |
|------|---------|
| `website/esp32_connection.py` | Device management logic |
| `website/esp32_routes.py` | REST API endpoints |
| `ESP32_Client.ino` | Arduino code for ESP32 |
| `ESP32_INTEGRATION_GUIDE.md` | Detailed setup guide |
| `test_esp32_api.py` | API testing script |
| `ESP32_QUICK_REFERENCE.md` | This file |

---

## 🔌 Network Configuration

### Typical Setup
```
┌─────────────────────┐
│   Your WiFi Network │
├─────────────────────┤
│                     │
│  ESP32              │
│  192.168.1.100      │
│                     │
│  Raspberry Pi       │
│  192.168.1.50       │
│  (Flask 0.0.0.0:5000)
│                     │
│  PC/Laptop          │
│  192.168.1.X        │
│  (Dashboard)        │
│                     │
└─────────────────────┘
```

### Configuration Steps
1. Note Raspberry Pi IP: `hostname -I`
2. Put in `SERVER_IP` in ESP32 code
3. Ensure ESP32 and Pi on same WiFi network
4. Test with: `ping 192.168.1.X` from PC

---

## 📦 Required Libraries (ESP32)

**Arduino IDE:**
1. `Sketch > Include Library > Manage Libraries`
2. Search: "ArduinoJson"
3. Install by Benoit Blanchon (latest version)
4. Board: ESP32 Dev Module (or your model)

**Python Server:**
- Flask (already installed with repo)
- requests (for testing)

---

## 🎯 Integration with Dashboard

When user sends package on web dashboard:
1. Route calculated
2. Instructions generated
3. Sent to:
   - ✓ Database (dashboard history)
   - ✓ MQTT Broker (other subscribers)
   - ✓ **ESP32 command queue (NEW!)**

ESP32 receives via: `GET /api/esp32/commands/{device_id}`

---

## 💡 Tips

- **Polling vs Push:** ESP32 polls commands (pull model). Commands queued on server until device fetches them.
- **Reliability:** Uses HTTP (reliable, TCP-based) unlike MQTT (unreliable, UDP-based)
- **Scalability:** Multiple ESP32 devices register with unique device_id
- **Debugging:** Always check Serial Monitor at 115200 baud
- **Status:** Device status tracks in memory (resets on server restart)

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Status:** Ready for deployment
