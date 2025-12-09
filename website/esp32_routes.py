# website/esp32_routes.py
"""
ESP32 API Routes
Provides REST endpoints untuk ESP32 devices berkomunikasi dengan server
"""

from flask import Blueprint, request, jsonify
from .esp32_connection import (
    register_esp32, 
    unregister_esp32,
    update_esp32_status,
    get_esp32_status,
    get_all_esp32_devices,
    is_esp32_connected,
    get_pending_commands,
    clear_pending_commands,
    record_esp32_telemetry,
    send_command_to_esp32
)
import logging

esp32_bp = Blueprint('esp32', __name__, url_prefix='/api/esp32')

logger = logging.getLogger(__name__)

@esp32_bp.route('/register', methods=['POST'])
def esp32_register():
    """
    Register ESP32 device ke server
    
    Request Body:
    {
        "device_id": "ESP32_001",
        "ip_address": "192.168.1.100",
        "firmware_version": "1.0.0",
        "mac_address": "AA:BB:CC:DD:EE:FF"
    }
    
    Returns:
        200: Device registered successfully
        400: Missing required fields
    """
    try:
        data = request.get_json()
        
        if not data or 'device_id' not in data:
            return jsonify({'error': 'device_id diperlukan'}), 400
        
        device_id = data['device_id']
        device_info = {
            'ip_address': data.get('ip_address', request.remote_addr),
            'firmware_version': data.get('firmware_version'),
            'mac_address': data.get('mac_address'),
            'capabilities': data.get('capabilities', [])
        }
        
        success = register_esp32(device_id, device_info)
        
        logger.info(f"ESP32 {device_id} registered from {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'message': f'Device {device_id} berhasil terdaftar',
            'device_id': device_id
        }), 200
    
    except Exception as e:
        logger.error(f"Error registering ESP32: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/unregister/<device_id>', methods=['POST'])
def esp32_unregister(device_id):
    """
    Unregister ESP32 device dari server
    
    Returns:
        200: Device unregistered successfully
        404: Device tidak ditemukan
    """
    try:
        if unregister_esp32(device_id):
            logger.info(f"ESP32 {device_id} unregistered")
            return jsonify({
                'success': True,
                'message': f'Device {device_id} berhasil diunregister'
            }), 200
        else:
            return jsonify({'error': 'Device tidak ditemukan'}), 404
    
    except Exception as e:
        logger.error(f"Error unregistering ESP32: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/status/<device_id>', methods=['GET'])
def get_device_status(device_id):
    """
    Get status dari ESP32 device tertentu
    
    Returns:
        200: Device status
        404: Device tidak ditemukan
    """
    try:
        status = get_esp32_status(device_id)
        
        if status is None:
            return jsonify({'error': 'Device tidak ditemukan'}), 404
        
        return jsonify(status), 200
    
    except Exception as e:
        logger.error(f"Error getting ESP32 status: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/status/<device_id>', methods=['PUT'])
def update_device_status(device_id):
    """
    Update status dari ESP32 device
    
    Request Body:
    {
        "status": "MOVING",
        "data": {
            "current_position": {"x": 10, "y": 20},
            "speed": 0.5
        }
    }
    
    Returns:
        200: Status updated successfully
        404: Device tidak ditemukan
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'status diperlukan'}), 400
        
        status = data['status']
        additional_data = data.get('data', {})
        
        if update_esp32_status(device_id, status, additional_data):
            logger.info(f"ESP32 {device_id} status updated to {status}")
            return jsonify({
                'success': True,
                'message': f'Status updated ke {status}',
                'device_id': device_id
            }), 200
        else:
            return jsonify({'error': 'Device tidak ditemukan'}), 404
    
    except Exception as e:
        logger.error(f"Error updating ESP32 status: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/devices', methods=['GET'])
def get_devices():
    """
    Get list semua ESP32 devices yang terhubung
    
    Returns:
        200: List devices
    """
    try:
        devices = get_all_esp32_devices()
        return jsonify({
            'devices': devices,
            'count': len(devices)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/commands/<device_id>', methods=['GET'])
def get_commands(device_id):
    """
    Get pending commands untuk ESP32 device
    (Endpoint ini digunakan ESP32 untuk pull commands dari server)
    
    Returns:
        200: List pending commands
        404: Device tidak ditemukan
    """
    try:
        if not is_esp32_connected(device_id):
            return jsonify({'error': 'Device tidak ditemukan'}), 404
        
        commands = get_pending_commands(device_id)
        
        # Clear commands setelah di-fetch oleh device
        clear_pending_commands(device_id)
        
        logger.info(f"ESP32 {device_id} pulled {len(commands)} command(s)")
        
        return jsonify({
            'device_id': device_id,
            'commands': commands,
            'count': len(commands)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting commands: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/commands/<device_id>', methods=['POST'])
def send_command(device_id):
    """
    Send command ke ESP32 device
    
    Request Body:
    {
        "command": "MOVE",
        "params": {
            "destination": "AREA_10",
            "speed": 0.5
        }
    }
    
    Returns:
        200: Command queued successfully
        404: Device tidak ditemukan
    """
    try:
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({'error': 'command diperlukan'}), 400
        
        command = data['command']
        params = data.get('params', {})
        
        result = send_command_to_esp32(device_id, command, params)
        
        if result['success']:
            logger.info(f"Command '{command}' sent to ESP32 {device_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/telemetry/<device_id>', methods=['POST'])
def receive_telemetry(device_id):
    """
    Receive telemetry data dari ESP32 device
    
    Request Body:
    {
        "battery": 85.5,
        "temperature": 28.3,
        "position": {"x": 15, "y": 20},
        "signal_strength": -60
    }
    
    Returns:
        200: Telemetry recorded successfully
        404: Device tidak ditemukan
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'telemetry data diperlukan'}), 400
        
        if record_esp32_telemetry(device_id, data):
            logger.info(f"Telemetry received from ESP32 {device_id}")
            return jsonify({
                'success': True,
                'message': 'Telemetry recorded',
                'device_id': device_id
            }), 200
        else:
            return jsonify({'error': 'Device tidak ditemukan'}), 404
    
    except Exception as e:
        logger.error(f"Error recording telemetry: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/telemetry/<device_id>', methods=['GET'])
def get_telemetry(device_id):
    """
    Get latest telemetry dari ESP32 device
    
    Returns:
        200: Latest telemetry data
        404: Device tidak ditemukan
    """
    try:
        status = get_esp32_status(device_id)
        
        if status is None:
            return jsonify({'error': 'Device tidak ditemukan'}), 404
        
        telemetry = status.get('last_telemetry', {})
        telemetry_history = status.get('telemetry_history', [])
        
        return jsonify({
            'device_id': device_id,
            'latest': telemetry,
            'history': telemetry_history
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting telemetry: {e}")
        return jsonify({'error': str(e)}), 500

@esp32_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        200: Server is healthy
    """
    devices = get_all_esp32_devices()
    return jsonify({
        'status': 'healthy',
        'connected_devices': len(devices),
        'devices': [d['device_id'] for d in devices]
    }), 200
