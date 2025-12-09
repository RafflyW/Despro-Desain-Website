# ESP32 Integration - Visual Diagrams & Architecture

## 1. System Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    INTERNET / CLOUD                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ (Optional)
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              LOCAL NETWORK (192.168.1.0/24)                  │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   WiFi Router    │  │  Wired Ethernet  │                │
│  │ (192.168.1.1)    │  │  (Optional)      │                │
│  └────────┬─────────┘  └──────────────────┘                │
│           │                                                │
│  ┌────────┼────────────────────────────┐                  │
│  │        │                            │                  │
│  ▼        ▼                            ▼                  │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│ │ Raspberry Pi │  │    ESP32_001 │  │ Laptop/PC    │     │
│ │ 192.168.1.50 │  │ 192.168.1.100│  │ 192.168.1.X  │     │
│ │              │  │              │  │              │     │
│ │ Flask Server │  │ Robot Device │  │  Dashboard   │     │
│ │ Port 5000    │  │              │  │   Browser    │     │
│ └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Communication Protocol Flow

### A. Device Registration & Startup

```
┌─────────┐                          ┌─────────────┐
│  ESP32  │                          │ Flask Server│
│ Startup │                          │             │
└────┬────┘                          └─────────────┘
     │
     │ 1. Boot, Connect to WiFi
     │
     ├─ WiFi connected ✓
     │
     │ 2. POST /register
     ├─────────────────────────────────────►│
     │   {"device_id": "ESP32_001",         │
     │    "firmware_version": "1.0.0"}      │
     │                                       │ Register device
     │                                       │ in memory
     │◄─────────────────────────────────────┤
     │   {"success": true, "device_id": "..."} │
     │
     │ 3. Start polling loop:
     ├─ Every 5s: GET /commands/{id}
     ├─ Every 10s: POST /telemetry/{id}
     ├─ Every 30s: PUT /status/{id}
     │
     └─ Connected & Running ✓
```

### B. Command Execution Flow

```
┌─────────┐                          ┌─────────────┐
│Dashboard│                          │ Flask Server│
│Browser  │                          │             │
└────┬────┘                          └─────────────┘
     │                                       ▲
     │ 1. User clicks "Send Package"        │
     │                                       │
     ├─ Calculate Route                     │
     ├─ Generate Instructions               │
     │                                       │
     │ 2. POST /send (form submission)      │
     ├──────────────────────────────────────►│
     │   destination=AREA_10, sender=John   │
     │                                       │ Store in:
     │                                       │ - Database
     │                                       │ - MQTT Broker
     │                                       │ - ESP32 Queue
     │◄──────────────────────────────────────┤
     │   Redirect to monitor page            │
     │
     │ 3. Dashboard updates (polling)       │
     │    Shows "Robot Moving..."           │

     ┌──────────────┐
     │    ESP32     │
     │   (Device)   │
     └──────┬───────┘
            │
            │ 4. Every 5s: GET /commands/ESP32_001
            │
            ├──────────────────────────────────────►
            │                                        │
            │◄──────────────────────────────────────┤
            │   [{"command":"MOVE",                │
            │     "params":{"destination":"AREA_10"}}]
            │
            │ 5. Process command
            ├─ Move to AREA_10
            ├─ Report status updates
            │
            │ 6. Every 10s: POST /telemetry
            │   {"battery":85, "position":{x:10,y:20}}
            │
            └─ Command executed ✓
```

---

## 3. Request Response Cycle

### Request Cycle (5-second loop on ESP32)

```
Time    Action
────────────────────────────────────────────────
0s      ├─ GET /commands/ESP32_001
        ├─ Response: [] (empty)
        │
5s      ├─ GET /commands/ESP32_001
        ├─ Response: [{"command":"MOVE",...}]
        ├─ Process command
        │
10s     ├─ POST /telemetry/ESP32_001
        ├─ Response: {"success":true}
        │
15s     ├─ GET /commands/ESP32_001
        ├─ Response: [] (commands cleared)
        │
20s     ├─ No action (unless commanded)
        │
25s     ├─ POST /telemetry/ESP32_001
        │
30s     ├─ PUT /status/ESP32_001 (heartbeat)
        └─ Repeat...
```

---

## 4. Data Model: Device State

