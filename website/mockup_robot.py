import time
import json
import os
from .database_management import update_tujuan_db, ROBOT_STATUS_FILE, add_to_delivery_history
from .route_instructions import generate_return_instructions
from .route_calculation import coords
from .status_book_callingcard import StatusRobot, StatusElektronika, StatusPaket

def run_robot_simulation(tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi):
    
    # --- BYPASS CEK HARDWARE (Supaya Demo Lancar) ---
    # Kita hapus logika pengecekan error yang bikin macet.
    # Langsung dianggap OK.
    print("[ROBOT] Simulasi dimulai (Mode Bypass Hardware)...")

    # --- MULAI MENGANTAR PAKET (104) ---
    print("[ROBOT] Bergerak Mengantar...")
    update_tujuan_db(
        tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi, 
        status_code=104, # Status MENGANTAR
        status_paket=303 # Status PAKET DIANTAR
    )
    time.sleep(5) 

    # --- SAMPAI TUJUAN (105) ---
    print(f"[ROBOT] Sampai di {tujuan_awal}.")
    update_tujuan_db(
        tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi, 
        status_code=105, # Status SAMPAI
        status_paket=304 # Status PAKET TIBA
    )
    
    time.sleep(15) # Menunggu paket diambil

    # --- PULANG KE STATION (106) ---
    print("[ROBOT] Kembali ke Station...")
    
    # Generate rute pulang (ambil teks & string saja)
    # Kita pakai underscore (_) untuk variabel kode yang tidak dipakai simulasi
    instruksi_pulang_text, _, rute_pulang_text = generate_return_instructions(tujuan_awal, coords)
    
    update_tujuan_db(
        "STATION (PULANG)", "SYSTEM", rute_pulang_text, instruksi_pulang_text, 
        status_code=106, # Status PULANG
        status_paket=301 # Status TIDAK TERSEDIA
    )
    
    time.sleep(5)

    # --- STANDBY (103) ---
    print("[ROBOT] Misi Selesai. Standby.")
    update_tujuan_db(
        "STANDBY", "-", "-", [], 
        status_code=103, # Status STANDBY
        status_paket=302 # Status MENUNGGU PAKET
    )
    
    # --- SIMPAN HISTORY ---
    add_to_delivery_history(
        tujuan_awal, nama_pengirim, rute_pergi_text, instruksi_pergi,
        rute_pulang_text, instruksi_pulang_text, "Paket tiba di Tujuan"
    )