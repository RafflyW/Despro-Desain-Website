import json
import os
from .dashboard_home import get_current_wifi
from .status_book_callingcard import StatusRobot, StatusElektronika, StatusPaket, get_status_robot, get_status_elektronika, get_status_paket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ELECTRONICDB_FILE = os.path.join(BASE_DIR, '..', 'electronicsystem_database.json')
ROBOT_STATUS_FILE = os.path.join(BASE_DIR, '..', 'robot_status.json')
DELIVERY_HISTORY_FILE = os.path.join(BASE_DIR, '..', 'trekkinghistory_database.json')

# Default states
DEFAULT_ELECTRONICS = {
    "status_robot": int(StatusRobot.ROBOT_TIDAK_AKTIF),
    "wifi": int(StatusElektronika.WIFI_ERROR),
    "raspberry": int(StatusElektronika.ELEKTRONIKA_ERROR),
    "esp32": int(StatusElektronika.ELEKTRONIKA_ERROR),
    "camera": int(StatusElektronika.ELEKTRONIKA_ERROR),
    "total_pengiriman": 0
}

DEFAULT_ROBOT_STATUS = {
    "status_robot": int(StatusRobot.ROBOT_STANDBY_DISTATION),
    "status_paket": int(StatusPaket.MENUNGGU_PAKET),
    "tujuan_sekarang": "STANDBY",
    "pengirim_terakhir": "-",
    "rute_terakhir": "-",
    "instruksi_navigasi": []
}

def read_electronics_status():
    """Read hardware/electronics status from dedicated file."""
    try:
        with open(ELECTRONICDB_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_ELECTRONICS

def read_robot_status():
    """Read current robot delivery status from dedicated file."""
    try:
        with open(ROBOT_STATUS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_ROBOT_STATUS

def read_statuses():
    """Combine electronics and robot status for dashboard display."""
    electronics = read_electronics_status()
    robot = read_robot_status()
    
    context = {
        "status_robot": get_status_robot(robot.get('status_robot')),
        "status_pengiriman": get_status_paket(robot.get('status_paket')),
        "WiFi_Name": get_current_wifi(),
        "tujuan_display": robot.get('tujuan_sekarang') if robot.get('status_robot') == int(StatusRobot.ROBOT_MENGANTAR_PAKET) else "",
        "status_wifi": get_status_elektronika(electronics.get('wifi')),
        "hw_pi": get_status_elektronika(electronics.get('raspberry')),
        "hw_esp": get_status_elektronika(electronics.get('esp32')),
        "hw_cam": get_status_elektronika(electronics.get('camera')),
        "total_angka": electronics.get('total_pengiriman')
    }
    return context

def update_tujuan_db(tujuan_baru, nama_pengirim, rute_text, instructions_list, status_code, status_paket=None):
    """Update robot status and delivery information."""
    robot_data = read_robot_status()
    
    robot_data['tujuan_sekarang'] = tujuan_baru
    robot_data['pengirim_terakhir'] = nama_pengirim
    robot_data['rute_terakhir'] = rute_text
    robot_data['status_robot'] = int(status_code)
    if status_paket is not None:
        robot_data['status_paket'] = int(status_paket)
    robot_data['instruksi_navigasi'] = instructions_list
    
    write_robot_status(robot_data)

def write_robot_status(data):
    """Write robot status to dedicated file."""
    os.makedirs(os.path.dirname(ROBOT_STATUS_FILE), exist_ok=True)
    with open(ROBOT_STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_to_delivery_history(tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi, rute_pulang_text, instruksi_pulang, status_paket_text):
    """Append completed delivery to history log."""
    try:
        with open(DELIVERY_HISTORY_FILE, 'r') as f:
            history = json.load(f)
            if not isinstance(history, list):
                history = []
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    delivery_record = {
        "tujuan_sekarang": tujuan_awal,
        "pengirim_terakhir": nama_pengirim,
        "rute_pergi": rute_pergi_text,
        "instruksi_pergi": instruksi_pergi,
        "rute_pulang": rute_pulang_text,
        "instruksi_pulang": instruksi_pulang,
        "status_paket": status_paket_text
    }
    
    history.append(delivery_record)
    
    os.makedirs(os.path.dirname(DELIVERY_HISTORY_FILE), exist_ok=True)
    with open(DELIVERY_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)