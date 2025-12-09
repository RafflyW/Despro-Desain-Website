# ESP32 Network Configuration Guide

## 🌐 Network Setup Overview

Your ESP32 needs to connect to the same WiFi network as your Raspberry Pi server. This guide walks through the networking setup.

---

## 1. Find Your Raspberry Pi IP Address

### On Raspberry Pi (via Terminal)
```bash
hostname -I
```
Output example: `192.168.1.50 fe80::abcd:1234::1`
(Use the first one: `192.168.1.50`)

### Alternative Methods
```bash
# Method 2
ifconfig
# Look for "inet addr" under "wlan0" or "eth0"

# Method 3
ip addr show
# Look for lines with "inet" (not inet6)
```

### From PC/Laptop
1. Check your router's admin panel (usually 192.168.1.1 or 192.168.0.1)
2. Look for "Connected Devices" or "DHCP Clients"
3. Find "Raspberry Pi" in the list
4. Note its IP address

---

## 2. Configure ESP32_Client.ino

Edit these lines in the Arduino code:

```cpp
// ==================== CONFIGURATION ====================

// WiFi Configuration
const char* SSID = "YOUR_SSID";           // ← Replace with your WiFi name
const char* PASSWORD = "YOUR_PASSWORD";   // ← Replace with your WiFi password

// Server Configuration
const char* SERVER_IP = "192.168.1.X";    // ← Replace with Raspberry Pi IP
const int SERVER_PORT = 5000;             // ← Usually 5000
const String DEVICE_ID = "ESP32_001";     // ← Can rename if multiple devices
```

### Example Filled In:
```cpp
const char* SSID = "MyHomeWiFi";
const char* PASSWORD = "MyPassword123";
const char* SERVER_IP = "192.168.1.50";       // Your Raspberry Pi IP
const int SERVER_PORT = 5000;
const String DEVICE_ID = "ESP32_001";
```

---

## 3. Verify Network Connectivity

### Before Uploading to ESP32

**Step 1: Ping Raspberry Pi from PC**
```powershell
ping 192.168.1.50
```
Should see replies like: `Reply from 192.168.1.50: bytes=32 time=5ms TTL=64`

**Step 2: Verify Flask Server Running**
```powershell
curl http://192.168.1.50:5000/api/esp32/health
```
Should see JSON response like:
```json
{
  "status": "healthy",
  "connected_devices": 0,
  "devices": []
}
```

**Step 3: Check Firewall**
Make sure port 5000 is not blocked:
- Windows Defender Firewall might block it
- Add exception for port 5000 if needed

---

## 4. Typical WiFi Network Setup

```
┌──────────────────────┐
│  Your WiFi Router    │
│  (SSID: MyHomeWiFi)  │
└──────────┬───────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
ESP32    RasPi   PC
192.168. 192.168.1.50 192.168.1.X
1.100   (Flask Server)
```

### Same Network Check

All three (ESP32, Raspberry Pi, PC) should have IP addresses that start with the same prefix:
- ✅ `192.168.1.100`, `192.168.1.50`, `192.168.1.30` - Same network
- ❌ `192.168.1.100`, `192.168.0.50`, `10.0.0.30` - Different networks

**To fix:** Make sure all devices connect to the same WiFi network.

---

## 5. WiFi Security Considerations

### Supported WiFi Types
✅ WPA/WPA2 (Most common, RECOMMENDED)  
✅ WPA3 (Newer, usually supported)  
✅ WEP (Old, not recommended)  
❌ Open WiFi (No security)  

### If Connection Fails

1. **Check WiFi Band:** ESP32 needs 2.4GHz WiFi, NOT 5GHz
   - Many modern routers broadcast both
   - Check your router settings
   - Look for "2.4GHz" SSID separately

2. **Special Characters in Password:**
   - Avoid special characters like `&`, `@`, `#` in password
   - Stick to alphanumeric if having issues