```
┌─────────────────────────────────────────────┐
│        Connected ESP32 Device State         │
├─────────────────────────────────────────────┤
│                                             │
│  device_id: "ESP32_001"                    │
│  status: "MOVING" / "IDLE" / "STOPPED" ... │
│  connected_at: "2025-12-09T10:00:00"       │
│  last_seen: "2025-12-09T10:30:45"          │
│  ip_address: "192.168.1.100"               │
│  firmware_version: "1.0.0"                 │
│  mac_address: "AA:BB:CC:DD:EE:FF"          │
│                                             │
│  pending_commands: [                       │
│    {                                        │
│      command: "MOVE",                      │
│      params: {destination: "AREA_10", ...} │
│      timestamp: "2025-12-09T10:30:00"      │
│    }                                        │
│  ]                                          │
│                                             │
│  last_telemetry: {                         │
│    battery: 85.5,                          │
│    temperature: 28.3,                      │
│    position: {x: 15, y: 20},               │
│    signal_strength: -60                    │
│  }                                          │
│                                             │
│  telemetry_history: [                      │
│    {...100 entries...}                     │
│  ]                                          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 5. Command Types & Execution

```
┌────────────────────────────────────────────────────┐
│        Command Processing on ESP32                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  Received: {"command": "MOVE",                    │
│            "params": {"destination": "AREA_10"}}  │
│            ▼                                       │
│         Parse                                     │
│            ▼                                       │
│    ┌──────────────────┐                          │
│    │  Command Router  │                          │
│    └────────┬─────────┘                          │
│             │                                    │
│    ┌────────┼────────┬───────────┐              │
│    │        │        │           │              │
│    ▼        ▼        ▼           ▼              │
│  MOVE    STOP   RETURN  EMERGENCY_STOP          │
│    │        │        │           │              │
│    ├─►Set target     │           │              │
│    ├─►Calculate path │           │              │
│    ├─►Start motors   │           │              │
│    │                 │           │              │
│    │              Stop motors    │              │
│    │              Set status=STOPPED           │
│    │                             │              │
│    │                          Return to START  │
│    │                          Calculate route  │
│    │                                            │
│    │                          Emergency stop!  │
│    │                          All motors off   │
│    │                          Set status=EMERGENCY
│    │                                            │
│    └─►Report status ✓                          │
│       Report telemetry ✓                       │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 6. Telemetry Collection Timeline

```
Device Lifetime:
┌────┬────┬────┬────┬────┬────┬────┬────┐
│    │    │    │    │    │    │    │    │ Time (seconds)
0    5    10   15   20   25   30   35   40

Commands │    │    │    │ ◄──┤    │    │
Polling  ├────┤    ├────┤    ├────┤    ├────
         │    │    │    │    │    │    │

Telemetry│    │ ◄──┤    │    │ ◄──┤    │ ◄──
Sending  │    ├────┤    ├────┤    ├────┤
         │    │    │    │    │    │    │

Heartbeat│    │    │    │    │    │ ◄──┤
         │    │    │    │    │    ├────┤
         │    │    │    │    │    │    │

Entry    #0   #1   #2   #3   #4   #5   #6
in log

Last 100 telemetry entries stored in memory
(Circular buffer - oldest entry dropped when full)
```

---

## 7. Multiple Devices Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Raspberry Pi Flask Server                   │
│                  (Single Instance)                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Connected Devices Dictionary:                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ "ESP32_001": {...state...}                        │ │
│  │ "ESP32_002": {...state...}                        │ │
│  │ "ESP32_003": {...state...}                        │ │
│  │ "ESP32_004": {...state...}                        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  API Routes:                                            │
│  ├─ /api/esp32/register       (Any device can join)    │
│  ├─ /api/esp32/status/{id}    (Device-specific)        │
│  ├─ /api/esp32/commands/{id}  (Device-specific)        │
│  ├─ /api/esp32/telemetry/{id} (Device-specific)        │
│  └─ /api/esp32/devices        (List all devices)       │
│                                                          │
└──────────────────────────────────────────────────────────┘
        │              │              │              │
        │              │              │              │
    ┌───▼──┐       ┌───▼──┐      ┌───▼──┐      ┌───▼──┐
    │ESP32 │       │ESP32 │      │ESP32 │      │ESP32 │
    │ 001  │       │ 002  │      │ 003  │      │ 004  │
    └──────┘       └──────┘      └──────┘      └──────┘
