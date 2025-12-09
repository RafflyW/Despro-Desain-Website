# ESP32 Integration - Setup Checklist

Use this checklist to complete the ESP32 setup step-by-step.

---

## 📋 Pre-Setup (Before You Start)

- [ ] Raspberry Pi is powered on and connected to WiFi
- [ ] Flask server can be started: `python main.py`
- [ ] ESP32 microcontroller board available
- [ ] USB cable for ESP32 programming
- [ ] Computer with Arduino IDE installed
- [ ] Know your WiFi SSID and password
- [ ] Know your Raspberry Pi IP address (from `hostname -I`)

---

## 📚 Documentation Review

Read these files in order (10-15 minutes):

- [ ] `ESP32_IMPLEMENTATION_SUMMARY.md` - Overview of what's been done
- [ ] `ESP32_QUICK_REFERENCE.md` - Quick reference guide
- [ ] `ESP32_NETWORK_SETUP.md` - Network configuration help
- [ ] `ESP32_INTEGRATION_GUIDE.md` - Detailed setup guide

---

## 🔧 Arduino IDE Setup (5-10 minutes)

### Install ESP32 Board Support
- [ ] Open Arduino IDE
- [ ] Go to File > Preferences
- [ ] Add to "Additional Boards Manager URLs":
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
- [ ] Click OK
- [ ] Go to Tools > Board > Boards Manager
- [ ] Search "ESP32"
- [ ] Install "ESP32 by Espressif Systems" (latest version)
- [ ] Close Boards Manager

### Install ArduinoJson Library
- [ ] Go to Sketch > Include Library > Manage Libraries
- [ ] Search "ArduinoJson"
- [ ] Install "ArduinoJson by Benoit Blanchon" (latest version)
- [ ] Close Library Manager

### Verify Installation
- [ ] Go to Tools > Board
- [ ] Should see "ESP32 Dev Module" (or your board model)
- [ ] Select it if not already selected
- [ ] Verify no errors in console

---

## 🌐 Network Configuration (5 minutes)

### Find Your Raspberry Pi IP
- [ ] SSH into Raspberry Pi or open terminal
- [ ] Run: `hostname -I`
- [ ] Note down the IP address (e.g., `192.168.1.50`)
- [ ] Write it here: `________________________`

### Find Your WiFi Info
- [ ] WiFi SSID (network name): `________________________`
- [ ] WiFi Password: `________________________`
- [ ] Verify WiFi is 2.4GHz (check router settings if unsure)

### Verify Server Connectivity
- [ ] Open terminal/PowerShell on your PC
- [ ] Run: `ping 192.168.1.X` (use your Pi IP)
- [ ] Should see "Reply from..." messages
- [ ] If not, check WiFi connection on PC

---

## ⚙️ Configure ESP32 Code (5 minutes)

### Open and Edit ESP32_Client.ino
- [ ] Open Arduino IDE
- [ ] File > Open > Select `ESP32_Client.ino`

### Update Configuration Lines
Find and update these lines (around line 7-13):

```cpp
const char* SSID = "YOUR_SSID";              // ← Change this
const char* PASSWORD = "YOUR_PASSWORD";      // ← Change this
const char* SERVER_IP = "192.168.1.X";       // ← Change this
const int SERVER_PORT = 5000;                // Keep as is
const String DEVICE_ID = "ESP32_001";        // Can change if you want
```

- [ ] SSID set to your WiFi name
- [ ] PASSWORD set to your WiFi password
- [ ] SERVER_IP set to your Raspberry Pi IP
- [ ] SERVER_PORT is 5000
- [ ] DEVICE_ID is set (can keep default)

### Save Configuration
- [ ] Ctrl+S (or Cmd+S on Mac) to save
- [ ] Verify no syntax errors in console

---

## 🔌 Hardware Connection (5 minutes)

### Connect ESP32 to Computer
- [ ] Connect ESP32 to computer via USB cable
- [ ] Arduino IDE should detect it

### Select Board and Port
- [ ] Tools > Board > ESP32 > "ESP32 Dev Module" (or your model)
- [ ] Tools > Port > Select the COM port where ESP32 appears
  - Windows: `COM3`, `COM4`, etc.
  - Mac: `/dev/cu.usbserial-*`
  - Linux: `/dev/ttyUSB0`, etc.

