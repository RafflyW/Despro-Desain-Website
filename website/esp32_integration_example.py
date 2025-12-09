# website/esp32_integration_example.py
"""
Example: Integration of ESP32 with Route Instructions
Shows how to send route instructions from the dashboard to ESP32
"""

from website.esp32_connection import send_command_to_esp32
from website.route_calculation import a_star_search, coords
from website.route_instructions import generate_instructions
import json

def send_route_to_esp32(device_id: str, destination: str, instructions: list, route_path: list):
    """
    Send calculated route and instructions to ESP32 device
    
    This function is called after route calculation in views.py
    
    Args:
        device_id (str): ESP32 device ID (e.g., "ESP32_001")
        destination (str): Target location
        instructions (list): List of navigation instructions from route_instructions.py
        route_path (list): Full path nodes ["START", "NODE1", "NODE2", ...]
    
    Returns:
        dict: Success/failure response
    
    Example Usage in views.py:
    ========================
    
    from .esp32_integration_example import send_route_to_esp32
    
    # After generating instructions
    list_instruksi = generate_instructions(path, coords)
    rute_str = " -> ".join(path)
    
    # Send to ESP32
    result = send_route_to_esp32("ESP32_001", tujuan, list_instruksi, path)
    
    if result['success']:
        print(f"Route sent to ESP32: {result['message']}")
    else:
        print(f"Failed to send to ESP32: {result['error']}")
    """
    
    try:
        # Package the route data
        route_payload = {
            "destination": destination,
            "path": route_path,
            "instructions": instructions,
            "path_string": " -> ".join(route_path),
            "total_nodes": len(route_path),
            "total_instructions": len(instructions)
        }
        
        # Send as ROUTE command to ESP32
        result = send_command_to_esp32(
            device_id,
            command="ROUTE",
            params=route_payload
        )
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'device_id': device_id
        }

def send_simple_movement(device_id: str, destination: str, speed: float = 0.5):
    """
    Send simple movement command to ESP32
    
    Args:
        device_id (str): ESP32 device ID
        destination (str): Target location
        speed (float): Movement speed (0.0 to 1.0)
    
    Returns:
        dict: Success/failure response
    
    Example:
        result = send_simple_movement("ESP32_001", "AREA_10", speed=0.7)
    """
    result = send_command_to_esp32(
        device_id,
        command="MOVE",
        params={
            "destination": destination,
            "speed": speed
        }
    )
    return result

def send_stop_command(device_id: str):
    """Stop ESP32 movement immediately"""
    result = send_command_to_esp32(
        device_id,
        command="STOP"
    )
    return result

def send_return_command(device_id: str):
    """Tell ESP32 to return to starting position"""
    result = send_command_to_esp32(
        device_id,
        command="RETURN"
    )
    return result

def send_emergency_stop(device_id: str):
    """Emergency stop - highest priority"""
    result = send_command_to_esp32(
        device_id,
        command="EMERGENCY_STOP"
    )
    return result

# ============= ESP32 Command Handler =============

def parse_esp32_command(command_dict: dict):
    """
    Parse command object to understand what ESP32 should do
    
    Used to understand incoming commands from the server queue
    """
    
    command_type = command_dict.get('command', '')
    params = command_dict.get('params', {})
    
    if command_type == 'ROUTE':
        return {
            'type': 'route',
            'destination': params.get('destination'),
            'instructions': params.get('instructions', []),
            'path': params.get('path', [])
        }
    
    elif command_type == 'MOVE':
        return {
            'type': 'move',
            'destination': params.get('destination'),
            'speed': params.get('speed', 0.5)
        }
    
    elif command_type == 'STOP':
        return {
            'type': 'stop'
        }
    
    elif command_type == 'RETURN':
        return {
            'type': 'return'
        }
    
    elif command_type == 'EMERGENCY_STOP':
        return {
            'type': 'emergency_stop'
        }
    
    else:
        return {
            'type': 'unknown',
            'raw_command': command_type
        }

# ============= Integration Example for views.py =============

"""
EXAMPLE: How to modify views.py to send routes to ESP32

def send_page():
    # ... existing code ...
    
    if request.method == 'POST':
        tujuan = request.form.get('pilihan').upper()
        nama = request.form.get('nama')
        
        # Validasi Input
        path, msg = a_star_search('START', tujuan)
        
        if path:
            rute_str = " -> ".join(path)
            hasil_rute = rute_str
            status_rute = "RUTE OK! ROBOT DILUNCURKAN"
            warna_status = "text-success"
            
            list_instruksi = generate_instructions(path, coords)
            
            # Send to MQTT (existing)
            try:
                send_instructions_via_mqtt(list_instruksi, tujuan, rute_str)
            except Exception as e:
                print(f"[ERROR] MQTT: {e}")
            
            # NEW: Send to ESP32
            try:
                esp32_result = send_route_to_esp32(
                    device_id="ESP32_001",           # Or get from config
                    destination=tujuan,
                    instructions=list_instruksi,
                    route_path=path
                )
                
                if esp32_result['success']:
                    print(f"[✓] Route sent to ESP32: {esp32_result['message']}")
                else:
                    print(f"[✗] ESP32 error: {esp32_result.get('error', 'Unknown')}")
                    # Continue anyway - system can work with just MQTT
                    
            except Exception as e:
                print(f"[ERROR] ESP32: {e}")
            
            # Run robot simulation (existing)
            robot_thread = threading.Thread(
                target=run_robot_simulation, 
                args=(tujuan, nama, rute_str, list_instruksi)
            )
            robot_thread.start()
            
            return redirect(url_for('views.send_page'))
        
        else:
            hasil_rute = "Lokasi tidak valid!"
            status_rute = "ERROR"
            warna_status = "text-danger"
    
    return render_template(...)
"""

# ============= Testing Example =============

if __name__ == "__main__":
    print("ESP32 Integration Example")
    print("=" * 50)
    
    # Example 1: Send simple movement
    print("\n1. Sending simple movement command...")
    result = send_simple_movement("ESP32_TEST_001", "AREA_10", speed=0.5)
    print(f"   Result: {result}")
    
    # Example 2: Send full route
    print("\n2. Sending full route with instructions...")
    path = ['START', 'SIMPANG_UTAMA', 'J_ATAS', '10A']
    instructions = [
        "Mulai dari START",
        "Maju menuju SIMPANG_UTAMA",
        "Lurus melewati SIMPANG_UTAMA ke J_ATAS",
        "Belok Kanan di J_ATAS menuju 10A",
        "Sampai di Tujuan"
    ]
    result = send_route_to_esp32("ESP32_TEST_001", "10A", instructions, path)
    print(f"   Result: {result}")
    
    # Example 3: Stop command
    print("\n3. Sending stop command...")
    result = send_stop_command("ESP32_TEST_001")
    print(f"   Result: {result}")
    
    print("\n" + "=" * 50)
    print("Examples complete!")
