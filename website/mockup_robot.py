import time
import json
import os
from .database_management import update_tujuan_db, ROBOT_STATUS_FILE, add_to_delivery_history
from .route_instructions import generate_return_instructions
from .route_calculation import coords
from .status_book_callingcard import StatusRobot, StatusElektronika, StatusPaket

# Path DB (Now using separate robot_status.json)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_robot_simulation(tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi):

    try:
        with open(ROBOT_STATUS_FILE, 'r') as f:
            cached_data = json.load(f)
        
        if cached_data.get('wifi', int(StatusElektronika.WIFI_ERROR)) == 0 or cached_data.get('raspberry', int(StatusElektronika.ELEKTRONIKA_ERROR)) == 0 or cached_data.get('esp32', int(StatusElektronika.ELEKTRONIKA_ERROR)) == 0:
            print("[ROBOT] GAGAL: Komponen Hardware Bermasalah!")

            update_tujuan_db(
                tujuan_awal, nama_pengirim, "BATAL - ERROR HARDWARE", [], 
                status_code=StatusRobot.ROBOT_MENGALAMI_KENDALA
            )
            return
            
    except Exception as e:
        print(f"[ROBOT] Error reading DB: {e}")
        return

    # --- MULAI MENGANTAR PAKET (104) ---
    print("[ROBOT] Hardware OK. Bergerak...")
    update_tujuan_db(
        tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi, 
        status_code=StatusRobot.ROBOT_MENGANTAR_PAKET,
        status_paket=StatusPaket.PAKET_DIANTAR
    )
    time.sleep(5) 

    # --- SAMPAI TUJUAN (105) ---
    print(f"[ROBOT] Sampai di {tujuan_awal}.")
    update_tujuan_db(
        tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi, 
        status_code=StatusRobot.ROBOT_TELAH_MENGANTAR_PAKET,
        status_paket=StatusPaket.PAKET_TIBA
    )
    
    time.sleep(15) # Menunggu paket diambil

    # --- PULANG KE STATION (106) ---
    print("[ROBOT] Kembali ke Station...")
    instruksi_pulang, rute_pulang_text = generate_return_instructions(tujuan_awal, coords)
    
    update_tujuan_db(
        "STATION (PULANG)", "SYSTEM", rute_pulang_text, instruksi_pulang, 
        status_code=StatusRobot.ROBOT_MENUJU_STATION,
        status_paket=StatusPaket.ROBOT_TIDAK_TERSEDIA
    )
    
    time.sleep(5)

    # --- STANDBY (103) ---
    print("[ROBOT] Misi Selesai. Standby.")
    update_tujuan_db(
        "STANDBY", "-", "-", [], 
        status_code=StatusRobot.ROBOT_STANDBY_DISTATION,
        status_paket=StatusPaket.MENUNGGU_PAKET
    )
    
    # --- ADD TO DELIVERY HISTORY ---
    add_to_delivery_history(
        tujuan_awal, 
        nama_pengirim, 
        rute_pergi_text, 
        instruksi_pergi,
        rute_pulang_text,
        instruksi_pulang,
        "Paket tiba di Tujuan"
    )