```

---

## 8. Software Layer Stack

```
┌─────────────────────────────────────────────┐
│         Web Dashboard (HTML/CSS/JS)         │
│  User sends commands via form submission    │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│      Flask Web Framework (views.py)         │
│  Handles routes, templating, redirects      │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│   Application Logic (route_calculation,     │
│  route_instructions, database_management)  │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┼───────┐
         │       │       │
    ┌────▼──┐ ┌─▼──┐ ┌──▼───┐
    │MQTT   │ │DB  │ │ESP32  │
    │Conn   │ │Mgmt│ │Routes │
    └────────┘ └────┘ └───────┘
         │       │       │
    ┌────▼───────▼───────▼────┐
    │   HTTP/TCP/IP Stack     │
    │  WiFi / Ethernet        │
    └────────────────────────┘
         │              │
    ┌────▼──┐      ┌────▼──┐
    │MQTT   │      │ESP32  │
    │Broker │      │Devices│
    └───────┘      └───────┘
```

---

## 9. File Organization

```
Despro-Desain-Website/
│
├─ main.py                              (Entry point)
├─ website/
│  ├─ __init__.py                      (App factory - UPDATED)
│  ├─ views.py                         (Routes - uses ESP32)
│  ├─ route_calculation.py             (A* algorithm)
│  ├─ route_instructions.py            (Instruction generation)
│  ├─ database_management.py           (Database ops)
│  ├─ mqtt_connection.py               (MQTT integration)
│  ├─ mockup_robot.py                  (Robot simulation)
│  │
│  ├─ esp32_connection.py              (NEW - Device mgmt)
│  ├─ esp32_routes.py                  (NEW - API endpoints)
│  └─ esp32_integration_example.py     (NEW - Helper funcs)
│
├─ ESP32_Client.ino                    (NEW - Arduino code)
│
├─ Documentation/
│  ├─ ESP32_README.md                  (NEW - This overview)
│  ├─ ESP32_IMPLEMENTATION_SUMMARY.md  (NEW - What was done)
│  ├─ ESP32_INTEGRATION_GUIDE.md       (NEW - Setup guide)
│  ├─ ESP32_QUICK_REFERENCE.md         (NEW - Quick ref)
│  ├─ ESP32_NETWORK_SETUP.md           (NEW - Network setup)
│  └─ ESP32_SETUP_CHECKLIST.md         (NEW - Step by step)
│
└─ test_esp32_api.py                   (NEW - Test suite)
```

---

## 10. Integration Points

```
┌───────────────────────────────────────────────────────┐
│          Dashboard (Frontend)                         │
│  Route send form                                      │
└────────────────┬────────────────────────────────────┘
                 │
                 │ POST /send
                 ▼
┌───────────────────────────────────────────────────────┐
│       views.py (send_page function)                   │
├───────────────────────────────────────────────────────┤
│                                                       │
│  1. Calculate Route                                   │
│     └─► route_calculation.a_star_search()            │
│                                                       │
│  2. Generate Instructions                            │
│     └─► route_instructions.generate_instructions()   │
│                                                       │
│  3. Store in Database                                │
│     └─► database_management.update_tujuan_db()       │
│                                                       │
│  4. Send via MQTT                                    │
│     └─► mqtt_connection.send_instructions_via_mqtt() │
│                                                       │
│  5. Queue for ESP32                                  │
│     └─► esp32_connection.send_command_to_esp32()     │
│          (NEW INTEGRATION POINT)                     │
│                                                       │
│  6. Run Robot Simulation                             │
│     └─► mockup_robot.run_robot_simulation()          │
│                                                       │
│  7. Redirect to Monitor                              │
│     └─► Dashboard shows "Robot Moving..."            │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 11. State Machine (ESP32 Status)

```
           ┌──────────────┐
           │ UNREGISTERED │
           └────────┬─────┘
                    │ Register
                    ▼
           ┌──────────────┐
    ┌─────►│    IDLE      │◄─────┐
    │      └────────┬─────┘      │
    │               │            │
    │        Command: MOVE       │
    │               │            │
    │               ▼            │
    │      ┌──────────────┐      │
    │      │   MOVING     │      │
    │      └────────┬─────┘      │
    │               │            │
    │   Reached destination      │
    │   or STOP command          │
    │               │            │
    │               ▼            │
    │      ┌──────────────┐      │
    │      │   STOPPED    │      │
    │      └────────┬─────┘      │
    │               │            │
    │       RETURN or MOVE       │
    └───────────────┘            │
                                  │
                    Command: EMERGENCY_STOP
                                  │
                    ┌─────────────┘
                    ▼
           ┌──────────────────┐
           │ EMERGENCY_STOP   │
           │ (Manual reset req)
           └──────────────────┘
```

