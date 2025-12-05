import json
import os
from .dashboard_home import get_current_wifi
from .status_book_callingcard import get_status_robot, get_status_elektronika, get_status_paket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '..', 'mock_database.json')

def read_statuses():
    try:
        with open(DB_FILE, 'r') as f:
            data_cache = json.load(f)
    except FileNotFoundError:
        # Fallback jika file belum dibuat
        data_cache = {"pengiriman": 0, "wifi": 0, "raspberry": 0, "esp32": 0, "camera": 0}

    # 2. Proses data menjadi status yang bisa dibaca
    context = {
        "status_robot": get_status_robot(data_cache.get('status_robot')),
        "status_pengiriman": get_status_paket(data_cache.get('status_paket')),
        "WiFi_Name": get_current_wifi(),
        "tujuan_display": data_cache.get('tujuan_sekarang') if data_cache.get('status_robot') == 104 else "",
        "status_wifi": get_status_elektronika(data_cache.get('wifi')),
        "hw_pi": get_status_elektronika(data_cache.get('raspberry')),
        "hw_esp": get_status_elektronika(data_cache.get('esp32')),
        "hw_cam": get_status_elektronika(data_cache.get('camera')),
        "total_angka": data_cache.get('total_pengiriman')
    }

    return context

def update_tujuan_db(tujuan_baru, nama_pengirim, rute_text, instructions_list):
    try:
        with open(DB_FILE, 'r') as f:
            data_tujuan = json.load(f)
    except FileNotFoundError:
        return {"pengiriman": 0, "tujuan_sekarang": "[Tujuan]", "wifi": 1, "raspberry": 1}
    
    data_tujuan['tujuan_sekarang'] = tujuan_baru
    data_tujuan['pengirim_terakhir'] = nama_pengirim
    data_tujuan['rute_terakhir'] = rute_text
    data_tujuan['pengiriman'] = 2 
    
    # Simpan instruksi agar bisa diambil Raspberry Pi
    data_tujuan['instruksi_navigasi'] = instructions_list 
    
    with open(DB_FILE, 'w') as f:
        json.dump(data_tujuan, f, indent=4)