3. **WiFi Password Length:**
   - Minimum 8 characters
   - Maximum 63 characters

---

## 6. Network Diagram

### Simple Setup (1 ESP32)
```
Internet
   │
   ▼
WiFi Router (192.168.1.1)
   │
   ├─ Raspberry Pi (192.168.1.50) - Flask Server :5000
   ├─ ESP32 (192.168.1.100) - Client
   └─ PC (192.168.1.X) - Dashboard Browser
```

### Advanced Setup (Multiple ESP32s)
```
Internet
   │
   ▼
WiFi Router (192.168.1.1)
   │
   ├─ Raspberry Pi (192.168.1.50) - Flask Server :5000
   ├─ ESP32_001 (192.168.1.100) - Robot 1
   ├─ ESP32_002 (192.168.1.101) - Robot 2
   ├─ ESP32_003 (192.168.1.102) - Robot 3
   └─ PC (192.168.1.X) - Dashboard Browser
```

Each ESP32 needs:
1. Unique DEVICE_ID in code
2. Unique IP (automatic via DHCP)
3. Same SERVER_IP (pointing to Raspberry Pi)

---

## 7. Port Configuration

### Port 5000 (Flask Server)
- Default Flask development port
- Used by ESP32 to communicate with server
- Make sure it's not blocked by firewall

### Changing Port (if needed)

**In Raspberry Pi `main.py`:**
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # ← Change 5000 to something else
```

**In ESP32 `ESP32_Client.ino`:**
```cpp
const int SERVER_PORT = 5000;  // ← Change to match
```

---

## 8. Troubleshooting Network Issues

### Issue: "Connection timeout"
**Causes:**
- Wrong SERVER_IP
- Raspberry Pi not running Flask
- Firewall blocking port 5000
- Different WiFi networks

**Solution:**
1. Verify IP with `hostname -I` on Raspberry Pi
2. Test with `curl` from PC first
3. Check firewall settings
4. Ensure all devices on same WiFi

### Issue: "WiFi connection failed"
**Causes:**
- Wrong SSID or password
- 5GHz WiFi instead of 2.4GHz
- Special characters in password
- WiFi disabled on ESP32

**Solution:**
```cpp
// Add debug output
Serial.println("Attempting: " + String(SSID));
Serial.println("Password length: " + String(strlen(PASSWORD)));

// Try with simple password first (no special chars)
const char* SSID = "TestWiFi";
const char* PASSWORD = "Test12345";
```

### Issue: "Device not connecting after registration"
**Causes:**
- Device registered but can't poll commands
- Network timeout mid-operation
- Server restarted, lost device state

**Solution:**
1. Check Serial Monitor output
2. Verify Flask still running on Raspberry Pi
3. Restart ESP32 (power cycle)
4. Check network connectivity with `ping` from PC

### Issue: "Commands not being received"
**Causes:**
- Device never polled for commands
- Device_id mismatch
- Commands not queued by server

**Solution:**
```bash
# Verify device registered
curl http://192.168.1.50:5000/api/esp32/devices

# Verify commands queued
curl http://192.168.1.50:5000/api/esp32/commands/ESP32_001

# Manually send test command
curl -X POST http://192.168.1.50:5000/api/esp32/commands/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"command":"MOVE","params":{"destination":"AREA_10","speed":0.5}}'
```

---

## 9. Monitoring Network Traffic

### Monitor from PC
```powershell
# View all devices on network
arp -a

# Ping Raspberry Pi
ping 192.168.1.50

# Test Flask API
curl http://192.168.1.50:5000/api/esp32/health

# Monitor connection (continuous)
ping -t 192.168.1.50
```

### Monitor from Raspberry Pi
```bash
# View network interfaces
ifconfig

# Monitor network activity
sudo nethogs

# Check listening ports
sudo netstat -tlnp | grep 5000