---

## 12. Sequence Diagram: Full Operation

```
ESP32    WiFi    RaspPi    Database   MQTT     Dashboard
 │        │        │           │        │         │
 │        │ Connect│           │        │         │
 ├────────────────►│           │        │         │
 │        │        │           │        │         │
 │        │ POST /register     │        │         │
 │        ├───────►│           │        │         │
 │        │        │ Register  │        │         │
 │        │        ├──────────►│        │         │
 │        │        │ OK        │        │         │
 │        │◄───────┤           │        │         │
 │        │        │           │        │         │ User
 │        │        │           │        │         │ clicks
 │        │        │           │        │         │ Send
 │        │        │◄──────────────────────────┤ │
 │        │ GET    │ POST /send                 │ │
 │        │ /cmd   ├──────────►│                 │ │
 │        ├───────►│           │ Update DB      │ │
 │        │        │           ├───────────────►│ │
 │        │ MOVE   │ MQTT Pub  │                │ │
 │        │        ├──────────────────────────►│ │
 │        │◄───────┤           │                 │ │
 │        │        │ Queue cmd │                 │ │
 │        │        │ for ESP32 │                 │ │
 │        │        │           │                 │ │
 │ Start  │        │           │                 │ │
 │ Motion │        │           │                 │ │
 │        │        │           │                 │ │
 │ POST   │        │           │                 │ │
 │ /telem │        │           │                 │ │
 ├────────────────►│           │                 │ │
 │        │        │ POST /telemetry            │ │
 │        │        ├──────────►│ Record         │ │
 │        │        │ OK        │ Telemetry     │ │
 │        │◄───────┤           │                 │ │
 │        │        │           │ Poll status    │ │
 │        │        │◄──────────────────────────┤ │
 │        │        │           │                 │ │
 │ Reach  │        │           │                 │ │
 │ Goal   │        │           │                 │ │
 │        │ Final  │           │                 │ │
 │ POST   │ Telem  │           │                 │ │
 ├────────────────►│           │                 │ │
 │        │        │ OK, Idle  │                 │ │
 │        │◄───────┤           │                 │ │
 │        │        │           │           Done │ │
 │        │        │           │                 │ │
 └────────────────────────────────────────────────┘
```

---

## 13. Performance Characteristics

```
┌────────────────────────────────────────────────────┐
│        Performance Metrics & Intervals             │
├────────────────────────────────────────────────────┤
│                                                    │
│  WiFi Connection:       ~2-5 seconds              │
│  Device Registration:   ~100-500 ms               │
│  Command Poll:          5 seconds (interval)      │
│  Command Latency:       ~100-200 ms (typical)     │
│  Telemetry Send:        10 seconds (interval)     │
│  Telemetry Latency:     ~50-150 ms (typical)      │
│  Heartbeat:             30 seconds (interval)     │
│  Memory per device:     ~5-10 KB (state + history)│
│  Max devices (RAM):     Depends on Pi RAM          │
│  Max devices (API):     Theoretical unlimited     │
│                                                    │
│  Typical Pi 4 (4GB RAM):  Support ~100+ devices  │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 14. Scaling Scenarios

### Scenario 1: Single Robot (Development)
```
1 Flask Server
   ↓
1 ESP32 Device
→ Easy testing
→ Quick validation
```

### Scenario 2: Multiple Robots (Production)
```
1 Flask Server
   │
   ├─ ESP32_001 (Robot A)
   ├─ ESP32_002 (Robot B)
   ├─ ESP32_003 (Robot C)
   └─ ESP32_004 (Robot D)
→ Independent control
→ Real-time monitoring
→ Distributed tasks
```

### Scenario 3: Distributed System (Advanced)
```
Multiple Flask Servers (load balanced)
   │
   ├─ Server 1 (Pi 1)
   │  ├─ ESP32_001
   │  ├─ ESP32_002
   │  └─ ESP32_003
   │
   ├─ Server 2 (Pi 2)
   │  ├─ ESP32_004
   │  ├─ ESP32_005
   │  └─ ESP32_006
   │
   └─ Shared Database
      └─ Central MQTT Broker
→ High availability
→ Geographic distribution
→ Fault tolerance
```

---

This visual guide helps understand the complete system architecture, data flow, and communication patterns of the ESP32-to-Raspberry-Pi integration.

**Last Updated:** December 9, 2025