### Verify Connection
- [ ] In Arduino IDE, you should see "Board: ESP32 Dev Module" at bottom
- [ ] You should see "Port: COMx" at bottom
- [ ] No connection errors in console

---

## 📤 Upload Code to ESP32 (5 minutes)

### Compile Code
- [ ] Sketch > Verify/Compile (or Ctrl+R)
- [ ] Should see "Compilation complete" message
- [ ] Fix any errors shown in red before uploading

### Upload Code
- [ ] Click Upload button (→ icon) in toolbar
- [ ] Wait for upload to complete
- [ ] Should see "Upload complete" message
- [ ] Do NOT disconnect USB cable yet

---

## 📊 Verify Connection (5-10 minutes)

### Open Serial Monitor
- [ ] Tools > Serial Monitor
- [ ] Set baud rate to **115200** (bottom right)
- [ ] You should see startup messages appearing

### Check for Success Indicators
Look for these messages in Serial Monitor (in order):

```
Starting WiFi connection...
. (dots appearing while connecting)
WiFi connected!
IP address: 192.168.1.X
Server URLs configured:
Base URL: http://192.168.1.X:5000/api/esp32
[✓] Device registered successfully
[✓] Heartbeat sent. Status: IDLE
[✓] Telemetry sent
```

- [ ] "WiFi connected!" appears
- [ ] "Device registered successfully" appears
- [ ] "Heartbeat sent" appears repeatedly
- [ ] No error messages in red

### If You See Errors

**WiFi Connection Failed:**
- [ ] Check SSID is spelled correctly (case sensitive)
- [ ] Check password is correct
- [ ] Verify 2.4GHz WiFi (not 5GHz)
- [ ] Try simple password without special characters

**Server Connection Failed:**
- [ ] Check SERVER_IP is correct
- [ ] Verify Raspberry Pi is powered on
- [ ] Check Flask server is running: `python main.py`
- [ ] Test from PC: `curl http://192.168.1.X:5000/api/esp32/health`

---

## ✅ Run API Tests (5 minutes)

### Check Server Health
Open terminal/PowerShell and run:
```powershell
curl http://192.168.1.X:5000/api/esp32/health
```
- [ ] Should see JSON response with device count
- [ ] Verify your ESP32 device_id is in the list

### List Connected Devices
```powershell
curl http://192.168.1.X:5000/api/esp32/devices
```
- [ ] Should show your ESP32 with status "IDLE"
- [ ] Should show device_id matches your ESP32

### Run Full Test Suite
In folder with `test_esp32_api.py`, run:
```powershell
python test_esp32_api.py
```
- [ ] Should run 10 tests
- [ ] Most tests should pass (✓)
- [ ] Report success rate at end

---

## 🎯 Send Test Commands (5 minutes)

### Send Movement Command
```powershell
curl -X POST http://192.168.1.X:5000/api/esp32/commands/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"command":"MOVE","params":{"destination":"AREA_10","speed":0.5}}'
```
- [ ] Should get success response
- [ ] Check Serial Monitor on ESP32
- [ ] Should see "Processing command: MOVE"

### Poll for Commands
```powershell
curl http://192.168.1.X:5000/api/esp32/commands/ESP32_001
```
- [ ] Should return list of commands
- [ ] Should be empty after ESP32 fetches them

### Send Telemetry Test
```powershell
curl -X POST http://192.168.1.X:5000/api/esp32/telemetry/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"battery":85,"temperature":28.3,"position":{"x":10,"y":20}}'
```
- [ ] Should return success response
- [ ] Check with GET request to verify recorded

---

## 🚀 Integration with Dashboard (Optional but Recommended)

### Verify MQTT Integration (Existing)
- [ ] Dashboard can calculate routes
- [ ] Routes are sent to MQTT broker
- [ ] MQTT connection is working