# Monitor Flask logs (if running in terminal)
# See console output directly
```

### Monitor from ESP32
```cpp
// Add to ESP32 code to see what it's trying to connect to
Serial.println("WiFi SSID: " + String(SSID));
Serial.println("Server IP: " + String(SERVER_IP));
Serial.println("Server Port: " + String(SERVER_PORT));
```

---

## 10. Static IP vs DHCP

### Recommended: DHCP (Automatic)
ESP32 gets IP automatically from router
- ✅ Easier setup
- ✅ No conflicts
- ✅ Recommended for most cases

The code uses DHCP by default - no changes needed.

### Alternative: Static IP (Manual)
Fix IP address to always be the same

**In ESP32_Client.ino:**
```cpp
// Before WiFi.begin()
IPAddress local_ip(192, 168, 1, 100);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);
IPAddress secondaryDNS(8, 8, 4, 4);

WiFi.config(local_ip, gateway, subnet, primaryDNS, secondaryDNS);
WiFi.begin(SSID, PASSWORD);
```

---

## 11. Testing Sequence

Follow this to verify everything works:

### Test 1: Ping Devices
```powershell
# From PC, ping Raspberry Pi
ping 192.168.1.50

# Should see: Reply from... time=Xms
```
✓ If works: Network connected

### Test 2: Flask Server
```powershell
# From PC, check Flask
curl http://192.168.1.50:5000/api/esp32/health

# Should see: {"status":"healthy",...}
```
✓ If works: Server running

### Test 3: Upload ESP32
- Configure `ESP32_Client.ino` with correct WiFi/IP
- Upload to board
- Check Serial Monitor

### Test 4: ESP32 Connection
Serial Monitor should show:
```
Starting WiFi connection...
WiFi connected!
IP address: 192.168.1.100
[✓] Device registered successfully
[✓] Heartbeat sent. Status: IDLE
```
✓ If works: ESP32 connected

### Test 5: Send Command
```powershell
curl -X POST http://192.168.1.50:5000/api/esp32/commands/ESP32_001 \
  -H "Content-Type: application/json" \
  -d '{"command":"MOVE","params":{"destination":"AREA_10","speed":0.5}}'
```

Serial Monitor on ESP32 should show:
```
[✓] Received 1 command(s)
Processing command: MOVE
Moving to: AREA_10 at speed: 0.5
```
✓ If works: Full communication working!

---

## 12. Quick Reference

### Required Info Before Starting
| Item | Where to Find | Example |
|------|---------------|---------|
| Raspberry Pi IP | `hostname -I` on Pi | 192.168.1.50 |
| WiFi SSID | WiFi network list | MyHomeWiFi |
| WiFi Password | Your WiFi password | MyPassword123 |
| Server Port | Flask config (default) | 5000 |
| Device ID | Custom (must be unique) | ESP32_001 |

### Configuration Template
```cpp
// Copy-paste and fill in:
const char* SSID = "________";              // Your WiFi name
const char* PASSWORD = "________";          // Your WiFi password
const char* SERVER_IP = "192.168.1.___";    // Your Pi IP (last number)
const int SERVER_PORT = 5000;               // Usually don't change
const String DEVICE_ID = "ESP32_001";       // Name for this device
```

---

## 13. Common IP Ranges

### Home Networks Usually Use:
- `192.168.1.0` - `192.168.1.255` (Most common)
- `192.168.0.0` - `192.168.0.255` (Also common)
- `10.0.0.0` - `10.0.0.255` (Some networks)

### Check Your Router's IP Range:
1. Windows: Check "Default Gateway" in `ipconfig /all`
2. Mac/Linux: Check `netstat -nr` or `route -n`
3. Router Admin Panel: Usually printed on router label

All connected devices must be in the **same range**.

---

**Network Setup Complete!** 🎉

Once configured, your ESP32 can communicate with the Flask server over WiFi.

---

Last Updated: December 9, 2025
