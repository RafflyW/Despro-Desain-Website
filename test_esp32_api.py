#!/usr/bin/env python3
"""
ESP32 Testing Script
Test ESP32 connection and API endpoints without needing actual hardware
"""

import requests
import json
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:5000"  # Change to your Raspberry Pi IP
DEVICE_ID = "ESP32_TEST_001"

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_health():
    """Test health endpoint"""
    print_header("Testing Server Health")
    
    try:
        response = requests.get(f"{SERVER_URL}/api/esp32/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy")
            print(f"  Connected devices: {data['connected_devices']}")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def test_register_device():
    """Test device registration"""
    print_header("Testing Device Registration")
    
    payload = {
        "device_id": DEVICE_ID,
        "firmware_version": "1.0.0",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "capabilities": ["MOVE", "STOP", "RETURN"]
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/esp32/register",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Device registered: {data['device_id']}")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_get_all_devices():
    """Test get all devices"""
    print_header("Listing All Devices")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/esp32/devices",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data['count']} device(s)")
            
            for device in data['devices']:
                print(f"\n  Device: {device['device_id']}")
                print(f"    Status: {device['status']}")
                print(f"    Connected: {device['connected_at']}")
                print(f"    Last Seen: {device['last_seen']}")
                if 'ip_address' in device:
                    print(f"    IP: {device['ip_address']}")
            return True
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_get_status():
    """Test get device status"""
    print_header(f"Getting Status for {DEVICE_ID}")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/esp32/status/{DEVICE_ID}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status retrieved")
            print(json.dumps(data, indent=2))
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_update_status():
    """Test update device status"""
    print_header(f"Updating Status for {DEVICE_ID}")
    
    payload = {
        "status": "MOVING",
        "data": {
            "current_position": {"x": 10, "y": 20},
            "speed": 0.5,
            "battery": 85
        }
    }
    
    try:
        response = requests.put(
            f"{SERVER_URL}/api/esp32/status/{DEVICE_ID}",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status updated")
            print(json.dumps(data, indent=2))
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_send_command():
    """Test sending command to device"""
    print_header(f"Sending Command to {DEVICE_ID}")
    
    payload = {
        "command": "MOVE",
        "params": {
            "destination": "AREA_10",
            "speed": 0.5
        }
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/esp32/commands/{DEVICE_ID}",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Command queued")
            print(json.dumps(data, indent=2))
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_poll_commands():
    """Test polling commands"""
    print_header(f"Polling Commands for {DEVICE_ID}")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/esp32/commands/{DEVICE_ID}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Poll successful - {data['count']} command(s) available")
            
            if data['count'] > 0:
                for cmd in data['commands']:
                    print(f"\n  Command: {cmd['command']}")
                    print(f"    Params: {cmd['params']}")
                    print(f"    Sent at: {cmd['timestamp']}")
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_send_telemetry():
    """Test sending telemetry"""
    print_header(f"Sending Telemetry for {DEVICE_ID}")
    
    payload = {
        "battery": 85.5,
        "temperature": 28.3,
        "signal_strength": -60,
        "position": {"x": 15, "y": 20},
        "status": "MOVING"
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/esp32/telemetry/{DEVICE_ID}",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Telemetry recorded")
            print(json.dumps(data, indent=2))
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_get_telemetry():
    """Test getting telemetry"""
    print_header(f"Getting Telemetry for {DEVICE_ID}")
    
    try:
        response = requests.get(
            f"{SERVER_URL}/api/esp32/telemetry/{DEVICE_ID}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Telemetry retrieved")
            print(f"\n  Latest Telemetry:")
            print(json.dumps(data['latest'], indent=4))
            print(f"\n  History entries: {len(data['history'])}")
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_unregister_device():
    """Test device unregistration"""
    print_header(f"Unregistering {DEVICE_ID}")
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/esp32/unregister/{DEVICE_ID}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Device unregistered")
            print(json.dumps(data, indent=2))
            return True
        elif response.status_code == 404:
            print_error(f"Device not found")
            return False
        else:
            print_error(f"Request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{BLUE}{'='*50}")
    print(f"  ESP32 API Test Suite")
    print(f"  Server: {SERVER_URL}")
    print(f"  Device ID: {DEVICE_ID}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}{RESET}\n")
    
    tests = [
        ("Health Check", test_health),
        ("Register Device", test_register_device),
        ("Get All Devices", test_get_all_devices),
        ("Get Device Status", test_get_status),
        ("Update Device Status", test_update_status),
        ("Send Command", test_send_command),
        ("Poll Commands", test_poll_commands),
        ("Send Telemetry", test_send_telemetry),
        ("Get Telemetry", test_get_telemetry),
        ("Unregister Device", test_unregister_device),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Test error: {e}")
            failed += 1
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print_header("Test Summary")
    print_success(f"Passed: {passed}")
    print_error(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1].lower()
        
        tests = {
            "health": test_health,
            "register": test_register_device,
            "devices": test_get_all_devices,
            "status": test_get_status,
            "update": test_update_status,
            "command": test_send_command,
            "poll": test_poll_commands,
            "telemetry": test_send_telemetry,
            "get_telemetry": test_get_telemetry,
            "unregister": test_unregister_device,
        }
        
        if test_name in tests:
            tests[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available: {', '.join(tests.keys())}")
    else:
        # Run all tests
        run_all_tests()