### Test Full Flow
- [ ] Open dashboard in browser: `http://192.168.1.X:5000`
- [ ] Select a destination and enter package info
- [ ] Click send/launch
- [ ] Check that:
  - [ ] Robot simulation starts
  - [ ] Database is updated
  - [ ] MQTT broker receives commands
  - [ ] ESP32 Serial Monitor shows receiving commands

---

## 📋 Troubleshooting Checklist

If something isn't working, check these:

### WiFi Issues
- [ ] SSID spelled correctly
- [ ] Password is correct
- [ ] WiFi is 2.4GHz (not 5GHz)
- [ ] ESP32 WiFi capability is enabled (should be by default)
- [ ] Power cycle ESP32 and try again

### Connection to Server
- [ ] Raspberry Pi is powered on
- [ ] Flask server is running: `python main.py`
- [ ] Raspberry Pi IP is correct
- [ ] PC can ping Raspberry Pi: `ping 192.168.1.X`
- [ ] Firewall not blocking port 5000

### Device Registration
- [ ] Device_id in code matches API calls
- [ ] Check: `curl http://192.168.1.X:5000/api/esp32/devices`
- [ ] Device should appear in list
- [ ] If not, restart ESP32 and Flask server

### Commands Not Received
- [ ] Device is registered (check previous point)
- [ ] Send command: `curl -X POST .../commands/ESP32_001 ...`
- [ ] Check: `curl http://192.168.1.X:5000/api/esp32/commands/ESP32_001`
- [ ] Command should appear in response
- [ ] Watch Serial Monitor on ESP32 while polling

### Serial Monitor Not Showing Output
- [ ] Baud rate set to 115200 (bottom right of Serial Monitor)
- [ ] ESP32 is powered (LED should be on)
- [ ] USB cable is properly connected
- [ ] Try different USB port on computer
- [ ] Try different USB cable

---

## ✨ Final Verification (All Systems Go!)

- [ ] WiFi connected (Serial Monitor shows it)
- [ ] Device registered (check `devices` endpoint)
- [ ] Commands being received (sent and confirmed)
- [ ] Telemetry being recorded (sent and confirmed)
- [ ] Integration with dashboard working
- [ ] No error messages in Serial Monitor
- [ ] No error messages from API responses
- [ ] All tests passing (test_esp32_api.py)

---

## 📞 Quick Support

### Serial Monitor Shows Error
1. Copy the error message
2. Check `ESP32_INTEGRATION_GUIDE.md` Troubleshooting section
3. Check `ESP32_NETWORK_SETUP.md` Troubleshooting section
4. Restart ESP32 (power cycle)
5. Restart Flask server

### API Not Responding
1. Verify server is running: `python main.py`
2. Test health check: `curl http://192.168.1.X:5000/api/esp32/health`
3. Check Raspberry Pi logs for errors
4. Restart server and try again

### Device Not Connecting
1. Check WiFi SSID and password in code
2. Verify Raspberry Pi IP in code
3. Test from PC: can you reach server?
4. Check Serial Monitor baud rate is 115200
5. Add more Serial.println() statements for debugging

---

## 🎉 Success Checklist

You're done when you can:

- [ ] ✅ ESP32 connects to WiFi automatically
- [ ] ✅ Device registers with server on startup
- [ ] ✅ Send commands from dashboard/API to ESP32
- [ ] ✅ ESP32 receives and processes commands
- [ ] ✅ ESP32 sends telemetry back to server
- [ ] ✅ View device status and history via API
- [ ] ✅ Multiple devices can be supported (just change DEVICE_ID)
- [ ] ✅ System is ready for robot control

---

## 📞 Support Resources

| Need Help With | File to Read |
|---|---|
| Quick overview | ESP32_IMPLEMENTATION_SUMMARY.md |
| Quick commands | ESP32_QUICK_REFERENCE.md |
| Network setup | ESP32_NETWORK_SETUP.md |
| Detailed guide | ESP32_INTEGRATION_GUIDE.md |
| Code reference | ESP32_Client.ino (comments in code) |
| API examples | ESP32_INTEGRATION_GUIDE.md (API section) |
| Testing | test_esp32_api.py |

---

**Estimated Total Time: 30-45 minutes**

Good luck! 🚀

---

Last Updated: December 9, 2025
Document Version: 1.0
