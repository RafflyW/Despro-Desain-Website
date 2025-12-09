# website/esp32_connection.py
"""
ESP32 Connection Management Module
Handles REST API connections from ESP32 devices to the Flask server
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# Dictionary untuk track ESP32 devices yang terhubung
connected_esp32_devices: Dict[str, dict] = {}

def register_esp32(device_id: str, device_info: dict) -> bool:
    """
    Register ESP32 device yang baru terhubung
    
    Args:
        device_id (str): Unique ID dari ESP32 (bisa MAC Address atau custom ID)
        device_info (dict): Informasi device (ip_address, firmware_version, etc)
    
    Returns:
        bool: True jika berhasil, False jika sudah terdaftar
    """
    if device_id in connected_esp32_devices:
        # Update existing device
        connected_esp32_devices[device_id]['last_seen'] = datetime.now().isoformat()
        connected_esp32_devices[device_id].update(device_info)
        return True
    
    # Register new device
    connected_esp32_devices[device_id] = {
        'device_id': device_id,
        'connected_at': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat(),
        'ip_address': device_info.get('ip_address', 'unknown'),
        'firmware_version': device_info.get('firmware_version', 'unknown'),
        'status': 'IDLE',
        **device_info
    }
    return True

def unregister_esp32(device_id: str) -> bool:
    """
    Unregister ESP32 device
    
    Args:
        device_id (str): Unique ID dari ESP32
    
    Returns:
        bool: True jika berhasil, False jika device tidak ada
    """
    if device_id in connected_esp32_devices:
        del connected_esp32_devices[device_id]
        return True
    return False

def update_esp32_status(device_id: str, status: str, data: dict = None) -> bool:
    """
    Update status ESP32 device
    
    Args:
        device_id (str): Unique ID dari ESP32
        status (str): Status baru (IDLE, MOVING, STOPPED, ERROR, etc)
        data (dict): Additional data untuk dicatat
    
    Returns:
        bool: True jika berhasil, False jika device tidak ada
    """
    if device_id not in connected_esp32_devices:
        return False
    
    connected_esp32_devices[device_id]['status'] = status
    connected_esp32_devices[device_id]['last_seen'] = datetime.now().isoformat()
    
    if data:
        connected_esp32_devices[device_id].update(data)
    
    return True

def get_esp32_status(device_id: str) -> Optional[dict]:
    """
    Get status ESP32 device
    
    Args:
        device_id (str): Unique ID dari ESP32
    
    Returns:
        dict: Status device atau None jika tidak ada
    """
    return connected_esp32_devices.get(device_id, None)

def get_all_esp32_devices() -> List[dict]:
    """
    Get list semua ESP32 devices yang terhubung
    
    Returns:
        list: List semua connected devices
    """
    return list(connected_esp32_devices.values())

def is_esp32_connected(device_id: str) -> bool:
    """
    Check apakah ESP32 device terhubung
    
    Args:
        device_id (str): Unique ID dari ESP32
    
    Returns:
        bool: True jika terhubung, False jika tidak
    """
    return device_id in connected_esp32_devices

def get_esp32_count() -> int:
    """Get jumlah ESP32 devices yang terhubung"""
    return len(connected_esp32_devices)

def send_command_to_esp32(device_id: str, command: str, params: dict = None) -> dict:
    """
    Queue command untuk dikirim ke ESP32
    
    Args:
        device_id (str): Unique ID dari ESP32
        command (str): Command yang akan dikirim
        params (dict): Parameter command
    
    Returns:
        dict: Response dari command
    """
    if device_id not in connected_esp32_devices:
        return {
            'success': False,
            'error': f'Device {device_id} tidak ditemukan',
            'device_id': device_id
        }
    
    # Format command payload
    payload = {
        'command': command,
        'params': params or {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Store command untuk dikirim
    if 'pending_commands' not in connected_esp32_devices[device_id]:
        connected_esp32_devices[device_id]['pending_commands'] = []
    
    connected_esp32_devices[device_id]['pending_commands'].append(payload)
    
    return {
        'success': True,
        'message': f'Command "{command}" queued untuk device {device_id}',
        'device_id': device_id,
        'command': command
    }

def get_pending_commands(device_id: str) -> List[dict]:
    """
    Get pending commands untuk ESP32 device
    
    Args:
        device_id (str): Unique ID dari ESP32
    
    Returns:
        list: List pending commands
    """
    if device_id not in connected_esp32_devices:
        return []
    
    return connected_esp32_devices[device_id].get('pending_commands', [])

def clear_pending_commands(device_id: str) -> bool:
    """
    Clear pending commands untuk ESP32 device (setelah device fetch)
    
    Args:
        device_id (str): Unique ID dari ESP32
    
    Returns:
        bool: True jika berhasil
    """
    if device_id not in connected_esp32_devices:
        return False
    
    connected_esp32_devices[device_id]['pending_commands'] = []
    return True

def record_esp32_telemetry(device_id: str, telemetry: dict) -> bool:
    """
    Record telemetry data dari ESP32
    
    Args:
        device_id (str): Unique ID dari ESP32
        telemetry (dict): Telemetry data (battery, temperature, position, etc)
    
    Returns:
        bool: True jika berhasil
    """
    if device_id not in connected_esp32_devices:
        return False
    
    if 'telemetry_history' not in connected_esp32_devices[device_id]:
        connected_esp32_devices[device_id]['telemetry_history'] = []
    
    telemetry_entry = {
        'timestamp': datetime.now().isoformat(),
        **telemetry
    }
    
    connected_esp32_devices[device_id]['telemetry_history'].append(telemetry_entry)
    connected_esp32_devices[device_id]['last_telemetry'] = telemetry_entry
    
    # Keep only last 100 telemetry entries
    if len(connected_esp32_devices[device_id]['telemetry_history']) > 100:
        connected_esp32_devices[device_id]['telemetry_history'] = \
            connected_esp32_devices[device_id]['telemetry_history'][-100:]
    
    return True
