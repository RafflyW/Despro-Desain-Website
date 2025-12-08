import paho.mqtt.client as mqtt
import time
import json
import logging

MQTT_BROKER = "127.0.0.1"        # broker di Pi sendiri
MQTT_PORT   = 1883
TOPIC_CMD   = "raspi/esp32/cmd"  # Pi -> ESP32
TOPIC_REPLY = "esp32/raspi/reply"  # ESP32 -> Pi
TOPIC_INSTRUCTIONS = "raspi/esp32/instruksi"  # Pi -> ESP32 (Navigation Instructions)

# Global MQTT client instance
_mqtt_client = None
_mqtt_connected = False

def setup_logger():
    """Setup logger untuk MQTT operations"""
    logger = logging.getLogger('mqtt_connection')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[MQTT] %(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

#Callback kalau Pi dapat balasan dari ESP32
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
    except UnicodeDecodeError:
        payload = str(msg.payload)
    logger.info(f"[ESP32 -> Pi] ({msg.topic}) : {payload}")

def on_connect(client, userdata, flags, rc):
    """Callback ketika terkoneksi ke broker MQTT"""
    global _mqtt_connected
    if rc == 0:
        _mqtt_connected = True
        logger.info("Terhubung ke broker MQTT")
        client.subscribe(TOPIC_REPLY)
    else:
        logger.error(f"Gagal terhubung, return code: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback ketika disconnect dari broker MQTT"""
    global _mqtt_connected
    _mqtt_connected = False
    logger.warning("Disconnect dari broker MQTT")

def initialize_mqtt_client():
    """Initialize MQTT client (run once on startup)"""
    global _mqtt_client, _mqtt_connected
    
    if _mqtt_client is not None:
        return _mqtt_client
    
    try:
        _mqtt_client = mqtt.Client(client_id="RaspberryPi_Dashboard")
        _mqtt_client.on_message = on_message
        _mqtt_client.on_connect = on_connect
        _mqtt_client.on_disconnect = on_disconnect
        
        logger.info("Menghubungkan ke broker MQTT...")
        _mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        _mqtt_client.loop_start()
        
        return _mqtt_client
    except Exception as e:
        logger.error(f"Error initializing MQTT: {e}")
        return None

def send_instructions_via_mqtt(instructions, tujuan, rute):
    """
    Mengirim instruksi navigasi ke ESP32 melalui MQTT
    
    Args:
        instructions (list): List instruksi navigasi dari route_instructions.py
        tujuan (str): Lokasi tujuan
        rute (str): Rute dalam format "START -> NODE1 -> NODE2"
    
    Returns:
        bool: True jika berhasil dikirim, False jika gagal
    """
    global _mqtt_client
    
    try:
        if _mqtt_client is None:
            initialize_mqtt_client()
        
        if not _mqtt_connected:
            logger.warning("MQTT belum terkoneksi, coba reconnect...")
            try:
                _mqtt_client.reconnect()
                time.sleep(1)
            except:
                logger.error("Gagal reconnect ke MQTT")
                return False
        
        # Format payload JSON untuk instruksi
        payload = {
            "tujuan": tujuan,
            "rute": rute,
            "instruksi": instructions,
            "timestamp": time.time()
        }
        
        json_payload = json.dumps(payload, ensure_ascii=False)
        
        result = _mqtt_client.publish(TOPIC_INSTRUCTIONS, json_payload, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"✓ Instruksi terkirim ke ESP32 - Tujuan: {tujuan}")
            return True
        else:
            logger.error(f"✗ Gagal mengirim instruksi - Return code: {result.rc}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending instructions: {e}")
        return False

def send_command_via_mqtt(command):
    """
    Mengirim command generic ke ESP32 melalui MQTT
    
    Args:
        command (str): Command string untuk dikirim
    
    Returns:
        bool: True jika berhasil dikirim, False jika gagal
    """
    global _mqtt_client
    
    try:
        if _mqtt_client is None:
            initialize_mqtt_client()
        
        if not _mqtt_connected:
            logger.warning("MQTT belum terkoneksi")
            return False
        
        result = _mqtt_client.publish(TOPIC_CMD, command, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"✓ Command terkirim: {command}")
            return True
        else:
            logger.error(f"✗ Gagal mengirim command")
            return False
            
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return False

def get_mqtt_status():
    """
    Mendapatkan status koneksi MQTT
    
    Returns:
        dict: Status MQTT connection
    """
    return {
        "connected": _mqtt_connected,
        "client": _mqtt_client is not None,
        "broker": MQTT_BROKER,
        "port": MQTT_PORT
    }

def cleanup_mqtt():
    """Cleanup MQTT connection (untuk graceful shutdown)"""
    global _mqtt_client, _mqtt_connected
    
    if _mqtt_client is not None:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()
        _mqtt_client = None
        _mqtt_connected = False
        logger.info("MQTT connection cleaned up")